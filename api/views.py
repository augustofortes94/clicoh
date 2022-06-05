from unicodedata import name
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, OrderDetail, Product
from .serializers import OrderSerializer, OrderDetailSerializer, ProductSerializer
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .decorators import api_login_required
import datetime, jwt

class OrderView(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @api_login_required
    def create(self, request, *args, **kwargs):
        order_object = Order.objects.create()
        for product in request.data['products']:
            try:
                product_object = Product.objects.get(name=product['name'])  #if product exist
                if product_object.stock - int(product['stock']) >= 0:    #if stock is enough
                    OrderDetail.objects.create(
                        order= order_object,
                        cuantity= product['stock'],
                        product= product_object,
                    )
                    ProductView.edit_stock(product_object.id, product_object.stock - int(product['stock'])) #update stock
            except:
                pass
        return Response(status=status.HTTP_202_ACCEPTED)
    
    @api_login_required
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @api_login_required
    def destroy(self, request, *args, **kwargs):
        try:
            for orderDetail in OrderDetail.objects.filter(order=self.get_object()):
                product_object = Product.objects.get(id=orderDetail.product_id)
                ProductView.edit_stock(product_object.id, orderDetail.cuantity + product_object.stock) #update stock
                OrderDetail.objects.filter(id=orderDetail.id).delete()
        except:
            pass
        return super().destroy(request, *args, **kwargs)

class OrderDetailView(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer

    @api_login_required
    def create(self, request, *args, **kwargs):
        product = Product.objects.get(id=request.data['product'])
        if product.stock < int(request.data['cuantity']) or product.stock <= 0:
            return JsonResponse({'message':"Error: stock of that product is not enough"})
        else:
            order_object = Order.objects.create()
            ProductView.edit_stock(product.id, product.stock - int(request.data['cuantity']))
            serializer = OrderDetailSerializer(data= {'order': order_object.id, 'cuantity': request.data['cuantity'], 'product': request.data['product']})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @api_login_required
    def update(self, request, *args, **kwargs):
        print(request.data)
        orderDetail_object = OrderDetail.objects.get(id=request.data['id'])
        return super().update(request, *args, **kwargs)

    @api_login_required
    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(id=self.get_object().product.id)
        cant = self.get_object().cuantity + product.stock
        ProductView.edit_stock(self.get_object().product.id, cant)
        return super().destroy(request, *args, **kwargs)

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @api_login_required
    def create(self, request, *args, **kwargs):
        if len(list(Product.objects.filter(id=request.data['id']).values())) > 0:
            return JsonResponse({'message':"Error: this id product already exist"})
        else:
            serializer = ProductSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    def edit_stock(id, stock):
        product_object = Product.objects.get(id=id)
        product_object.stock = stock
        product_object.save()
        return product_object
    
    @api_login_required
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class ProductViewApi(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @api_login_required
    def patch(self, request, id, *args, **kargs):   #Edit STOCK
        data = request.data
        if len(list(Product.objects.filter(id=id).values())) == 0:
            return JsonResponse({'message':"Error: this id product doesn't exist"})
        if not 'stock' in data:
            return JsonResponse({'message':"Error: this funtion is only for stock update"})
        serializer = ProductSerializer(ProductView.edit_stock(id, data['stock']))
        return Response(serializer.data)

class ApiLogin(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'message':"Error: user not found..."},status=status.HTTP_401_UNAUTHORIZED)

        else:
            if not user.check_password(password):
                return Response({'message':"Error: incorrect password..."},status=status.HTTP_401_UNAUTHORIZED)
            
            payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')

            response = Response(status=status.HTTP_200_OK)
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {'message': "Succes"}
            return response
            
            