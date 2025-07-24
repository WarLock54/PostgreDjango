from rest_framework import serializers

from .models import Product,Customer,ProductHistory

class ProductSerializers(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields= ['pk','id','name','price','stock','description']

class CustomerSerializers(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields= ['pk', 'id', 'first_name', 'last_name', 'email', 'user']
        

class ProductHistorySerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductHistory
        fields= ['pk','id','product','purchase_date']