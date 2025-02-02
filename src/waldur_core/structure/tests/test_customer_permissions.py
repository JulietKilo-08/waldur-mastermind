import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, test
from rest_framework.reverse import reverse

from waldur_core.permissions.enums import PermissionEnum
from waldur_core.permissions.fixtures import CustomerRole, ProjectRole
from waldur_core.permissions.tasks import check_expired_permissions
from waldur_core.permissions.utils import get_permissions
from waldur_core.structure.tests import factories
from waldur_core.structure.tests.utils import (
    client_add_user,
    client_delete_user,
    client_list_users,
    client_update_user,
)

User = get_user_model()


class CustomerPermissionListTest(test.APITransactionTestCase):
    def test_user_cannot_list_roles_of_customer_he_is_not_affiliated(self):
        response = client_list_users(
            self.client, factories.UserFactory(), factories.CustomerFactory()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_owner_can_list_roles_of_his_customer(self):
        owner = factories.UserFactory()
        customer = factories.CustomerFactory()
        customer.add_user(owner, CustomerRole.OWNER)
        response = client_list_users(self.client, owner, customer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_admin_can_list_roles_of_his_customer(self):
        admin = factories.UserFactory()
        customer = factories.CustomerFactory()
        project = factories.ProjectFactory(customer=customer)
        project.add_user(admin, ProjectRole.ADMIN)
        response = client_list_users(self.client, admin, customer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_list_roles_of_any_customer(self):
        response = client_list_users(
            self.client,
            factories.UserFactory(is_staff=True),
            factories.CustomerFactory(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_owner_cannot_list_roles_of_another_customer(self):
        owner = factories.UserFactory()
        customer = factories.CustomerFactory()
        customer.add_user(owner, CustomerRole.OWNER)
        response = client_list_users(self.client, owner, factories.CustomerFactory())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_admin_cannot_list_roles_of_another_customer(self):
        admin = factories.UserFactory()
        customer = factories.CustomerFactory()
        project = factories.ProjectFactory(customer=customer)
        project.add_user(admin, ProjectRole.ADMIN)
        response = client_list_users(self.client, admin, factories.CustomerFactory())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CustomerPermissionGrantTest(test.APITransactionTestCase):
    def setUp(self):
        super().setUp()
        self.owner = factories.UserFactory()
        self.customer = factories.CustomerFactory()
        self.customer.add_user(self.owner, CustomerRole.OWNER)

    def test_user_which_granted_permission_is_stored(self):
        staff_user = factories.UserFactory(is_staff=True)

        user = factories.UserFactory()
        customer = factories.CustomerFactory()

        response = client_add_user(
            self.client, staff_user, user, customer, CustomerRole.OWNER
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        permission = get_permissions(customer, user).get()
        self.assertEqual(permission.created_by, staff_user)

    def test_customer_owner_can_grant_new_role_within_his_customer(self):
        CustomerRole.OWNER.add_permission(PermissionEnum.CREATE_CUSTOMER_PERMISSION)

        response = client_add_user(
            self.client,
            self.owner,
            factories.UserFactory(),
            self.customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_cannot_grant_existing_role_within_his_customer(self):
        response = client_add_user(
            self.client,
            factories.UserFactory(is_staff=True),
            self.owner,
            self.customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_owner_cannot_grant_role_within_another_customer(self):
        response = client_add_user(
            self.client,
            self.owner,
            factories.UserFactory(),
            factories.CustomerFactory(),
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_owner_can_not_grant_new_role_within_his_customer(
        self,
    ):
        response = client_add_user(
            self.client,
            self.owner,
            factories.UserFactory(),
            self.customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_admin_cannot_grant_role_within_his_customer(self):
        CustomerRole.OWNER.add_permission(PermissionEnum.CREATE_CUSTOMER_PERMISSION)
        admin = factories.UserFactory()
        customer = factories.CustomerFactory()
        project = factories.ProjectFactory(customer=customer)
        project.add_user(admin, ProjectRole.ADMIN)

        response = client_add_user(
            self.client,
            admin,
            factories.UserFactory(),
            customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CustomerPermissionRevokeTest(test.APITransactionTestCase):
    def setUp(self):
        super().setUp()
        self.owner = factories.UserFactory()
        self.customer = factories.CustomerFactory()
        self.customer.add_user(self.owner, CustomerRole.OWNER)

    def test_customer_owner_can_revoke_role_within_his_customer(self):
        CustomerRole.OWNER.add_permission(PermissionEnum.DELETE_CUSTOMER_PERMISSION)

        response = client_delete_user(
            self.client,
            self.owner,
            self.owner,
            self.customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_owner_cannot_revoke_role_within_another_customer(self):
        another_owner = factories.UserFactory()
        another_customer = factories.CustomerFactory()
        another_customer.add_user(another_owner, CustomerRole.OWNER)

        response = client_delete_user(
            self.client,
            self.owner,
            another_owner,
            another_customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_owner_can_not_revoke_role_within_his_customer(
        self,
    ):
        response = client_delete_user(
            self.client,
            self.owner,
            self.owner,
            self.customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_admin_cannot_revoke_role_within_his_customer(self):
        CustomerRole.OWNER.add_permission(PermissionEnum.DELETE_CUSTOMER_PERMISSION)

        admin = factories.UserFactory()
        project = factories.ProjectFactory(customer=self.customer)
        project.add_user(admin, ProjectRole.ADMIN)

        response = client_delete_user(
            self.client,
            admin,
            self.owner,
            self.customer,
            CustomerRole.OWNER,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_revoke_role_within_any_customer(self):
        response = client_delete_user(
            self.client,
            factories.UserFactory(is_staff=True),
            self.owner,
            self.customer,
            CustomerRole.OWNER,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CustomerPermissionFilterTest(test.APITransactionTestCase):
    def setUp(self):
        staff_user = factories.UserFactory(is_staff=True)
        self.client.force_authenticate(user=staff_user)

        self.users = {
            'first': factories.UserFactory(),
            'second': factories.UserFactory(),
        }

        self.customers = {
            'first': factories.CustomerFactory(),
            'second': factories.CustomerFactory(),
        }

        for customer in self.customers:
            self.customers[customer].add_user(self.users['first'], CustomerRole.OWNER)
            self.customers[customer].add_user(self.users['second'], CustomerRole.OWNER)

    def test_staff_user_can_filter_roles_within_customer_by_customer_uuid(self):
        response = self.client.get(reverse('customer_permission-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for customer in self.customers:
            response = self.client.get(
                reverse('customer_permission-list'),
                data={'customer': self.customers[customer].uuid.hex},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            customer_url = self._get_customer_url(self.customers[customer])

            for permission in response.data:
                self.assertEqual(customer_url, permission['customer'])

    def test_staff_user_can_filter_roles_within_customer_by_username(self):
        response = self.client.get(reverse('customer_permission-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in self.users:
            self._ensure_matching_entries_in('username', self.users[user].username)
            self._ensure_non_matching_entries_not_in(
                'username', self.users[user].username
            )

    def test_staff_user_can_filter_roles_within_customer_by_native_name(self):
        response = self.client.get(reverse('customer_permission-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in self.users:
            self._ensure_matching_entries_in(
                'native_name', self.users[user].native_name
            )
            self._ensure_non_matching_entries_not_in(
                'native_name', self.users[user].native_name
            )

    def test_staff_user_can_filter_roles_within_customer_by_full_name(self):
        response = self.client.get(reverse('customer_permission-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in self.users:
            self._ensure_matching_entries_in('full_name', self.users[user].full_name)
            self._ensure_non_matching_entries_not_in(
                'full_name', self.users[user].full_name
            )

    def test_staff_user_can_filter_roles_within_customer_by_role_name(self):
        response = self.client.get(reverse('customer_permission-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse('customer_permission-list'), data={'role': 'owner'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for permission in response.data:
            self.assertEqual('owner', permission['role'])

    def test_staff_user_can_see_required_fields_in_filtration_response(self):
        response = self.client.get(reverse('customer_permission-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for customer in self.customers:
            response = self.client.get(
                reverse('customer_permission-list'),
                data={'customer': self.customers[customer].uuid.hex},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            required_fields = (
                'url',
                'user_native_name',
                'user_full_name',
                'user_username',
            )

            for permission in response.data:
                for field in required_fields:
                    self.assertIn(field, permission)

    # Helper methods
    def _ensure_matching_entries_in(self, field, value):
        response = self.client.get(
            reverse('customer_permission-list'), data={field: value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for permission in response.data:
            self.assertEqual(value, permission['user_' + field])

    def _ensure_non_matching_entries_not_in(self, field, value):
        user = factories.UserFactory()

        customer = factories.CustomerFactory()
        customer.add_user(user, CustomerRole.OWNER)

        response = self.client.get(
            reverse('customer_permission-list'), data={field: getattr(user, field)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for permission in response.data:
            self.assertNotEqual(value, permission['user_' + field])

    def _get_customer_url(self, customer):
        return 'http://testserver' + reverse(
            'customer-detail', kwargs={'uuid': customer.uuid.hex}
        )


class CustomerPermissionExpirationTest(test.APITransactionTestCase):
    def setUp(self):
        super().setUp()
        self.user = factories.UserFactory()
        self.customer = factories.CustomerFactory()
        self.customer.add_user(self.user, CustomerRole.OWNER)

    def update_expiration_time(self, current_user, target_user, expiration_time):
        return client_update_user(
            self.client,
            current_user,
            target_user,
            self.customer,
            CustomerRole.OWNER,
            expiration_time,
        )

    def test_user_can_not_update_permission_expiration_time_for_himself(self):
        expiration_time = timezone.now() + datetime.timedelta(days=100)
        response = self.update_expiration_time(self.user, self.user, expiration_time)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_permission_expiration_time_for_any_user(self):
        staff_user = factories.UserFactory(is_staff=True)

        expiration_time = timezone.now() + datetime.timedelta(days=100)
        response = self.update_expiration_time(staff_user, self.user, expiration_time)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['expiration_time'], expiration_time, response.data
        )

    def test_owner_can_update_permission_expiration_time_for_other_owner_in_same_customer(
        self,
    ):
        CustomerRole.OWNER.add_permission(PermissionEnum.UPDATE_CUSTOMER_PERMISSION)
        owner = factories.UserFactory()
        self.customer.add_user(owner, CustomerRole.OWNER)

        expiration_time = timezone.now() + datetime.timedelta(days=100)
        response = self.update_expiration_time(owner, self.user, expiration_time)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(
            response.data['expiration_time'], expiration_time, response.data
        )

    def test_owner_can_not_update_permission_expiration_time_for_other_owner(
        self,
    ):
        owner = factories.UserFactory()
        self.customer.add_user(owner, CustomerRole.OWNER)

        expiration_time = timezone.now() + datetime.timedelta(days=100)
        response = self.update_expiration_time(owner, self.user, expiration_time)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_not_set_permission_expiration_time_lower_than_current(self):
        staff_user = factories.UserFactory(is_staff=True)
        expiration_time = timezone.now() - datetime.timedelta(days=100)

        response = self.update_expiration_time(staff_user, self.user, expiration_time)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_grant_permissions_with_greater_expiration_time(self):
        customer = factories.CustomerFactory()
        current_user = factories.UserFactory()
        target_user = factories.UserFactory()
        expiration_time = timezone.now() + datetime.timedelta(days=100)
        customer.add_user(
            current_user, CustomerRole.OWNER, expiration_time=expiration_time
        )

        response = client_add_user(
            self.client,
            current_user,
            target_user,
            customer,
            CustomerRole.OWNER,
            expiration_time=expiration_time + datetime.timedelta(days=1),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_set_expiration_time_when_role_is_created(self):
        customer = factories.CustomerFactory()
        staff_user = factories.UserFactory(is_staff=True)
        target_user = factories.UserFactory()
        expiration_time = timezone.now() + datetime.timedelta(days=100)

        response = client_add_user(
            self.client,
            staff_user,
            target_user,
            customer,
            CustomerRole.OWNER,
            expiration_time,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['expiration_time'], expiration_time, response.data
        )

    def test_task_revokes_expired_permissions(self):
        customer = factories.CustomerFactory()
        expired_user = factories.UserFactory()
        non_expired_user = factories.UserFactory()

        customer.add_user(
            expired_user,
            CustomerRole.OWNER,
            expiration_time=timezone.now() - datetime.timedelta(days=100),
        )
        customer.add_user(
            non_expired_user,
            CustomerRole.OWNER,
            expiration_time=timezone.now() + datetime.timedelta(days=100),
        )

        check_expired_permissions()

        self.assertFalse(customer.has_user(expired_user, CustomerRole.OWNER))
        self.assertTrue(customer.has_user(non_expired_user, CustomerRole.OWNER))
