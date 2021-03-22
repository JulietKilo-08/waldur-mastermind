from django.utils.translation import ugettext_lazy as _

from waldur_mastermind.marketplace import processors, signals
from waldur_mastermind.marketplace.processors import get_order_item_post_data
from waldur_mastermind.marketplace_openstack import views
from waldur_openstack.openstack import models as openstack_models
from waldur_openstack.openstack import views as openstack_views
from waldur_openstack.openstack_tenant import views as tenant_views

from . import utils


class TenantCreateProcessor(processors.CreateResourceProcessor):
    def get_serializer_class(self):
        return views.MarketplaceTenantViewSet.serializer_class

    def get_viewset(self):
        return views.MarketplaceTenantViewSet

    def get_post_data(self):
        order_item = self.order_item

        fields = (
            'name',
            'description',
            'user_username',
            'user_password',
            'subnet_cidr',
            'skip_connection_extnet',
            'availability_zone',
        )

        payload = get_order_item_post_data(order_item, fields)
        quotas = utils.map_limits_to_quotas(order_item.limits, order_item.offering)

        return dict(quotas=quotas, **payload)

    def get_scope_from_response(self, response):
        return openstack_models.Tenant.objects.get(uuid=response.data['uuid'])


class TenantUpdateProcessor(processors.UpdateResourceProcessor):
    def update_limits_process(self, user):
        scope = self.order_item.resource.scope
        if not scope or not isinstance(scope, openstack_models.Tenant):
            signals.resource_limit_update_failed.send(
                sender=self.order_item.resource.__class__,
                order_item=self.order_item,
                message=_('Limit updating is available only for tenants.'),
            )
            return

        utils.update_limits(self.order_item)


class TenantDeleteProcessor(processors.DeleteResourceProcessor):
    viewset = openstack_views.TenantViewSet


class InstanceCreateProcessor(processors.BaseCreateResourceProcessor):
    viewset = tenant_views.InstanceViewSet

    fields = (
        'name',
        'description',
        'flavor',
        'image',
        'security_groups',
        'internal_ips_set',
        'floating_ips',
        'system_volume_size',
        'system_volume_type',
        'data_volume_size',
        'data_volume_type',
        'volumes',
        'ssh_public_key',
        'user_data',
        'availability_zone',
    )


class InstanceDeleteProcessor(processors.DeleteResourceProcessor):
    viewset = tenant_views.InstanceViewSet


class VolumeCreateProcessor(processors.BaseCreateResourceProcessor):
    viewset = tenant_views.VolumeViewSet

    fields = (
        'name',
        'description',
        'image',
        'size',
        'availability_zone',
        'type',
    )


class VolumeDeleteProcessor(processors.DeleteResourceProcessor):
    viewset = tenant_views.VolumeViewSet
