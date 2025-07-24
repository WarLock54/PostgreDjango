from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    id = models.AutoField(primary_key=True) 
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null= True,blank=True)  # güvenlik için
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    
    customer = models.ForeignKey(
        Customer,
        on_delete= models.CASCADE,
        related_name='products',
        null=True, blank=True
    )
    
    def __str__(self):
        return self.name
    
class ProductHistory(models.Model):
    id = models.AutoField(primary_key=True)  
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="histories")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

class DailyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField()
    date_created = models.DateField(auto_now_add=True)