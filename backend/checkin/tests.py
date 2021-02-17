from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from django.test import Client

from .models import User, Customer
from .views import CustomerCreate


class UserModelTests(TestCase):
    def setUp(self):
        User.objects.create(email="one@example.com", password="test")
        User.objects.create(email="two@example.com", password="testing1234")
        User.objects.create_superuser(email="super@example.com", password="test")

    def test_unique_ids(self):
        user1 = User.objects.get(email="one@example.com")
        user2 = User.objects.get(email="two@example.com")
        self.assertNotEqual(user1.id, user2.id)

    def test_unique_emails(self):
        self.assertRaises(IntegrityError, User.objects.create, email="one@example.com", password="differenttest")

    def test_create_superuser(self):
        user1 = User.objects.get(email="super@example.com")
        self.assertEqual(user1.is_superuser, True)
        self.assertEqual(user1.is_staff, True)

    def test_create_superuser_invalid_is_superuser(self):
        self.assertRaises(ValueError, User.objects.create_superuser, email="super@example.com", password="test", is_superuser=False)

    def test_create_superuser_invalid_is_staff(self):
        self.assertRaises(ValueError, User.objects.create_superuser, email="super@example.com", password="test", is_staff=False)


class CustomerModelTests(TestCase):
    def setUp(self):
        user1 = User.objects.create(email="user1@example.com", password="test")
        Customer.objects.create(user=user1, first_name="Customer", last_name="One", phone_num=1000000000)

    def test_unique_customers(self):
        user1 = User.objects.get(email="user1@example.com")
        self.assertRaises(IntegrityError, Customer.objects.create, user=user1, first_name="Customer", last_name="Two",
                          phone_num=2000000000)

    def test_to_string(self):
        customer1 = Customer.objects.get(user=User.objects.get(email="user1@example.com"))
        self.assertEqual(str(customer1), "Customer One")


class CustomerCreateViewTests(TestCase):
    def test_customer_creation_successful_post_request(self):
        c = Client()
        data = {
            "user":
            {
                "email": "user1@example.com",
                "password": "test"
            },
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": 1000000000
        }

        response = c.post('/checkin/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="user1@example.com").is_customer, True)

    def test_customer_creation_failed_post_request(self):
        c = Client()
        data = {}

        response = c.post('/checkin/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
