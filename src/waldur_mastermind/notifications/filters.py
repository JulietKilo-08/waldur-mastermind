import django_filters

from waldur_core.core import filters as core_filters


class NotificationFilterSet(django_filters.FilterSet):
    subject = django_filters.CharFilter(lookup_expr='icontains')

    o = core_filters.ExtendedOrderingFilter(
        fields=(
            ('created', 'created'),
            ('subject', 'subject'),
            (('author__first_name', 'author__last_name'), 'author_full_name'),
        )
    )
