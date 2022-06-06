from itertools import product
from math import prod
from urllib import response

from requests import request
from .test_setup import UserTestCase
from rest_framework import status
from ..models import Product

class ProductTestCase(UserTestCase):
    def create_product(self):
        return Product.objects.create(
            id="123",
            name="product_test",
            price=123.45,
            stock=12)

    def test_get_products(self):
        product = self.create_product()
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], product.id)
        self.assertEqual(response.data[0]['name'], product.name)
        self.assertEqual(response.data[0]['price'], str(product.price))
        self.assertEqual(response.data[0]['stock'], product.stock)

    def test_get_products_by_id(self):
        product = self.create_product()
        response = self.client.get('/products/123/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], product.id)
        self.assertEqual(response.data['name'], product.name)
        self.assertEqual(response.data['price'], str(product.price))
        self.assertEqual(response.data['stock'], product.stock)

        ##Error
        response = self.client.get('/products/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")
    
    def test_post_product(self):
        response = self.client.post('/products/', {'id':'234', 'name':'product_test_2', 'price':123.45, 'stock':20})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], '234')
        self.assertEqual(response.data['name'], 'product_test_2')
        self.assertEqual(response.data['price'], '123.45')
        self.assertEqual(response.data['stock'], 20)

        ##Error
        response = self.client.post('/products/', {'id':'234', 'name':'product_test_2', 'price':123.45, 'stock':20})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Error: this id product already exist")

    def test_put_product(self):
        product = self.create_product()
        response = self.client.put('/products/' + product.id + '/', {'id':'12', 'name':'product_test_3', 'price':12.05, 'stock':2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], '12')
        self.assertEqual(response.data['name'], 'product_test_3')
        self.assertEqual(response.data['price'], '12.05')
        self.assertEqual(response.data['stock'], 2)

        self.assertNotEqual(product.id, response.data['id'])
        self.assertNotEqual(product.name, response.data['name'])
        self.assertNotEqual(product.price, response.data['price'])
        self.assertNotEqual(product.stock, response.data['stock'])

        ##Error
        response = self.client.put('/products/' + product.id + 'h/', {'id':'12', 'name':'product_test_3', 'price':12.05, 'stock':2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    def test_patch_product(self):
        product = self.create_product()
        response = self.client.patch('/product/' + product.id, {'stock':3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], product.id)
        self.assertEqual(response.data['name'], product.name)
        self.assertEqual(response.data['price'], str(product.price))
        self.assertEqual(response.data['stock'], 3)

        ##Error
        response = self.client.patch('/product/' + product.id + '1', {'stock':3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Error: this id product doesn't exist")

    def test_detele_product(self):
        product = self.create_product()
        response = self.client.delete('/products/' + product.id + '/')

        ##Error
        response = self.client.delete('/products/' + product.id + 'a/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], "Error: this id product already exist")