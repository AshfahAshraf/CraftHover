from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password

from django.core.mail import send_mail
import random
import time

from user.models import *
from admin_app.models import AdminUser
from .models import Artisan
# admin login

def login_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        #  Check username exists
        try:
            user = AdminUser.objects.get(username=username)
        except AdminUser.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'Username does not exist'
            })

        #  Check password
        if user.password != password:
            return render(request, 'login.html', {
                'error': 'Password does not match'
            })

        #  Login success
        request.session['admin_id'] = user.id
        return redirect('admin_dashboard')

    return render(request, 'login.html')

#admin logout

def logout_admin(request):
    request.session.flush()
    return redirect('login_admin')

#admin forget password

def admin_send_otp(request):

    if request.method == "POST":
        email = request.POST.get("email")

        # check admin email
        if not AdminUser.objects.filter(email=email).exists():
            return render(request, "admin_send_otp.html", {
                "error": "Email not registered"
            })

        otp = str(random.randint(100000, 999999))

        # store session
        request.session['admin_email'] = email
        request.session['admin_otp'] = otp
        request.session['admin_otp_time'] = time.time()

        send_mail(
            "Admin Password Reset - CraftHover",
            f"Your OTP is: {otp}",
            "yourgmail@gmail.com",
            [email],
            fail_silently=False,
        )

        return redirect("admin_verify_otp")

    return render(request, "admin_send_otp.html")


def admin_verify_otp(request):

    if request.method == "POST":
        user_otp = request.POST.get("otp")
        saved_otp = request.session.get("admin_otp")
        otp_time = request.session.get("admin_otp_time")

        # expiry check (2 min)
        if otp_time and (time.time() - otp_time > 120):
            return render(request, "admin_verify.html", {
                "error": "OTP expired"
            })

        if user_otp == saved_otp:
            request.session["admin_otp_verified"] = True
            return redirect("admin_reset_password")

        else:
            return render(request, "admin_verify.html", {
                "error": "Invalid OTP"
            })

    return render(request, "admin_verify.html")


def admin_reset_password(request):

    if not request.session.get("admin_otp_verified"):
        return redirect("admin_send_otp")

    if request.method == "POST":
        new_password = request.POST.get("newPassword")
        email = request.session.get("admin_email")

        admin = AdminUser.objects.get(email=email)

        # plain password (as you want)
        admin.password = new_password
        admin.save()

        # clear session
        request.session.flush()

        return redirect("login_admin")

  
    return render(request, "admin_reset.html")

#admin dashboard

def dashboard(request):
    if not request.session.get('admin_id'):
        return redirect('login_admin')

    categories = Category.objects.all()
    products = Product.objects.all()

    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_artisans = Artisan.objects.count()

    total_revenue = sum(order.total_price for order in Order.objects.all())

    return render(request, 'dashboard.html', {
        'categories': categories,
        'products': products,
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_artisans': total_artisans,
    })
def add_category(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category_id")
        name = request.POST.get("category_name")
        desc = request.POST.get("category_desc")
        image = request.FILES.get("category_image")
        sub_name = request.POST.get("subcategory_name")

        #  Use existing category OR create new
        if category_id:
            category = Category.objects.get(id=category_id)
        else:
            category = Category.objects.create(
                name=name,
                description=desc,
                image=image
            )

        #  Add subcategory
        if sub_name:
            SubCategory.objects.create(
                name=sub_name,
                category=category
            )

        return redirect('add_category')

    return render(request, 'add_category.html', {
        'categories': categories,
        'subcategories': subcategories
    })

#  EDIT CATEGORY
def edit_category(request, id):
    category = Category.objects.get(id=id)

    if request.method == "POST":
        category.name = request.POST.get('category_name')
        category.description = request.POST.get('category_desc')

        #  IMAGE FIX
        if 'category_image' in request.FILES:
            if category.image:
                category.image.delete()

            category.image = request.FILES['category_image']

        category.save()
        return redirect('add_category')

    return render(request, 'add_category.html', {
        'edit_category': category,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all()
    })

#  EDIT SUBCATEGORY
def edit_subcategory(request, id):
    sub = SubCategory.objects.get(id=id)

    if request.method == "POST":
        sub.name = request.POST.get('subcategory_name')
        sub.save()
        return redirect('add_category')

    return render(request, 'add_category.html', {
        'edit_sub': sub,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all()
    })


#  EDIT SUBCATEGORY
def edit_subcategory(request, id):
    sub = SubCategory.objects.get(id=id)

    if request.method == "POST":
        sub.name = request.POST.get('subcategory_name')
        sub.save()
        return redirect('add_category')

    return render(request, 'add_category.html', {
        'edit_sub': sub,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all()
    })


#  DELETE
def delete_category(request, id):
    category = Category.objects.get(id=id)

    # delete image file also
    if category.image:
        category.image.delete()

    category.delete()
    return redirect('add_category')

def delete_subcategory(request, id):
    SubCategory.objects.get(id=id).delete()
    return redirect('add_category')

# PRODUCT LIST PAGE (your admin page)
def admin_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    product_types = SubCategory.objects.all() 

    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'product_types': product_types
    })


