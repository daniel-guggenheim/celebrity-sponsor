from aiaUsers.models import UserDetails, BaseUserDetails
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone


class BaseUserDetailsModelTest(TestCase):
    def create_normal_user(self):
        return User.objects.create(username='testUser', password='12345678')

    def create_company_user_details(self, type_u=BaseUserDetails.COMPANY_VAL, creation_d=timezone.now()):
        new_user = self.create_normal_user()
        return UserDetails.objects.create(linked_user=new_user, user_type=type_u, creation_date=creation_d)

    def test_normal_user_creation(self):
        new_user = self.create_normal_user()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, 'testUser')

    def test_user_details_has_good_attribute_at_creation(self):
        now = timezone.now()
        type_u = BaseUserDetails.COMPANY_VAL
        user_details = self.create_company_user_details(type_u=type_u, creation_d=now)
        self.assertEqual(user_details.creation_date, now)
        self.assertEqual(user_details.user_type, type_u)

    def test_is_company_user_self_function_for_user_details(self):
        user_details = self.create_company_user_details()
        self.assertEqual(user_details.is_company_user_self(), True)
