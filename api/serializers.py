from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from .models import Order, OrderDetail, Product

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'date_time')

class OrderDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ('id', 'order', 'cuantity', 'product')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock')