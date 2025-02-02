import copy
import datetime
import logging
import re

from dateutil.parser import parse as parse_datetime
from django.utils import timezone

from waldur_mastermind.booking import models as models
from waldur_mastermind.marketplace import models as marketplace_models

from . import PLUGIN_NAME

try:
    # using Python 3.10+
    from collections.abc import Sequence
except ImportError:
    # using Python 3.10-
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class TimePeriod:
    def __init__(
        self,
        start,
        end,
        period_id=None,
        location=None,
        attendees=None,
        order_item=None,
        time_zone=None,
        name=None,
    ):
        if not isinstance(start, datetime.datetime):
            start = parse_datetime(start)

        if not start.tzname() and time_zone:
            start = start.replace(tzinfo=time_zone)

        if not isinstance(end, datetime.datetime):
            end = parse_datetime(end)

        if not end.tzname() and time_zone:
            end = end.replace(tzinfo=time_zone)

        self.start = start
        self.end = end

        reg_exp = re.compile(r'[^a-z0-9]')
        self.id = period_id and re.sub(reg_exp, '', period_id)
        self.location = location
        self.attendees = attendees or []
        self.order_item = order_item
        self.name = name

        if not isinstance(self.attendees, Sequence):
            self.attendees = [self.attendees]


def is_interval_in_schedules(interval, schedules):
    for s in schedules:
        if interval.start >= s.start:
            if interval.end <= s.end:
                return True

    return False


def get_offering_bookings(offering):
    """
    OK means that booking request has been accepted.
    CREATING means that booking request has been made but not yet confirmed.
    If it is rejected, the time slot could be freed up.
    But it is more end-user friendly if choices that you see are
    always available (if some time slots at risk, better to conceal them).
    """
    States = marketplace_models.Resource.States
    resources = marketplace_models.Resource.objects.filter(
        offering=offering, state__in=(States.OK, States.CREATING)
    ).order_by('created')
    bookings = []

    if offering.latitude and offering.longitude:
        location = '{{{}}}, {{{}}}'.format(
            offering.latitude,
            offering.longitude,
        )
    else:
        location = None

    for resource in resources:
        order_item = (
            resources.first()
            .orderitem_set.filter(type=marketplace_models.OrderItem.Types.CREATE)
            .first()
        )
        attendees = []

        if order_item:
            email = order_item.order.created_by.email or None
            full_name = order_item.order.created_by.full_name or None
            if email:
                attendees = [{'displayName': full_name, 'email': email}]

        schedule = models.BookingSlot.objects.filter(resource=resource).order_by(
            'start'
        )

        if schedule:
            for period in schedule:
                if period:
                    bookings.append(
                        TimePeriod(
                            period.start,
                            period.end,
                            period.backend_id,
                            attendees=attendees,
                            location=location,
                            order_item=order_item,
                            name=period.resource.name,
                        )
                    )

    return bookings


def get_offering_bookings_and_busy_slots(offering):
    slots = get_offering_bookings(offering)

    for slot in models.BusySlot.objects.filter(offering=offering):
        slots.append(
            TimePeriod(
                slot.start,
                slot.end,
                slot.backend_id,
            )
        )

    return slots


def get_other_offering_booking_requests(order_item):
    States = marketplace_models.OrderItem.States
    schedules = (
        marketplace_models.OrderItem.objects.filter(
            offering=order_item.offering,
            state__in=(States.PENDING, States.EXECUTING, States.DONE),
        )
        .exclude(id=order_item.id)
        .values_list('attributes__schedules', flat=True)
    )
    return [
        TimePeriod(period['start'], period['end'], period.get('id'))
        for schedule in schedules
        if schedule
        for period in schedule
        if period
    ]


def get_info_about_upcoming_bookings():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    upcoming_bookings = marketplace_models.Resource.objects.filter(
        offering__type=PLUGIN_NAME,
        state=marketplace_models.Resource.States.OK,
        attributes__schedules__0__start__icontains='%s-%02d-%02dT'
        % (tomorrow.year, tomorrow.month, tomorrow.day),
    )

    result = []

    for resource in upcoming_bookings:
        try:
            order_item = marketplace_models.OrderItem.objects.get(
                resource=resource, type=marketplace_models.OrderItem.Types.CREATE
            )
            user = order_item.order.created_by
        except marketplace_models.OrderItem.DoesNotExist:
            logger.warning(
                'Skipping notification because '
                'marketplace resource hasn\'t got a order item. '
                'Resource ID: %s',
                resource.id,
            )
        except marketplace_models.OrderItem.MultipleObjectsReturned:
            logger.warning(
                'Skipping notification because '
                'marketplace resource has got few order items. '
                'Resource ID: %s',
                resource.id,
            )
        else:
            rows = list(
                filter(lambda x: x['user'] == resource.project.customer, result)
            )
            if rows:
                rows[0]['resources'].append(resource)
            else:
                result.append(
                    {
                        'user': user,
                        'resources': [resource],
                    }
                )

    return result


def change_attributes_for_view(attrs):
    # We use copy of attrs to do not change offering.attributes
    attributes = copy.deepcopy(attrs)
    schedules = attributes.get('schedules', [])
    attributes['schedules'] = [
        schedule
        for schedule in schedules
        if parse_datetime(schedule['end']) > timezone.now()
    ]
    for schedule in attributes['schedules']:
        if parse_datetime(schedule['start']) < timezone.now():
            schedule['start'] = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    return attributes


# def sort_attributes_schedules(attributes):
#     schedules = attributes.get('schedules')
#     if not schedules:
#         return
#
#     for s in schedules:
#         s['start'] = parse_datetime(s['start']).astimezone(timezone.utc).isoformat()
#         s['end'] = parse_datetime(s['end']).astimezone(timezone.utc).isoformat()
#
#     attributes['schedules'] = sorted(schedules, key=lambda schedule: schedule['start'])
