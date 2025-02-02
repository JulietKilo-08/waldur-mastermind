from django.apps import AppConfig
from django.db.models import signals


class MarketplaceSlurmConfig(AppConfig):
    name = 'waldur_mastermind.marketplace_slurm'
    verbose_name = 'Marketplace SLURM'

    def ready(self):
        from waldur_mastermind.marketplace import handlers as marketplace_handlers
        from waldur_mastermind.marketplace import models as marketplace_models
        from waldur_mastermind.marketplace.plugins import Component, manager
        from waldur_mastermind.marketplace_slurm import PLUGIN_NAME
        from waldur_slurm import models as slurm_models
        from waldur_slurm import signals as slurm_signals
        from waldur_slurm.apps import SlurmConfig

        from . import handlers, processor
        from . import registrators as slurm_registrators

        slurm_registrators.SlurmRegistrator.connect()

        signals.post_save.connect(
            handlers.update_component_quota,
            sender=slurm_models.Allocation,
            dispatch_uid='waldur_mastermind.marketplace_slurm.update_component_quota',
        )

        marketplace_handlers.connect_resource_handlers(slurm_models.Allocation)
        marketplace_handlers.connect_resource_metadata_handlers(slurm_models.Allocation)

        USAGE = marketplace_models.OfferingComponent.BillingTypes.USAGE
        manager.register(
            PLUGIN_NAME,
            create_resource_processor=processor.CreateAllocationProcessor,
            delete_resource_processor=processor.DeleteAllocationProcessor,
            components=(
                Component(
                    type='cpu',
                    name='CPU',
                    measured_unit='hours',
                    billing_type=USAGE,
                ),
                Component(
                    type='gpu',
                    name='GPU',
                    measured_unit='hours',
                    billing_type=USAGE,
                ),
                Component(
                    type='ram',
                    name='RAM',
                    measured_unit='GB-hours',
                    billing_type=USAGE,
                ),
            ),
            service_type=SlurmConfig.service_name,
        )

        slurm_signals.slurm_association_created.connect(
            handlers.create_offering_user_for_slurm_user,
            sender=slurm_models.Allocation,
            dispatch_uid='waldur_mastermind.marketplace_slurm.create_offering_user_for_slurm_user',
        )

        slurm_signals.slurm_association_deleted.connect(
            handlers.drop_offering_user_for_slurm_user,
            sender=slurm_models.Allocation,
            dispatch_uid='waldur_mastermind.marketplace_slurm.drop_offering_user_for_slurm_user',
        )
