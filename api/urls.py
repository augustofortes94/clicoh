from django.urls import path, include
from . import views
from rest_framework import routers
from .views import ApiLogin, APIRegister

router = routers.DefaultRouter()
router.register('orderDetails', views.OrderDetailView)
router.register('orders', views.OrderView)
router.register('products', views.ProductView)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', ApiLogin.as_view(), name='api_login'),
    path('register/', APIRegister.as_view(), name='api_register'),
    path('product/<str:id>', views.ProductViewApi.as_view(), name='edit_product_stock'),
]
