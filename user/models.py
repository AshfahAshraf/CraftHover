from django.db import models
# Create your models here.
#-----  User ----#

class User(models.Model):
    Name = models.CharField(max_length=200)
    Username =models.CharField(max_length=250)
    Email =models.EmailField(unique=True,null=True, blank=True)
    Phone_Number = models.CharField(max_length=20,null=True,blank=True)
    Address =models.CharField(max_length=200,null=True,blank=True)
    Password = models.CharField(max_length=250)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True,null=True)

    def __str__(self):
        return self.Username
    
# ---  Artisan ----#

class Artisan(models.Model):  
     name = models.CharField(max_length=200)
     email = models.EmailField(unique=True)
     phone = models.CharField(max_length=20)
     password = models.CharField(max_length=255)

     shop_name = models.CharField(max_length=200)

     address = models.CharField(max_length=200)
     city = models.CharField(max_length=100)
     state =models.CharField(max_length=100)
     pincode =models.CharField(max_length=10)

     profile_image = models.ImageField(upload_to="artisan_profiles/",null=True,blank=True)

     bio = models.TextField(blank=True)


     bank_account_number = models.CharField(max_length=30)
     ifsc_code = models.CharField(max_length=20)   

     def __str__(self):
          return self.shop_name

 #-- category --#    

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
          return self.name

 #--sub category --#    


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
          return self.name

# -----  Product -----#

class Product(models.Model):
     artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE)

     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
     subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
  
     Product_name = models.CharField(max_length=200)

     Actual_price = models.DecimalField(max_digits=10, decimal_places=2)
     Offer_price = models.DecimalField(max_digits= 10, decimal_places=2)
     
     Quantity = models.IntegerField()

     Description = models.TextField()
     
#  IMAGES 

     front_image = models.ImageField(upload_to='products/', null=True, blank=True)
     left_image = models.ImageField(upload_to='products/', null=True, blank=True)
     right_image = models.ImageField(upload_to='products/', null=True, blank=True)

     def __str__(self):
          return self.Product_name

#----- cart -----#

class Cart(models.Model):

     user =models.ForeignKey(User, on_delete=models.CASCADE)
     product=models.ForeignKey(Product, on_delete=models.CASCADE)

     quantity = models.IntegerField(default=1)

     def __str__(self):
          return f"{self.user.Username} - {self.product.Product_name}"
     
     class Meta:
          unique_together = ('user', 'product')

#------ Wishlist ------#
          
class Wishlist(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     product = models.ForeignKey(Product, on_delete=models.CASCADE)


     class Meta:
          unique_together = ('user', 'product')

     def __str__(self):
        return f"{self.user.Username} - {self.product.Product_name}"
    
 #----  Order -----#
          
class Order(models.Model):

     STATUS_CHOICES = [
          ("Pending","Pending"),
          ("Shipped","Shipped"),
          ("Delivered","Delivered"),
          ("Cancelled","Cancelled"),
     ]

     user = models.ForeignKey(User, on_delete=models.CASCADE)
     product =models.ForeignKey(Product, on_delete=models.CASCADE)
     
     quantity = models.IntegerField()
     total_price = models.DecimalField(max_digits=10,decimal_places=2)
     final_price = models.DecimalField(max_digits=10, decimal_places=2)
     address = models.TextField(null=True,blank=True)
     order_date = models.DateField(auto_now_add=True)
     status = models.CharField(max_length=20,choices=STATUS_CHOICES, default="Pending")

     def __str__(self):
        return f"Order {self.id} - {self.status}"

#----- Complaint ----#

class Complaint(models.Model):
     
     Fullname =models.CharField(max_length=100)
     Email =models.EmailField()
     Phonenumber = models.CharField(max_length=15)

     Orderid = models.ForeignKey(Order, on_delete=models.CASCADE)
     Productname = models.ForeignKey(Product, on_delete=models.CASCADE)
     Issue_type = models.CharField(max_length=100)
     Product_image =models.ImageField(upload_to="complaints/",null=True, blank=True)
     Description = models.TextField()
     created_at =models.DateTimeField(auto_now_add=True)


     def __str__(self):
          return self.Fullname

#-- my account --#

class Address(models.Model):
     user =models.ForeignKey(User, on_delete=models.CASCADE)
     full_name = models.CharField(max_length=100)
     street = models.CharField(max_length=200) 
     city = models.CharField(max_length=100)
     state = models.CharField(max_length=100)
     pincode = models.CharField(max_length=10)
     phone = models.CharField(max_length=15)

     def __str__(self):
          return self.full_name
     

