"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import CreateProductHistoryView, home,CustomerCreate, CustomerDelete,CustomerList , CustomerDetail, CustomerUpdate, ProductCreate, ProductDetail, ProductHistoryByCustomerView, MyProductHistoryView, ProductList, ProductUpdate,ProductDelete

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('my/product-history/', MyProductHistoryView.as_view(),name='my-product-history'),
    
    path('create-customer/', CustomerCreate.as_view(), name='create-customer'),
    path('customers', CustomerList.as_view()),
    path('<int:pk>/', CustomerDetail.as_view(), name='retrieve-customer'),
    path('update-customer/<int:pk>/', CustomerUpdate.as_view(), name='update-customer'),
    path('delete/<int:pk>/', CustomerDelete.as_view(), name='delete-customer'),
    
    path('products', ProductList.as_view()),
    path('create-product/', ProductCreate.as_view(), name='create-product'),
    path('<int:pk>/', ProductDetail.as_view(), name='retrieve-product'),
    path('update-product/<int:pk>/', ProductUpdate.as_view(), name='update-product'),
    path('delete/<int:pk>/', ProductDelete.as_view(), name='delete-product'),
    
    path('create-product-history/', CreateProductHistoryView.as_view(), name='create-product-history'),
    path('customers/<int:customer_id>/product-history/', ProductHistoryByCustomerView.as_view(), name='customer-product-history'),

]
