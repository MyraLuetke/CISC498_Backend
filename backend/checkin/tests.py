from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from django.test import Client
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Customer, Business
from .views import CustomerCreate


class UserModelTests(TestCase):
    def setUp(self):
        User.objects.create(email="one@example.com", password="test")
        User.objects.create(email="two@example.com", password="testing1234")
        User.objects.create_superuser(email="super@example.com", password="test")

    def test_unique_ids(self):
        user1 = User.objects.get(email="one@example.com")
        user2 = User.objects.get(email="two@example.com")
        self.assertNotEqual(user1.uuid, user2.uuid)

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


class CustomerDetailViewTests(TestCase):
    def setUp(self):
        c = Client()
        data = {
            "user":
                {
                    "email": "user1@example.com",
                    "password": "password"
                },
            "first_name": "User",
            "last_name": "One",
            "phone_num": "1111111111"
        }
        c.post('/checkin/create_account/', data=data, content_type="application/json")

    def test_customer_detail_successful_get_request(self):
        c = Client()
        user_id = User.objects.get(email="user1@example.com").uuid

        response = c.get(f'/checkin/{user_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_detail_successful_put_request(self):
        c = Client()
        data = data = {
            "phone_num": "0000000000"
        }

        user_id = User.objects.get(email="user1@example.com").uuid
        response = c.put(f'/checkin/{user_id}/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Customer.objects.get(user=User.objects.get(email="user1@example.com")).phone_num, "0000000000")

    def test_customer_detail_successful_delete_request(self):
        c = Client()
        user_id = User.objects.get(email="user1@example.com").uuid

        response = c.delete(f'/checkin/{user_id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(ObjectDoesNotExist, Customer.objects.get, user=User.objects.get(email="user1@example.com"))


class BusinessModelTests(TestCase):
    def setUp(self):
        user1 = User.objects.create(email="business1@example.com", password="test")
        Business.objects.create(user=user1, name="Business One", phone_num=1000000000, address="1234 Street St.", capacity=123)

    def test_unique_businesses(self):
        user1 = User.objects.get(email="business1@example.com")
        self.assertRaises(IntegrityError, Business.objects.create, user=user1, name="Business Two", phone_num=2000000000, address="1235 Street St.", capacity=123)

    def test_to_string(self):
        business1 = Business.objects.get(user=User.objects.get(email="business1@example.com"))
        self.assertEqual(str(business1), "Business One")


class BusinessCreateViewTests(TestCase):
    def test_business_creation_successful_post_request(self):
        c = Client()
        data = {
            "user":
                {
                    "email": "business@example.com",
                    "password": "password"
                },
            "name": "business1",
            "phone_num": "1111111111",
            "address": "1234 Street St.",
            "capacity": 123
        }

        response = c.post('/checkin/create_business_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="business@example.com").is_customer, False)

    def test_business_creation_failed_post_request(self):
        c = Client()
        data = {}

        response = c.post('/checkin/create_business_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BusinessDetailViewTests(TestCase):
    def setUp(self):
        c = Client()
        data = {
            "user":
                {
                    "email": "business@example.com",
                    "password": "password"
                },
            "name": "business1",
            "phone_num": "1111111111",
            "address": "1234 Street St.",
            "capacity": 123
        }
        c.post('/checkin/create_business_account/', data=data, content_type="application/json")

    def test_business_detail_successful_get_request(self):
        c = Client()
        user_id = User.objects.get(email="business@example.com").uuid

        response = c.get(f'/checkin/business/{user_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_business_detail_successful_put_request(self):
        c = Client()
        data = data = {
            "address": "999 Street St.",
        }

        user_id = User.objects.get(email="business@example.com").uuid
        response = c.put(f'/checkin/business/{user_id}/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Business.objects.get(user=User.objects.get(email="business@example.com")).address, "999 Street St.")

    def test_business_detail_successful_delete_request(self):
        c = Client()
        user_id = User.objects.get(email="business@example.com").uuid

        response = c.delete(f'/checkin/business/{user_id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(ObjectDoesNotExist, Business.objects.get, user=User.objects.get(email="business@example.com"))
