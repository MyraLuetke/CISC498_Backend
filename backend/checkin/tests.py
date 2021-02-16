from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from .models import User, Customer
from .views import CustomerCreate


class UserModelTests(TestCase):
    def setUp(self):
        User.objects.create(email="one@example.com", password="test")
        User.objects.create(email="two@example.com", password="testing1234")

    def test_unique_ids(self):
        user1 = User.objects.get(email="one@example.com")
        user2 = User.objects.get(email="two@example.com")
        self.assertNotEqual(user1.id, user2.id)

    def test_unique_emails(self):
        self.assertRaises(IntegrityError, User.objects.create, email="one@example.com", password="differenttest")


class CustomerModelTests(TestCase):
    def setUp(self):
        user1 = User.objects.create(email="user1@example.com", password="test")
        Customer.objects.create(user=user1, first_name="Customer", last_name="One", phone_num=1000000000)

    def test_unique_customers(self):
        user1 = User.objects.get(email="user1@example.com")
        self.assertRaises(IntegrityError, Customer.objects.create, user=user1, first_name="Customer", last_name="Two",
                          phone_num=2000000000)


class CustomerCreateViewTests(TestCase):
    def test_customer_creation_successful_post_request(self):
        factory = APIRequestFactory()
        data = {"user": {"email": "user1@example.com", "password": "test"}, "first_name": "Customer",
                "last_name": "One", "phone_num": 1000000000}
        request = factory.post('/checkin/create_account/', data, format='json')

        view = CustomerCreate.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="user1@example.com").is_customer, True)


