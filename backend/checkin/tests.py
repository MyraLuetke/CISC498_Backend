from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from django.test import Client
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Customer, Business, Visit, UnregisteredVisit
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
        Customer.objects.create(user=user1, first_name="Customer", last_name="One", phone_num=1000000000, contact_pref="P")

    def test_unique_customers(self):
        user1 = User.objects.get(email="user1@example.com")
        self.assertRaises(IntegrityError, Customer.objects.create, user=user1, first_name="Customer", last_name="Two",
                          phone_num=2000000000, contact_pref="E")

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
            "phone_num": 1000000000,
            "contact_pref": 'P'
        }

        response = c.post('/checkin/customer/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="user1@example.com").is_customer, True)

    def test_customer_creation_failed_post_request(self):
        c = Client()
        data = {}

        response = c.post('/checkin/customer/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_creation_after_user_deactivation(self):
        c = Client()

        data = {
            "user":
            {
                "email": "user1@example.com",
                "password": "test"
            },
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": 1000000000,
            "contact_pref": 'P'
        }
        response = c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        user = User.objects.get(email="user1@example.com")
        user.is_active = False
        user.save()

        data = {
            "user":
                {
                    "email": "user1@example.com",
                    "password": "testing"
                },
            "first_name": "Customer",
            "last_name": "OneAgain",
            "phone_num": 1000000001,
            "contact_pref": 'E'
        }

        response = c.post('/checkin/customer/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="user1@example.com").is_customer, True)
        self.assertEqual(Customer.objects.get(user=User.objects.get(email="user1@example.com")).last_name, "OneAgain")


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
            "phone_num": "1111111111",
            "contact_pref": 'P'
        }
        c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        data = {
            "email": "user1@example.com",
            "password": "password"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

    def test_customer_detail_successful_get_request(self):
        c = Client()
        user_id = User.objects.get(email="user1@example.com").id

        response = c.get(f'/checkin/customer/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_detail_successful_put_request(self):
        c = Client()
        data = {
            "phone_num": "0000000000",
            "contact_pref": "E"
        }

        user_id = User.objects.get(email="user1@example.com").id
        response = c.put(f'/checkin/customer/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data,
                         content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Customer.objects.get(user=User.objects.get(id=user_id)).phone_num, "0000000000")
        self.assertEqual(Customer.objects.get(user=User.objects.get(id=user_id)).contact_pref, "E")

    def test_customer_detail_successful_delete_request(self):
        c = Client()
        user_id = User.objects.get(email="user1@example.com").id

        data = {
            "password": "password",
        }
        response = c.delete(f'/checkin/customer/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data,
                            content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=user_id).is_active, False)

class BusinessModelTests(TestCase):
    def setUp(self):
        user1 = User.objects.create(email="business1@example.com", password="test")
        Business.objects.create(user=user1, name="Business One", phone_num=1000000000, street_address="1234 Street St.",
                                city="City", postal_code="E4X 2M1", province="Ontario", capacity=123)

    def test_unique_businesses(self):
        user1 = User.objects.get(email="business1@example.com")
        self.assertRaises(IntegrityError, Business.objects.create, user=user1, name="Business Two",
                          phone_num=2000000000, street_address="3334 Street Ave.", city="Town",
                          postal_code="R4S 6M5", province="Ontario", capacity=123)

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
            "street_address": "1234 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 123,
        }

        response = c.post('/checkin/business/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="business@example.com").is_customer, False)

    def test_business_creation_failed_post_request(self):
        c = Client()
        data = {}

        response = c.post('/checkin/business/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_creation_after_user_deactivation(self):
        c = Client()

        data = {
            "user":
            {
                "email": "business@example.com",
                "password": "password"
            },
            "name": "business1",
            "phone_num": "1111111111",
            "street_address": "1234 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 123,
        }
        response = c.post('/checkin/business/create_account/', data=data, content_type="application/json")

        user = User.objects.get(email="business@example.com")
        user.is_active = False
        user.save()

        data = {
            "user":
            {
                "email": "business@example.com",
                "password": "password1"
            },
            "name": "business11",
            "phone_num": "1111111112",
            "street_address": "14 Ave St.",
            "city": "Town",
            "postal_code": "C4X 2M1",
            "province": "Ontario",
            "capacity": 120,
        }

        response = c.post('/checkin/business/create_account/', data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="business@example.com").is_customer, False)
        self.assertEqual(Business.objects.get(user=User.objects.get(email="business@example.com")).name, "business11")


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
            "street_address": "1234 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 123,
        }
        c.post('/checkin/business/create_account/', data=data, content_type="application/json")

        data = {
            "email": "business@example.com",
            "password": "password"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

    def test_business_detail_successful_get_request(self):
        c = Client()
        user_id = User.objects.get(email="business@example.com").id

        response = c.get(f'/checkin/business/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_business_detail_successful_put_request(self):
        c = Client()
        data = {
            "street_address": "999 Street St.",
        }

        user_id = User.objects.get(email="business@example.com").id
        response = c.put(f'/checkin/business/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Business.objects.get(user=User.objects.get(id=user_id)).street_address, "999 Street St.")

    def test_business_detail_successful_delete_request(self):
        c = Client()
        user_id = User.objects.get(email="business@example.com").id

        data = {
            "password": "password",
        }

        response = c.delete(f'/checkin/business/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data,
                            content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=user_id).is_active, False)


class ChangePasswordViewTests(TestCase):

    def setUp(self):
        c = Client()
        data = {
            "user":
                {
                    "email": "customer@example.com",
                    "password": "password"
                },
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": "1111111111",
            "contact_pref": 'P'
        }
        c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        data = {
            "email": "customer@example.com",
            "password": "password"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

    def test_change_password_successful_put_request(self):
        c = Client()
        data = {
            "old_password": "password",
            "new_password": "newpassword"
        }

        user_id = User.objects.get(email="customer@example.com").id
        response = c.put(f'/checkin/change_password/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access,
                         data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(id=user_id).check_password("newpassword"))

    def test_change_password_unsuccessful_put_request_wrong_password(self):
        c = Client()
        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword"
        }

        user_id = User.objects.get(email="customer@example.com").id
        response = c.put(f'/checkin/change_password/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access,
                         data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.get(id=user_id).check_password("password"))

    def test_change_password_unsuccessful_put_request_insufficient_data(self):
        c = Client()
        data = {
            "new_password": "newpassword"
        }

        user_id = User.objects.get(email="customer@example.com").id
        response = c.put(f'/checkin/change_password/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access,
                         data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.get(id=user_id).check_password("password"))


class ChangeEmailViewTests(TestCase):

    def setUp(self):
        c = Client()
        data = {
            "user":
                {
                    "email": "customer@example.com",
                    "password": "password"
                },
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": "1111111111",
            "contact_pref": 'P'
        }
        c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        data = {
            "email": "customer@example.com",
            "password": "password"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

    def test_change_email_successful_put_request(self):
        c = Client()
        data = {
            "email": "customer2@example.com",
        }

        user_id = User.objects.get(email="customer@example.com").id
        response = c.put(f'/checkin/change_email/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access,
                         data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=user_id).email, "customer2@example.com")

    def test_change_password_not_possible_through_this_view(self):
        c = Client()
        data = {
            "password": "newpassword",
        }

        user_id = User.objects.get(email="customer@example.com").id
        response = c.put(f'/checkin/change_email/{user_id}/', HTTP_AUTHORIZATION='Bearer ' + self.access,
                         data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.get(id=user_id).check_password("password"))



class UnregisteredVisitModelTests(TestCase):
    def setUp(self):
        user11 = User.objects.create(email="business1@example.com", password="test")
        business1 = Business.objects.create(user=user11, name="Business One", phone_num=1000000000,
                                            street_address="1234 Street St.", city="City", postal_code="E4X 2M1",
                                            province="Ontario", capacity=123)
        UnregisteredVisit.objects.create(dateTime='2006-10-25 14:30:59', first_name="First", last_name="Name",
                                         phone_num=1000000001, business=business1, numVisitors=3)

    def test_to_string(self):
        business1 = Business.objects.get(user=User.objects.get(email="business1@example.com"))
        visit1 = UnregisteredVisit.objects.get(first_name="First", phone_num=1000000001, business=business1)
        self.assertEqual(str(visit1), "First Name 1000000001 Business One 2006-10-25 14:30:59")


class BusinessAddedVisitCreateTests(TestCase):
    def setUp(self):
        c = Client()

        data = {
            "user":
                {
                    "email": "user1@example.com",
                    "password": "test"
                },
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": "1000000000",
            "contact_pref": "E"
        }
        c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        data = {
            "user":
                {
                    "email": "business1@example.com",
                    "password": "test"
                },
            "name": "business one",
            "phone_num": "1000000000",
            "street_address": "1234 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 123
        }
        c.post('/checkin/business/create_account/', data=data, content_type="application/json")

        data = {
            "email": "user1@example.com",
            "password": "test"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]


    def test_business_add_visit_creation_successful_post_request(self):
        c = Client()
        data = {
            "dateTime": "2006-10-25 14:30:59",
            "customer": "user1@example.com",
            "business": User.objects.get(email="business1@example.com").id,
            "numVisitors": "6"
        }
        response = c.post('/checkin/visit/business_create_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_business_add_visit_creation_failed_post_request(self):
        c = Client()
        data = {}
        #i get this for some reason and its coming from this code. so the error message prints in the shell for some reason 
        #..{'dateTime': [ErrorDetail(string='This field is required.', code='required')], 'customer': [ErrorDetail(string='This field is required.', code='required')], 'business':
        # [ErrorDetail(string='This field is required.', code='required')], 'numVisitors': [ErrorDetail(string='This field is required.', code='required')]}

        response = c.post('/checkin/visit/business_create_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BusinessAddUnregisteredVisitCreateTests(TestCase):
    def setUp(self):
        c = Client()

        data = {
            "user":
                {
                    "email": "business1@example.com",
                    "password": "test"
                },
            "name": "business one",
            "phone_num": "1000000000",
            "street_address": "1234 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 123
        }
        c.post('/checkin/business/create_account/', data=data, content_type="application/json")

        data = {
            "email": "business1@example.com",
            "password": "test"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

    def test_business_add_unregistered_visit_creation_successful_post_request(self):
        c = Client()
        data = {
            "dateTime": "2006-10-25 14:30:59",
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": 1000000000,
            "business": User.objects.get(email="business1@example.com").id,
            "numVisitors": "6"
        }
        response = c.post('/checkin/visit/business_create_unregistered_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_business_add_unregistered_visit_creation_failed_post_request(self):
        c = Client()
        data = {}

        response = c.post('/checkin/visit/business_create_unregistered_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VisitModelTests(TestCase):
    def setUp(self):
        user1 = User.objects.create(email="user1@example.com", password="test")
        user11 = User.objects.create(email="business1@example.com", password="test")
        customer1 = Customer.objects.create(user=user1, first_name="Customer", last_name="One", phone_num=1000000000)
        business1 = Business.objects.create(user=user11, name="Business One", phone_num=1000000000,
                                            street_address="1234 Street St.", city="City", postal_code="E4X 2M1",
                                            province="Ontario", capacity=123)
        Visit.objects.create(dateTime='2006-10-25 14:30:59', customer=customer1, business=business1, numVisitors=3)

    def test_to_string(self):
        customer1 = Customer.objects.get(user=User.objects.get(email="user1@example.com"))
        business1 = Business.objects.get(user=User.objects.get(email="business1@example.com"))
        visit1 = Visit.objects.get(customer=customer1, business=business1)
        self.assertEqual(str(visit1), "Customer One Business One 2006-10-25 14:30:59")


class VisitCreateViewTests(TestCase):
    def setUp(self):
        c = Client()

        data = {
            "user":
                {
                    "email": "user1@example.com",
                    "password": "test"
                },
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": "1000000000",
            "contact_pref": 'P'
        }
        c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        data = {
            "user":
                {
                    "email": "business1@example.com",
                    "password": "test"
                },
            "name": "business one",
            "phone_num": "1000000000",
            "street_address": "1234 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 123,
        }
        c.post('/checkin/business/create_account/', data=data, content_type="application/json")

        data = {
            "email": "user1@example.com",
            "password": "test"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

    def test_visit_creation_successful_post_request(self):
        c = Client()
        data = {
            "dateTime": "2006-10-25 14:30:59",
            "customer": User.objects.get(email="user1@example.com").id,
            "business": User.objects.get(email="business1@example.com").id,
            "numVisitors": "6"
        }
        response = c.post('/checkin/visit/create_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_visit_creation_failed_post_request(self):
        c = Client()
        data = {}

        response = c.post('/checkin/visit/create_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VisitListViewTests(TestCase):

    def setUp(self):
        c = Client()
        data = {
            "user":
                {
                    "email": "customer1@example.com",
                    "password": "password"
                },
            "first_name": "Customer",
            "last_name": "One",
            "phone_num": "1111111111",
            "contact_pref": 'P'
        }
        c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        data = {
            "user":
                {
                    "email": "customer2@example.com",
                    "password": "password"
                },
            "first_name": "Customer",
            "last_name": "Two",
            "phone_num": "1111111111",
            "contact_pref": 'E'
        }
        c.post('/checkin/customer/create_account/', data=data, content_type="application/json")

        data = {
            "user":
                {
                    "email": "business1@example.com",
                    "password": "test"
                },
            "name": "business one",
            "phone_num": "1000000000",
            "street_address": "1234 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 123,
        }
        c.post('/checkin/business/create_account/', data=data, content_type="application/json")

        data = {
            "user":
                {
                    "email": "business2@example.com",
                    "password": "test"
                },
            "name": "business two",
            "phone_num": "1000000000",
            "street_address": "123 Street St.",
            "city": "City",
            "postal_code": "E4X 2M1",
            "province": "Ontario",
            "capacity": 120,
        }
        c.post('/checkin/business/create_account/', data=data, content_type="application/json")

        data = {
            "email": "customer2@example.com",
            "password": "password"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

        data = {
            "dateTime": "2021-03-24 20:30:23",
            "customer": User.objects.get(email="customer2@example.com").id,
            "business": User.objects.get(email="business2@example.com").id,
            "numVisitors": "4"
        }
        response = c.post('/checkin/visit/create_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")

        data = {
            "email": "customer1@example.com",
            "password": "password"
        }
        response = c.post('/api/token/', data=data, content_type="application/json")
        self.access = response.json()["access"]

        data = {
            "dateTime": "2021-01-25 14:30:59",
            "customer": User.objects.get(email="customer1@example.com").id,
            "business": User.objects.get(email="business1@example.com").id,
            "numVisitors": "6"
        }
        response = c.post('/checkin/visit/create_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")

        data = {
            "dateTime": "2021-03-24 20:30:23",
            "customer": User.objects.get(email="customer1@example.com").id,
            "business": User.objects.get(email="business2@example.com").id,
            "numVisitors": "2"
        }
        response = c.post('/checkin/visit/create_visit/', HTTP_AUTHORIZATION='Bearer ' + self.access, data=data, content_type="application/json")

    def test_visit_list_successful_get_request(self):
        c = Client()

        response = c.get("/checkin/visit/", HTTP_AUTHORIZATION='Bearer ' + self.access)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.content)