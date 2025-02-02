from django.apps import AppConfig
from django.db.models import signals


class BookingConfig(AppConfig):
    name = 'waldur_mastermind.booking'
    verbose_name = 'Booking system'

    def ready(self):
        from waldur_mastermind.marketplace import models as marketplace_models
        from waldur_mastermind.marketplace.plugins import manager

        from . import PLUGIN_NAME, handlers, processors
        from . import registrators as booking_registrators
        from . import utils

        manager.register(
            offering_type=PLUGIN_NAME,
            create_resource_processor=processors.BookingCreateProcessor,
            delete_resource_processor=processors.BookingDeleteProcessor,
            change_attributes_for_view=utils.change_attributes_for_view,
            enable_usage_notifications=True,
        )

        booking_registrators.BookingRegistrator.connect()

        signals.post_save.connect(
            handlers.update_google_calendar_name_if_offering_name_has_been_changed,
            sender=marketplace_models.Offering,
            dispatch_uid='waldur_mastermind.booking.handlers.update_google_calendar_name',
        )
