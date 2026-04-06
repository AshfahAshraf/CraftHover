from django.shortcuts import render, redirect, get_object_or_404
from user.models import *
import random
from django.core.mail import send_mail
from admin_app.models import AdminUser
import time


def login_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 🔹 Check username exists
        try:
            user = AdminUser.objects.get(username=username)
        except AdminUser.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'Username does not exist'
            })

        # 🔹 Check password
        if user.password != password:
            return render(request, 'login.html', {
                'error': 'Password does not match'
            })

        # 🔹 Login success
        request.session['admin_id'] = user.id
        return redirect('admin_dashboard')

    return render(request, 'login.html')

def logout_admin(request):
    request.session.flush()
    return redirect('login_admin')




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



def dashboard(request):
    if not request.session.get('admin_id'):
        return redirect('login_admin')

    categories = Category.objects.all()
    products = Product.objects.all()

    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()

    total_revenue = sum(order.total_price for order in Order.objects.all())

    return render(request, 'dashboard.html', {
        'categories': categories,
        'products': products,
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue
    })

def add_category(request):
    if request.method == "POST":

        category_id = request.POST.get('category_id')
        category_name = request.POST.get('category_name')
        subcategory_name = request.POST.get('subcategory_name')

        category = None

        # ✅ If existing category selected
        if category_id:
            category = Category.objects.get(id=category_id)

        # ✅ Else check/create category (NO DUPLICATE)
        elif category_name:
            category = Category.objects.filter(name=category_name).first()

            if not category:
                category = Category.objects.create(name=category_name)

        # ✅ Add subcategory
        if category and subcategory_name:
            SubCategory.objects.create(
                name=subcategory_name,
                category=category
            )

        return redirect('add_category')

    return render(request, 'add_category.html', {
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all()
    })


# ✅ EDIT CATEGORY
def edit_category(request, id):
    category = Category.objects.get(id=id)

    if request.method == "POST":
        category.name = request.POST.get('category_name')
        category.save()
        return redirect('add_category')

    return render(request, 'add_category.html', {
        'edit_category': category,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all()
    })


# ✅ EDIT SUBCATEGORY
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


# ✅ DELETE
def delete_category(request, id):
    Category.objects.get(id=id).delete()
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
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    product_types = SubCategory.objects.all() 

    if request.method == "POST":
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

    return render(request, 'edit_product.html', {
        'product': product,
        'categories': categories,
        'product_types': product_types
    })




def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
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

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

    return redirect('admin_users')


# EDIT USER
def edit_user(request, id):
    user = get_object_or_404(User, id=id)

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
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('admin_users')



# LIST ARTISANS
def admin_artisans(request):
    artisans = Artisan.objects.all()
    return render(request, 'artisans.html', {'artisans': artisans})


# ADD ARTISAN (PLAIN PASSWORD)
def add_artisan(request):
    if request.method == "POST":

        Artisan.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            password=request.POST.get("password"),   # ✅ plain password
            phone=request.POST.get("phone"),
            shop_name=request.POST.get("shop_name"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
        )

    return redirect('admin_artisans')


# EDIT ARTISAN
def edit_artisan(request, id):
    artisan = get_object_or_404(Artisan, id=id)

    if request.method == "POST":
        artisan.name = request.POST.get("name")
        artisan.phone = request.POST.get("phone")
        artisan.shop_name = request.POST.get("shop_name")
        artisan.address = request.POST.get("address")
        artisan.city = request.POST.get("city")
        artisan.state = request.POST.get("state")
        artisan.pincode = request.POST.get("pincode")

        # update password if entered
        if request.POST.get("password"):
            artisan.password = request.POST.get("password")

        artisan.save()
        return redirect('admin_artisans')

    return render(request, 'edit_artisan.html', {'artisan': artisan})


# DELETE ARTISAN
def delete_artisan(request, id):
    artisan = get_object_or_404(Artisan, id=id)
    artisan.delete()
    return redirect('admin_artisans')