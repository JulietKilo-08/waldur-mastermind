from functools import reduce

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum


class FieldsContainerMeta(type):
    """Initiates quota fields names.

    Quotas fields should be located in class with FieldsContainerMeta metaclass.
    Example:
        example_quota = QuotaField()  # this quota field will have name 'example_quota'
    """

    def __new__(self, name, bases, attrs):
        for key in attrs:
            if isinstance(attrs[key], QuotaField):
                attrs[key].name = key
        return type.__new__(self, name, bases, attrs)


class QuotaField:
    """Base quota field.

    Links quota to its scope right after its creation.
    Allows to define:
     - default_limit
     - is_backend - is quota represents backend limitation. It is impossible to modify backend quotas.
     - creation_condition - function that receive quota scope and return True if quota should be created
                            for given scope. Quota will be created automatically if creation_condition is None.

    Default limit and usage can be defined as callable function.
    Example:
        quota_name = QuotaField(default_limit=lambda scope: scope.attr)
    """

    def __init__(
        self,
        default_limit=-1,
        is_backend=False,
        creation_condition=None,
    ):
        self.default_limit = default_limit
        self.is_backend = is_backend
        self.creation_condition = creation_condition

    def is_connected_to_scope(self, scope):
        if self.creation_condition is None:
            return True
        return self.creation_condition(scope)

    def __str__(self):
        return self.name

    def recalculate(self, scope):
        if not self.is_connected_to_scope(scope):
            return
        self.recalculate_usage(scope)

    def recalculate_usage(self, scope):
        pass


class CounterQuotaField(QuotaField):
    """Provides limitation on target models instances count.

    Automatically increases/decreases usage on target instances creation/deletion.

    By default usage is increased by 1. You may tweak this delta by defining get_delta function,
    which accepts target instance and returns number.

    Example:
        # This quota will increase/decrease own values on any resource creation/deletion
        nc_resource_count = CounterQuotaField(
            target_models=lambda: Resource.get_all_models(),  # list or function that return list of target models
            path_to_scope='project',  # path from target model to scope
        )

    It is possible to define trickier calculation by passing `get_current_usage` function as parameter.
    Function should accept two parameters:
        - models - list of target models
        - scope - quota scope
    And return count of current usage.
    """

    def __init__(
        self,
        target_models,
        path_to_scope,
        get_current_usage=None,
        get_delta=None,
        **kwargs
    ):
        self._raw_target_models = target_models
        self._raw_get_current_usage = get_current_usage
        self._raw_get_delta = get_delta
        self.path_to_scope = path_to_scope
        super().__init__(**kwargs)

    def get_delta(self, target_instance):
        if not self._raw_get_delta:
            return 1
        return self._raw_get_delta(target_instance)

    def get_current_usage(self, models, scope):
        if self._raw_get_current_usage is not None:
            return self._raw_get_current_usage(models, scope)
        else:
            filter_path_to_scope = self.path_to_scope.replace('.', '__')
            return sum(
                [
                    m.objects.filter(**{filter_path_to_scope: scope}).count()
                    for m in models
                ]
            )

    @property
    def target_models(self):
        if not hasattr(self, '_target_models'):
            self._target_models = (
                self._raw_target_models()
                if callable(self._raw_target_models)
                else self._raw_target_models
            )
        return self._target_models

    def recalculate_usage(self, scope):
        current_usage = self.get_current_usage(self.target_models, scope)
        scope.set_quota_usage(self.name, current_usage)

    def add_usage(self, target_instance, delta):
        try:
            scope = self._get_scope(target_instance)
        except ObjectDoesNotExist:
            # ignore as scope has been deleted
            return
        delta *= self.get_delta(target_instance)
        if self.is_connected_to_scope(scope):
            scope.add_quota_usage(self.name, delta)

    def _get_scope(self, target_instance):
        return reduce(getattr, self.path_to_scope.split('.'), target_instance)


class TotalQuotaField(CounterQuotaField):
    """
    This field aggregates sum of value for the same field of children objects.
    For example, it allows to compute total volume size for the project.

     class Quotas(quotas_models.QuotaModelMixin.Quotas):
        nc_volume_size = quotas_fields.TotalQuotaField(
            target_models=lambda: Volume.get_all_models(),
            path_to_scope='project',
            target_field='size',
        )

    """

    def __init__(self, target_models, path_to_scope, target_field):
        self.target_field = target_field
        super().__init__(target_models, path_to_scope)

    def get_current_usage(self, models, scope):
        total_usage = 0
        filter_path_to_scope = self.path_to_scope.replace('.', '__')
        query = {filter_path_to_scope: scope}
        for model in models:
            resources = model.objects.filter(**query)
            subtotal = resources.values(self.target_field).aggregate(
                total_usage=Sum(self.target_field)
            )['total_usage']
            if subtotal:
                total_usage += subtotal
        return total_usage

    def get_delta(self, target_instance):
        return getattr(target_instance, self.target_field)


class UsageAggregatorQuotaField(QuotaField):
    """Aggregates sum of quota scope children with the same name.

    Example:
        # This quota will store sum of all customer projects resources
        nc_resource_count = quotas_fields.UsageAggregatorQuotaField(
            get_children=lambda customer: customer.projects.all(),
        )
    """

    def __init__(self, get_children, child_quota_name=None, **kwargs):
        self.get_children = get_children
        self._child_quota_name = child_quota_name
        super().__init__(**kwargs)

    def get_child_quota_name(self):
        return (
            self._child_quota_name if self._child_quota_name is not None else self.name
        )

    def recalculate_usage(self, scope):
        children = self.get_children(scope)
        current_usage = 0
        for child in children:
            current_usage += child.get_quota_usage(self.get_child_quota_name())
        scope.set_quota_usage(self.name, current_usage)
