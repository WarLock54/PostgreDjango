from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from myapp.models import Customer, Product, ProductHistory, DailyToken
from django.utils import timezone


class CustomerProductTests(APITestCase):

    def setUp(self):
        # User oluştur
        """
        Prepare test fixtures for tests.
        
        Creates two users, two customers (one linked to the primary test user), and a product, then logs the test client in as the primary test user to allow authenticated API requests.
        """
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass123"
        )

        # Customer oluştur
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="Test",
            last_name="Customer",
            email="test@example.com"
        )
        self.other_customer = Customer.objects.create(
            user=self.other_user,
            name="Other Customer"
        )

        # Product oluştur
        self.product = Product.objects.create(
            name="Test Product",
            price=100,
            stock=10
        )
        # Login
        self.client.login(username="testuser", password="testpass123")

    # -------------------------
    # CUSTOMER TESTS
    # -------------------------

    def test_customer_list(self):
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_detail(self):
        response = self.client.get(f"/customers/{self.customer.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------
    # PRODUCT TESTS
    # -------------------------

    def test_product_list(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_detail(self):
        response = self.client.get(f"/products/{self.product.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------
    # PRODUCT HISTORY TESTS
    # -------------------------

    def test_create_product_history(self):
        url = "/product-history/create/"
        data = {
            "product_id": self.product.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductHistory.objects.count(), 1)

    def test_my_product_history(self):
        ProductHistory.objects.create(
            customer=self.customer,
            product=self.product
        )

        response = self.client.get("/product-history/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    def test_product_history_by_customer_permission_denied(self):
        """
        Cannot access another user's customer data
        """
        url = f"/product-history/customer/{self.other_customer.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------
    # DAILY TOKEN TESTS
    # -------------------------

    def test_daily_token_create(self):
        url = "/daily-token/"
        data = {
            "username": "testuser",
            "password": "testpass123"
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

        # DB kontrol
        self.assertTrue(
            DailyToken.objects.filter(user=self.user).exists()
        )

    def test_daily_token_same_day(self):
        today = timezone.now().date()
        DailyToken.objects.create(
            user=self.user,
            token="old_token",
            date_created=today
        )

        url = "/daily-token/"
        data = {
            "username": "testuser",
            "password": "testpass123"
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], "old_token")