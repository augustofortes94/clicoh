import requests
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order, OrderDetail, Product
from .serializers import OrderSerializer, OrderDetailSerializer, ProductSerializer, RegisterSerializer
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .decorators import api_login_required
import datetime, jwt

class OrderView(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def retrieve(self, request, *args, **kwargs):   #get by
        orderDetails = list(OrderDetail.objects.filter(order=self.get_object()).values())
        return Response({'id':self.get_object().id, 'date_time':self.get_object().date_time, 'order_details':orderDetails})

    @api_login_required
    def create(self, request, *args, **kwargs):
        order_object = Order.objects.create()
        for product in request.data['products']:
            try:
                product_object = Product.objects.get(name=product['name'])  #if product exist
                if product_object.stock - int(product['stock']) >= 0:    #if stock is enough
                    serializer = OrderDetailSerializer(data= {'order': order_object.id, 'cuantity': product['stock'], 'product': product_object.id})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()   #create OrderDetail
                    ProductView.edit_stock(product_object.id, product_object.stock - int(product['stock'])) #update stock
            except:
                pass
        return Response(status=status.HTTP_202_ACCEPTED)
    
    @api_login_required
    def update(self, request, *args, **kwargs):
        if self.detect_duplicates(request):
            return Response({'message':'Duplicated products'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            for product in request.data['products']:    #detect if there is a product with not enough stock, and break before save any change
                try:
                    product_object = Product.objects.get(name=product['name'])  #if product exist
                    orderDetail_object = OrderDetail.objects.get(order=self.get_object(), product=product_object.id)
                    amount = product_object.stock + orderDetail_object.cuantity - int(product['stock'])
                    if amount < 0:    #if stock is enough, return bad request
                        return Response({'message':'The stock requested is out of range'}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    pass
            
            for product in request.data['products']:
                product_object = Product.objects.get(name=product['name'])  #if product exist
                orderDetail_object = OrderDetail.objects.get(order=self.get_object(), product=product_object.id)
                amount = product_object.stock + orderDetail_object.cuantity - int(product['stock'])
                orderDetail_object.cuantity = product['stock']
                orderDetail_object.save()
                ProductView.edit_stock(product_object.id, amount) #update stock
            return Response(status=status.HTTP_202_ACCEPTED)

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

    def detect_duplicates(self, request):
        dict = {}
        a=0
        for product in request.data['products']:
            dict[a] = product['name']
            a += 1
        rev_dict = {}
        for key, value in dict.items():
            rev_dict.setdefault(value, set()).add(key)
        return [key for key, values in rev_dict.items() if len(values) > 1]

    @api_login_required
    @action(detail=True, methods=['get'])
    def get_total(self, request, *args, **kwargs):
        try:
            total = 0
            for orderDetail in OrderDetail.objects.filter(order=self.get_object()):
                product_object = Product.objects.get(id=orderDetail.product_id)
                total = total + (product_object.price * orderDetail.cuantity)
            return Response({'total_price':total})
        except:
            pass
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @api_login_required
    @action(detail=True, methods=['get'])
    def get_total_usd(self, request, *args, **kwargs):
        try:
            response = requests.get('https://www.dolarsi.com/api/api.php?type=valoresprincipales').json()
            dolar_blue = float(response[1]['casa']['venta'].replace(',', '.'))
            return Response({'total_price_usd':round((float(self.get_total(request).data['total_price']) / dolar_blue), 2)})
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer

    @api_login_required
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @api_login_required
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @api_login_required
    def destroy(self, request, *args, **kwargs):
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
            
class APIRegister(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'succes'})           