# EDIT PRODUCT
def edit_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return redirect('admin_products')  # or show error page

    categories = Category.objects.all()
    product_types = SubCategory.objects.all()

    if request.method == "POST":
        try:
            product.Product_name = request.POST.get('product_name')
            product.category_id = request.POST.get('category')
            product.subcategory_id = request.POST.get('product_type')
            product.Actual_price = request.POST.get('actual_price')
            product.Offer_price = request.POST.get('offer_price')
            product.Quantity = request.POST.get('quantity')
            product.description = request.POST.get('description')

            # Image update (optional)
            if request.FILES.get('front_image'):
                product.front_image = request.FILES.get('front_image')

            if request.FILES.get('left_image'):
                product.left_image = request.FILES.get('left_image')

            if request.FILES.get('right_image'):
                product.right_image = request.FILES.get('right_image')

            product.save()
            return redirect('admin_products')

        except Exception as e:
            print("Error updating product:", e)

    return render(request, 'edit_product.html', {
        'product': product,
        'categories': categories,
        'product_types': product_types
    })


def delete_product(request, id):
    try:
        product = Product.objects.get(id=id)
        product.delete()
    except Product.DoesNotExist:
        print("Product not found")  # optional

    return redirect('admin_products')

# LIST USERS
def admin_users(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})


# ADD USER
def add_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        User.objects.create(
            Username=username,
            Email=email,
            Password=password
        )

    return redirect('admin_users')


# EDIT USER
def edit_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return redirect('admin_users')

    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')

        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))

        user.save()
        return redirect('admin_users')

    return render(request, 'edit_user.html', {'user': user})

# DELETE USER
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return redirect('admin_users')

    user.delete()
    return redirect('admin_users')

# LIST ARTISANS
def admin_artisans(request):
    artisans = Artisan.objects.all()
    return render(request, 'artisans.html', {'artisans': artisans})


# ADD ARTISAN 
def add_artisan(request):
    artisans = Artisan.objects.all()

    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        #  EMAIL DUPLICATE CHECK
        if Artisan.objects.filter(email=email).exists():
            return render(request, "artisans.html", {
                "artisans": artisans,
                "error": "Email already exists!",
                "old": request.POST,
                "open_modal": True
            })

        # PHONE VALIDATION (10 digits only)
        if phone:
            if (not phone.isdigit()) or len(phone) != 10:
                return render(request, "artisans.html", {
                    "artisans": artisans,
                    "error": "Phone must be exactly 10 digits!",
                    "old": request.POST,
                    "open_modal": True
                })

        try:
            Artisan.objects.create(
                name=request.POST.get("name"),
                email=email,
                password=make_password(request.POST.get("password")),
                phone=phone,
                shop_name=request.POST.get("shop_name"),
                address=request.POST.get("address"),
                city=request.POST.get("city"),
                state=request.POST.get("state"),
                pincode=request.POST.get("pincode"),
            )
            return redirect('admin_artisans')

        except IntegrityError:
            return render(request, "artisans.html", {
                "artisans": artisans,
                "error": "Email already exists!",
                "old": request.POST,
                "open_modal": True
            })

    return redirect('admin_artisans')
# EDIT ARTISAN 
def edit_artisan(request, id):
    artisan = Artisan.objects.filter(id=id).first()

    if not artisan:
        return redirect('admin_artisans')

    if request.method == "POST":
        artisan.name = request.POST.get("name")
        artisan.phone = request.POST.get("phone")
        artisan.shop_name = request.POST.get("shop_name")
        artisan.address = request.POST.get("address")
        artisan.city = request.POST.get("city")
        artisan.state = request.POST.get("state")
        artisan.pincode = request.POST.get("pincode")

        if request.POST.get("password"):
            artisan.password = make_password(request.POST.get("password"))

        artisan.save()
        return redirect('admin_artisans')

    return render(request, 'edit_artisan.html', {'artisan': artisan})


# DELETE ARTISAN 
def delete_artisan(request, id):
    artisan = Artisan.objects.filter(id=id).first()

    if artisan:
        artisan.delete()

    return redirect('admin_artisans')


# LIVE EMAIL CHECK 
def check_email(request):
    email = request.GET.get("email")
    exists = Artisan.objects.filter(email=email).exists()
    return JsonResponse({"exists": exists})