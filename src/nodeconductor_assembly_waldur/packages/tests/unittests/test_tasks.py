from django.test import TestCase
from mock import MagicMock

from nodeconductor.core import models as core_models

from .. import factories
from ... import tasks


class OpenStackPackageErrorTaskTest(TestCase):

    def setUp(self):
        self.openstack_package = factories.OpenStackPackageFactory()
        self.tenant = self.openstack_package.tenant
        self.service_settings = self.openstack_package.service_settings
        self.task = tasks.OpenStackPackageErrorTask()
        self.task.result = MagicMock()
        self.task.result.result = 'Test error'

    def test_task_marks_tenant_and_settings_as_erred_if_it_was_not_created(self):
        self.tenant.state = core_models.StateMixin.States.CREATION_SCHEDULED
        self.tenant.save()
        self.service_settings.state = core_models.StateMixin.States.CREATION_SCHEDULED
        self.service_settings.save()

        self.task.execute(self.openstack_package)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.state, core_models.StateMixin.States.ERRED)
        self.service_settings.refresh_from_db()
        self.assertEqual(self.service_settings.state, core_models.StateMixin.States.ERRED)

    def test_task_does_not_mark_tenant_as_erred_if_it_was_created(self):
        self.tenant.state = core_models.StateMixin.States.OK
        self.tenant.save()
        self.service_settings.state = core_models.StateMixin.States.CREATION_SCHEDULED
        self.service_settings.save()

        self.task.execute(self.openstack_package)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.state, core_models.StateMixin.States.OK)
        self.service_settings.refresh_from_db()
        self.assertEqual(self.service_settings.state, core_models.StateMixin.States.ERRED)
