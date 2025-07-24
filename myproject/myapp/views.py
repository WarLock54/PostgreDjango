from django.shortcuts import render

from .serializers import CustomerSerializers,ProductSerializers,ProductHistorySerializers
from rest_framework import generics,permissions
from .models import Customer,Product,ProductHistory
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import DailyToken
from django.contrib.auth import authenticate
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to My Django App!")

class CustomerCreate(generics.CreateAPIView):
    queryset = Customer.objects.all(),
    serializer_class = CustomerSerializers
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class CustomerList(generics.ListAPIView):
    queryset=Customer.objects.all()
    serializer_class = CustomerSerializers
    
class CustomerDetail(generics.RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializers
    
class CustomerUpdate(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializers
    
class CustomerDelete(generics.RetrieveDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializers
    
class ProductCreate(generics.CreateAPIView):
    queryset = Product.objects.all(),
    serializer_class = ProductSerializers


class ProductList(generics.ListAPIView):
    queryset=Product.objects.all()
    serializer_class = ProductSerializers

class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    
class ProductUpdate(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    
class ProductDelete(generics.RetrieveDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers

## customer a ait productları listeler
class ProductHistoryByCustomerView(generics.ListAPIView):
    serializer_class = ProductHistorySerializers
    permission_classes = [permissions.IsAuthenticated]  # login şartı
    
    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise PermissionDenied("Bu müşteri kaydı bulunamadı.")
        
        if customer.user != self.request.user:
            raise PermissionDenied("Bu veriyi erişme izninz yok")
        return ProductHistory.objects.filter(customer=customer)
    
#login olan kullanıcıya ait verileri direkt döndürmek
class MyProductHistoryView(generics.ListAPIView):
    serializer_class = ProductHistorySerializers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        customer = Customer.objects.get(user=self.request.user)
        return ProductHistory.objects.filter(customer=customer)

class CreateProductHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response({"detail": "Bu kullanıcıya ait müşteri bulunamadı."}, status=404)

        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"detail": "product_id alanı zorunludur."}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": f"id={product_id} olan ürün bulunamadı."}, status=404)

        ProductHistory.objects.create(customer=customer, product=product)

        return Response(
            {"detail": f"ProductHistory oluşturuldu (Customer: {customer.id}, Product: {product.id})"},
            status=201
        )

class DailyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if not user:
            return Response({"detail": "Geçersiz kullanıcı adı veya şifre"}, status=401)

        today = timezone.now().date()
        try:
            daily_token = DailyToken.objects.get(user=user)
            if daily_token.date_created == today:
                # Aynı günse, mevcut token'ı dön
                return Response({"token": daily_token.token})
            else:
                # Yeni günse, yeni token üret
                daily_token.token = self.create_token(user)
                daily_token.save()
        except DailyToken.DoesNotExist:
            # İlk kez login oluyorsa
            token = self.create_token(user)
            DailyToken.objects.create(user=user, token=token, date_created=today)
            return Response({"token": token})

        return Response({"token": daily_token.token})

    def create_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)  # sadece access token dönülüyor