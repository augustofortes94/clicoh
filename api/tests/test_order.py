from .test_setup import UserTestCase
from .test_product import ProductTestCase
from rest_framework import status
from ..models import Order

class OrderTestCase(UserTestCase):
    def create_order(self):
        return Order.objects.create()

    def test_get_order(self):
        order = self.create_order()
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], order.id)
        self.assertEqual(response.data[0]['date_time'], str(order.date_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')))
    
    def test_get_order_by_id(self):
        order = self.create_order()
        response = self.client.get('/orders/'+ str(order.id) +'/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(response.data['date_time'], order.date_time)

        ##Error
        response = self.client.get('/products/1000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")
    
    def test_post_order(self):
        product = ProductTestCase.create_product(self)
        response = self.client.post('/orders/', {"products": [{"name":product.name,"stock": 2}]})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_delete_order(self):
        order = self.create_order()
        response = self.client.delete('/orders/' + str(order.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response = self.client.get('/orders/' + str(order.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

        ##Error
        response = self.client.delete('/orders/' + str(order.id) + 'h/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)