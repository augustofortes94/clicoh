from .test_setup import UserTestCase
from rest_framework import status

class ProductTestCase(UserTestCase):
    def test_create_user(self):
        """self.client.post(self.login_url)
        response = self.client.post('/products/', {'id':'1', 'name':'product_test', 'price':'123.45', 'stock':10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)"""
        pass