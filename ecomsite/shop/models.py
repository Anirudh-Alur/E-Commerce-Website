from django.db import models

# Create your models here.
class Products(models.Model):
 
    def __str__(self):
        return self.title
    title = models.CharField(max_length=200)
    price = models.FloatField()
    discount_price = models.FloatField()
    category = models.CharField(max_length=200, default='')
    description = models.TextField()
    image = models.CharField(max_length=300)
 
 
# models.py

# shop/models.py

from django.db import models

class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)  
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)
    items = models.TextField()
    total = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


    
   