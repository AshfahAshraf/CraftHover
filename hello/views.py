from django.shortcuts import render,redirect
from .models import * 
from django.db.models import Q ,Sum
from django.conf import settings

#order

from datetime import timedelta
from django.utils import timezone

# email
import random
from django.core.mail import send_mail

# contact
from django.contrib import messages

#description
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.ai_description import generate_description


#cart
from django.shortcuts import get_object_or_404
# from django.contrib.auth.decorators import login_required
# @login_required



# Create your views here.


def index(request):

    if request.method == 'POST':

        #REGISTER
        if "register" in request.POST:
            username = request.POST["textUsername"]
            email_phone = request.POST["textEmailPhone"]
            password = request.POST["textPassword"]
            confirm_password = request.POST["textConfirmPassword"]

            if password != confirm_password:
                print("passwords do not match")
                return render(request,"register.html")
        
            email = None
            phone_number = None

            if "@" in email_phone:
                email = email_phone
            else:
                phone_number = email_phone

            reg = User(Username =username,
                       Email =email,
                       Phone_Number =phone_number,
                       Password = password
            ) 
            reg.save()


        #LOGIN

        elif "login" in request.POST:
            email_phone = request.POST["textEmailPhone"]  # email or phone
            password = request.POST["textPassword"]

            try:
                user = User.objects.get(
                    Q(Email = email_phone) | Q(Phone_Number = email_phone),
                    Password =password
                )

                request.session["user_id"] = user.id
                request.session["user_name"] = user.Username
                return redirect("home")
            except User.DoesNotExist:
                print("invalid login")
        

    return render(request, "register.html")



 
########
#email 

# send otp 

def send_otp(request):

    if request.method == "POST":
        email = request.POST["email"]


        #check if email exists
        if not User.objects.filter(Email=email).exists():
            return render(request, "send_otp.html",{"error": "Email not registered"})

        otp = str(random.randint(100000, 999999))

        #store in session instead of database
        request.session['email'] = email
        request.session['otp'] =otp

        send_mail(
            "Password Reset OTP",
            f"Your OTP is {otp}",
            "yourgmail@gmail.com",
            [email],
            fail_silently=False,
        )

        

        return redirect("verify_otp")
    
    return render(request, "send_otp.html")


#verify otp

def verify_otp(request):

    if request.method == "POST":
        user_otp = request.POST["otp"]
       


        if user_otp == request.session.get("otp_verifedwokring?"):
            request.session["otp_verifed"] =True
            return redirect("reset_password")
           
        else:
           return render(request, "verify_otp.html", {"error": "Invalid OTP"})

    return render(request, "verify_otp.html")


#reset password

def reset_password(request):

    if not request.session.get("otp_verified"):
        return redirect("send_otp")

    if request.method == "POST":
        new_password = request.POST["newPassword"]
        email = request.session.get("email")

        user = User.objects.get(Email=email)
        user.Password = new_password
        user.save()

        return redirect("register")
    
    return render(request,"reset_password.html")
#########
def terms_conditon(request):
    return render(request, "terms_conditon.html")

def privacy_policy(request):
    return render(request,"privacy_policy.html")

def navbar(request):
    return render(request,"navbar.html")

def example(request):
    return render(request, "example.html")


def your_view(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    return render(request, "your_template.html", {
        "categories": categories,
        "subcategories": subcategories
    })

def footer(request):
    return render(request,"footer.html")

def home(request):                #
    return render(request ,"Home.html")

def aboutus(request):
    return render(request, "aboutUs.html")

def contact(request):

    if request.method =="POST":

        fullname = request.POST["fullname"]
        email = request.POST["email"]
        phonenumber = request.POST["phonenumber"]
        orderid = request.POST["orderid"]
        productname =request.POST["productname"]
        issue_type = request.POST["issue_type"]
        description = request.POST["description"]
        product_image = request.FILES["product_image"]


        Complaint.objects.create(
            Fullname =fullname,
            Email = email,
            Phonenumber = phonenumber,
            Orderid = orderid,
            Productname = productname,
            Issue_type = issue_type,
            Product_image = product_image,
            Description = description
        )

        #confirmation email
        send_mail(
            "Complaint Received",
            f"Hello  {fullname},\n\nYour complaint has been received successfully. Our support team will contact you soon.\n\nThank you,",
            "supoort@yourwebsite.com",
            [email],
            fail_silently=False
        )

        messages.success(request,"Complaint submitted successfully!")

        return redirect("contact")

    return render(request,"contact.html")

########## cart

def cart_view(request):

    cart_items= []
    total_price = 0
    total_items = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)

   

    for item in cart_items:
        total_price += item.product.offer_price * item.quantity
        total_items += item.quantity

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_items": total_items
    }

    return render(request,"cart.html", context)

