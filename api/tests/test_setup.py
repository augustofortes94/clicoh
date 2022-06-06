from rest_framework.test import APITestCase
from rest_framework import status

class UserTestCase(APITestCase):
    def setUp(self):
        self.register_url = '/register/'
        self.login_url = '/login/'
        response = self.client.post(self.register_url, {'username':'testing_login', 'email':'test@test.com', 'password':'admin123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.login_url, {'username':'testing_login', 'password':'admin123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()