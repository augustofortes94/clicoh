from django.urls import path, include
from . import views 
from rest_framework import routers 

router = routers.DefaultRouter()
router.register('orderDetails', views.OrderDetailView)
router.register('order', views.OrderView)
router.register('products', views.ProductView)

urlpatterns = [
    path('', include(router.urls)),
    path('product/<str:id>', views.ProductViewApi.as_view(), name='edit_product_stock')
]