# add product to cart

def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(
        user= request.user,
        product =product
    )
    if not created:
        cart_item.quantity +=1
        cart_item.save()
    return redirect("cart")

# remove product from cart

def remove_from_cart(request, cart_id):
    item =get_object_or_404(Cart, id=cart_id, user=request.user)
    item.delete()

    return redirect("cart")

# increase_quantity

def increase_quantity(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity < item.product.Quantity: 
        item.quantity +=1
        item.save()

    return redirect("cart")


# decrease_quantity 

def decrease_quantity(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()

    return redirect("Cart")


################
def order_success(request):
    return render(request, "order_success.html")

# wishlist

# add product to wishlist

def add_to_wishlist(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("wishlist")

# wislist page view

def wishlist_view(request):


    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items = []
    context ={
        "wishlist_items": wishlist_items
    }

    return render(request, "wishlist.html",context)

# remove from wishlist

def remove_wishlist(request, wishlist_id):
    item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)

    item.delete()

    return redirect("wishlist")

# move wishlist item to cart

def wishlist_to_cart(request, wishlist_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        id=wishlist_id,
        user =request.user)

    product = wishlist_item.product

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    wishlist_item.delete()

    return redirect("wishlist")
#########

def faq(request):
    return render(request,'faq.html')

def return_refund(request):
    return render(request,"return_refund.html")


def shipping_info(request):
    return render(request,"shipping_info.html")

def my_account(request):

    user_id = request.session.get("user_id")

  

    if not user_id:
        return redirect("register")


    user = User.objects.filter(id=user_id).first()

    if not user:
        request.session.flush()
        return redirect("register")

    if request.method == "POST":

        user.Username = request.POST["username"]
        user.email = request.POST["email"]
        user.phone_number = request.POST["phone_number"] 

        user.save()   


    orders = Order.objects.filter(user=user).order_by("-order_date")[:3]

    address = Address.objects.filter(user =user).first()


    context = {
        "user": user,
        "orders": orders,
        "address": address
    }
    return render(request,"my_account.html", context)

def orders(request):

    user_id = request.session.get("user_id")

    orders = Order.objects.filter(user_id=user_id)

    # STATUS FILTER
    status_list = request.GET.getlist("status")

    if status_list:
        orders = orders.filter(status__in=status_list)

    # LAST  FILTER
    date = request.GET.get("date")
    year = request.GET.get("year")

    context = {
        "orders": orders,
        "status_list": status_list,
        "date": date,
        "year": year,
    }

    return render(request,"order.html", context)

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)


    if order.status != "Delivered":
        order.status = "Cancelled"
        order.save()
    return redirect("orders")

def seller_home(request):
    return render(request,"seller_home.html")



def artisan_register(request):

    message = ""
    show_otp = False
    show_step2 = False

    if request.method == "POST":

        # SEND OTP
        if "send_otp" in request.POST:

            email = request.POST.get("email")

            if Artisan.objects.filter(email=email).exists():
                return render(request, "artisan_register.html", {
                    "message": "Email already registered"
                })

            otp = random.randint(1000,9999)

            request.session["email"] = email
            request.session["email_otp"] = str(otp)

            send_mail(
                "Email Verification OTP",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            print("OTP:", otp)

            return render(request, "artisan_register.html", {
                "show_otp": True,
                "email": email
            })

        # VERIFY OTP
        elif "verify_otp" in request.POST:

            user_otp = request.POST.get("otp")
            saved_otp = request.session.get("email_otp")

            if user_otp == saved_otp:

                return render(request, "artisan_register.html", {
                    "show_step2": True,
                    "email": request.session.get("email")
                })

            else:
                return render(request, "artisan_register.html", {
                    "show_otp": True,
                    "message": "Invalid OTP"
                })

        # FINAL REGISTER
        elif "register" in request.POST:

            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                return render(request, "artisan_register.html", {
                    "show_step2": True,
                    "email": request.session.get("email"),
                    "message": "Passwords do not match"
                })

            Artisan.objects.create(
                name=request.POST.get("name"),
                email=request.session.get("email"),
                password=password,   # simple (no hashing)
                phone=request.POST.get("phone"),
                shop_name=request.POST.get("shop_name"),
                address=request.POST.get("address"),
                city=request.POST.get("city"),
                state=request.POST.get("state"),
                pincode=request.POST.get("pincode"),
            )

            request.session.flush()
            return redirect("artisan_login")

    return render(request, "artisan_register.html")

def artisan_login(request):

    message = ""

    if request.method == "POST":

        email = request.POST["email"]
        password = request.POST["password"]

        try:
            artisan = Artisan.objects.get(email=email,password=password)

            request.session["artisan_id"] = artisan.id

            return redirect("artisan_dashboard")

        except Artisan.DoesNotExist:

            message = "Invalid Email or Password"

    return render(request,"artisan_login.html",{"message":message})

def artisan_dashboard(request):

    total_orders = Order.objects.count()

    pending_orders = Order.objects.filter(status = "Pending").count()

    total_revenue = Order.objects.aggregate(
        total = Sum("total_price")
    )["total"] or 0

    total_products = Product.objects.count()


    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "total_products": total_products
    }

    return render (request, "artisan_dashboard.html", context)

def artisan_products(request):

    artisan_id = request.session.get("artisan_id")

    products = Product.objects.filter(artisan_id=artisan_id)
    categories = Category.objects.all()
    product_types = SubCategory.objects.all()

    return render(request, "artisan_products.html", {"products": products,  "categories": categories,
        "product_types": product_types})


def add_product(request):
    if request.method == "POST":

        product = Product.objects.create(
            artisan=Artisan.objects.get(id=request.session.get("artisan_id")),
            category_id=request.POST.get("category"),
            subcategory_id=request.POST.get("product_type"),
            Product_name=request.POST.get("product_name"),
            Actual_price=request.POST.get("actual_price"),
            Offer_price=request.POST.get("offer_price"),
            Quantity=request.POST.get("quantity"),
            Description=request.POST.get("description"),
        )

        # ✅ SAVE IMAGES CORRECTLY
        if request.FILES.get("front_image"):
            product.front_image = request.FILES.get("front_image")

        if request.FILES.get("left_image"):
            product.left_image = request.FILES.get("left_image")

        if request.FILES.get("right_image"):
            product.right_image = request.FILES.get("right_image")

        if request.FILES.get("back_image"):
            product.back_image = request.FILES.get("back_image")

        product.save()

        return redirect("artisan_products")
    


from transformers import pipeline

generator = pipeline("text-generation", model="distilgpt2")

def generate_description(name, category):

    prompt = f"{name} is a handmade {category} product. It is"

    result = generator(
        prompt,
        max_length=80,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7
    )

    text = result[0]['generated_text']

    # ✅ remove prompt part
    cleaned = text.replace(prompt, "").strip()

    # ✅ final clean format
    return f"""
{name} is a handcrafted {category} product made by skilled artisans.

Material: Natural {category}  
Usage: Home décor / daily use  
Care: Keep in dry conditions  

{cleaned}
"""

# @csrf_exempt
# def generate_description_api(request):
#     try:
#         if request.method == "POST":
#             data = json.loads(request.body)

#             name = data.get("name")
#             category = data.get("category")

#             # safety check
#             if not name or not category:
#                 return JsonResponse({"error": "Missing data"}, status=400)

#             description = generate_description(name, category)

#             return JsonResponse({
#                 "description": description
#             })

#         return JsonResponse({"error": "Invalid request"}, status=400)

#     except Exception as e:
#         print("ERROR:", e)   # debug in terminal
#         return JsonResponse({"error": str(e)}, status=500)



def edit_product(request, id):

    artisan_id = request.session.get("artisan_id")

    product = Product.objects.get(id=id, artisan_id=artisan_id)

    if request.method == "POST":

        product.Product_name = request.POST.get("product_name")
        product.Actual_price = request.POST.get("actual_price")
        product.Offer_price = request.POST.get("offer_price")
        product.Quantity = request.POST.get("quantity")
        product.Description = request.POST.get("description")

        if request.FILES.get("front_image"):
            product.front_image = request.FILES.get("front_image")

        if request.FILES.get("left_image"):
            product.left_image = request.FILES.get("left_image")

        if request.FILES.get("right_image"):
            product.right_image = request.FILES.get("right_image")

        if request.FILES.get("back_image"):
            product.back_image = request.FILES.get("back_image")
        product.save()

        return redirect("artisan_products")

    return render(request, "edit_product.html", {"product": product})



def delete_product(request, id):

    artisan_id = request.session.get("artisan_id")

    product = Product.objects.get(id=id, artisan_id=artisan_id)

    product.delete()

    return redirect("artisan_products")

# CREATE PRODUCT VIEW PAGE
def product_list(request, subcategory_id):
    products = Product.objects.filter(subcategory_id=subcategory_id)
    subcategory = SubCategory.objects.get(id=subcategory_id)


      # ✅ Calculate save amount
    for product in products:
        product.save_amount = product.Actual_price - product.Offer_price

    return render(request, "product_list.html", {
        "products": products,
        "subcategory": subcategory
    })
# product VIEW
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    product.savings = product.Actual_price - product.Offer_price

    return render(request, "product_detail.html", {
        "product": product
    })

def artisan_orders(request):
    artisan_id = request.session.get("artisan_id")

    orders = Order.objects.filter(
        product__artisan_id = artisan_id
    ).order_by("-id")

    context = {
        "orders": orders
    }

    return render(request, "artisan_orders.html",context)


def cancel_order(request, order_id):
    
    artisan_id = request.session.get("artisan_id")

    order = get_object_or_404(
        Order,
        id=order_id,
        product__artisan_id = artisan_id
            
    )

    order.status = "Cancelled"
    order.save()

    return redirect("artisan_orders")





def artisan_profile(request):

    artisan_id = request.session.get("artisan_id")

    # if not artisan_id:
    #     return redirect("artisan_login")
    artisan = Artisan.objects.first()


    # artisan = get_object_or_404(Artisan, id=artisan_id)

    if request.method == "POST":

        artisan.name = request.POST.get("name")
        artisan.email = request.POST.get("email")
        artisan.phone = request.POST.get("phone")

        artisan.shop_name = request.POST.get("shop_name")

        artisan.address = request.POST.get("address")
        artisan.city = request.POST.get("city")
        artisan.state = request.POST.get("state")
        artisan.pincode = request.POST.get("pincode")

        artisan.bio = request.POST.get("bio")

        artisan.bank_account_number = request.POST.get("bank_account_number")
        artisan.ifsc_code = request.POST.get("ifsc_code")

        if request.FILES.get("profile_image"):
            artisan.profile_image = request.FILES.get("profile_image")

        artisan.save()

        return redirect("artisan_profile")

    context = {
        "artisan": artisan
    }

    return render(request, "artisan_profile.html", context)

def artisan_logout(request):

    if "artisan_id" in request.session:
        del request.session["artisan_id"]

    return redirect("artisan_login")

def change_password(request):
    return render(request, "change_password.html")

def address(request):
    return render(request, "address.html")

def logout_view(request):
    request.session.flush()
    return redirect("/")


from .models import Category

def home(request):
    categories = Category.objects.all()
    return render(request, "home.html", {"categories": categories})