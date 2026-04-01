from django.shortcuts import render,redirect,get_object_or_404
from .models import * 
from django.db.models import Q ,Sum
from django.conf import settings
import random
from django.core.mail import send_mail
from django.contrib import messages
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.ai_description import generate_description
# Create your views here.


def index(request):

    if request.method == 'POST':

        if "register" in request.POST:
            username = request.POST.get("textUsername")
            email = request.POST.get("textEmail")
            password = request.POST.get("textPassword")
            confirm_password = request.POST.get("textConfirmPassword")

            if password != confirm_password:
                print("passwords do not match")
                return render(request, "register.html")

            #  CHECK EMAIL EXISTS
            if User.objects.filter(Email=email).exists():
                print("Email already exists")
                return render(request, "register.html", {
                    "error": "Email already registered"
                })

            reg = User(
                Username=username,
                Email=email,
                Password=password
            )
            reg.save()

        #LOGIN

        elif "login" in request.POST:
                email = request.POST.get("textEmail")
                password = request.POST.get("textPassword")

                try:
                    user = User.objects.get(
                        Email=email,
                        Password=password
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
        user_otp = request.POST.get("otp")
        saved_otp = request.session.get("otp")

        if user_otp == saved_otp:
            request.session["otp_verified"] = True   # correct key
            return redirect("reset_password")

        else:
            return render(request, "verify_otp.html", {
                "error": "Invalid OTP"
            })

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
    return render(request,"terms_conditon.html")

def privacy_policy(request):
    return render(request,"privacy_policy.html")

def navbar(request):
    return render(request,"navbar.html")


def search(request):
    # q usually stands for query
    # It’s a common convention for search inputs
    query = request.GET.get('q')

    categories = []
    products = []

    if query:
        categories = Category.objects.filter(name__icontains=query)

        products = Product.objects.filter(
            Q(Product_name__icontains=query) |
            Q(subcategory__name__icontains=query) |
            Q(category__name__icontains=query)
        )

    
        for product in products:
            if product.Actual_price and product.Offer_price:
                product.save_amount = product.Actual_price - product.Offer_price
            else:
                product.save_amount = 0

    return render(request, "search_results.html", {
        "query": query,
        "categories_result": categories,
        "products": products,
        "categories": Category.objects.all()
    })


def your_view(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    return render(request, "your_template.html", {
        "categories": categories,
        "subcategories": subcategories
    })

def footer(request):
    return render(request,"footer.html")

def aboutus(request):
    return render(request, "aboutUs.html")


# Contact Page

def contact(request):

    if request.method == "POST":

        fullname = request.POST["fullname"]
        email = request.POST["email"]
        phonenumber = request.POST["phonenumber"]
        orderid = request.POST["orderid"]
        issue_type = request.POST["issue_type"]
        description = request.POST["description"]
        product_image = request.FILES["product_image"]

        order = get_object_or_404(Order, id=orderid)
        product = order.product

        Complaint.objects.create(
            Fullname=fullname,
            Email=email,
            Phonenumber=phonenumber,
            Orderid=order,
            Productname=product,
            Issue_type=issue_type,
            Product_image=product_image,
            Description=description
        )

        #  SEND EMAIL
        send_mail(
            "Complaint Received",  # Email Subject
            #f - string (dynamic values)
            f"""
                Hello {fullname},

                Your complaint has been received successfully.

                Order ID: {order.id}
                Product: {product.Product_name}
                Issue: {issue_type}

                We will contact you soon.

                Thank you,
                CraftHover Support
                """,
                    settings.EMAIL_HOST_USER,   #  sender
                    [email],                   #  receiver
                    fail_silently=False         # If email fails →  Error will be shown
                )

        messages.success(request, "Complaint submitted successfully!")  #messages- Django message framework

        return redirect("contact")  # Prevents form resubmission on refresh

    return render(request, "contact.html")  # show HTML page


#### wishlist
# adding wishlist
# It works like a  button (toggle) on your website

# Click once → Add to wishlist
# Click again → Remove from wishlist

def add_to_wishlist(request, product_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "login required"}, status=403)

    item = Wishlist.objects.filter(
        user_id=user_id,
        product_id=product_id
    ).first()

    if item:
        item.delete()
        return JsonResponse({"status": "removed"})
    else:
        Wishlist.objects.create(
            user_id=user_id,
            product_id=product_id
        )
        return JsonResponse({"status": "added"})
    
# wislist page view 
# It shows the logged-in user’s wishlist page

def wishlist_view(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    wishlist_items = Wishlist.objects.filter(user_id=user_id)

    return render(request, "wishlist.html", {
        "wishlist_items": wishlist_items
    })

#  deleteing from wislist section

def remove_wishlist(request, wishlist_id):

    user_id = request.session.get("user_id")

    item = get_object_or_404(Wishlist, id=wishlist_id, user_id=user_id)
    item.delete()

    return redirect("wishlist")

# move wishlist item to cart

def wishlist_to_cart(request, wishlist_id):

    user_id = request.session.get("user_id")

    user = get_object_or_404(User, id=user_id)

    wishlist_item = get_object_or_404(
        Wishlist,
        id=wishlist_id,
        user_id=user_id
    )

    product = wishlist_item.product

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    wishlist_item.delete()

    return redirect("wishlist")

#########

# cart

# add product to cart

def add_to_cart(request, product_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")
   
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user_id= user_id,
        product =product
    )
    if not created:
        cart_item.quantity +=1
        cart_item.save()

    return redirect("cart")

# cart page view

def cart_view(request):

    user_id = request.session.get("user_id")

    cart_items = []
    total_price = 0
    total_items = 0

    if user_id:
        cart_items = Cart.objects.filter(user_id=user_id)

    for item in cart_items:
        item.total = item.product.Offer_price * item.quantity
        total_price += item.total
        total_items += item.quantity

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_items": total_items
    }

    return render(request, "cart.html", context)


# remove product from cart

def remove_from_cart(request, cart_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    item = get_object_or_404(Cart, id=cart_id, user_id=user_id)
    item.delete()

    return redirect("cart")

# increase_quantity product in the cart

def increase_quantity(request, cart_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    item = get_object_or_404(Cart, id=cart_id, user_id=user_id)

    if item.quantity < item.product.Quantity:
        item.quantity += 1
        item.save()

    return redirect("cart")


# decrease_quantity  product in the cart

def decrease_quantity(request, cart_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    item = get_object_or_404(Cart, id=cart_id, user_id=user_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")


################

# orderss

def orders(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")
    # Sorts orders in descending order
    # Latest order comes first
    orders = Order.objects.filter(user_id=user_id).order_by("-id")

    context = {
        "orders": orders,
    }

    return render(request,"order.html", context)

# cancelling the order

def cancel_order(request, order_id):

    if request.method == "POST":

        order = get_object_or_404(
            Order,
            id=order_id,
            user_id=request.session.get("user_id")  
        )

        if order.status not in ["Delivered", "Cancelled"]:
            order.status = "Cancelled"
            order.save()

    return redirect("order")


#  PLACE ORDER
def place_order(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    user = User.objects.get(id=user_id)

    if request.method == "POST":

        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return redirect("cart")

        shipping_cost = int(request.POST.get("shipping_cost") or 0)

        total_price = 0
        for item in cart_items:
            total_price += item.product.Offer_price * item.quantity

        final_price = total_price + shipping_cost
        # CREATE ORDER FOR EACH ITEM
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,       
                quantity=item.quantity,      
                total_price=item.product.Offer_price * item.quantity,  #  per item price
                final_price=final_price, 
                status="Pending"
            )

        cart_items.delete()

        return redirect("order_success")

    return redirect("cart")

#####
# after place order then it order sucess page

def order_success(request):
    return render(request, "order_success.html")

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

        #  UPDATE PROFILE
        if "username" in request.POST:

            user.Username = request.POST.get("username", user.Username)
            user.Email = request.POST.get("email", user.Email)
            user.Phone_Number = request.POST.get("phone_number", user.Phone_Number)

            user.save()

        #  UPLOAD IMAGE
        elif "upload_image" in request.POST:
            if request.FILES.get("profile_image"):
                user.profile_image = request.FILES.get("profile_image")
                user.save()

        #  REMOVE IMAGE
        elif "remove_image" in request.POST:
            user.profile_image = None
            user.save()

        #  ADD ADDRESS
        elif "full_name" in request.POST and "address_id" not in request.POST:
            Address.objects.create(
                user=user,
                full_name=request.POST.get("full_name"),
                street=request.POST.get("street"),
                city=request.POST.get("city"),
                state=request.POST.get("state"),
                pincode=request.POST.get("pincode"),
                phone=request.POST.get("phone"),
            )

        #  DELETE ADDRESS
        elif "delete_address_id" in request.POST:
            address_id = request.POST.get("delete_address_id")
            Address.objects.filter(id=address_id, user=user).delete()

        #  UPDATE ADDRESS
        elif "update_address" in request.POST:
            address_id = request.POST.get("address_id")

            address = Address.objects.filter(id=address_id, user=user).first()

            if address:
                address.full_name = request.POST.get("full_name")
                address.street = request.POST.get("street")
                address.city = request.POST.get("city")
                address.state = request.POST.get("state")
                address.pincode = request.POST.get("pincode")
                address.phone = request.POST.get("phone")
                address.save()

    orders = Order.objects.filter(user=user).order_by("-order_date")[:3]
    addresses = Address.objects.filter(user=user)

    return render(request, "my_account.html", {
        "user": user,
        "orders": orders,
        "addresses": addresses
    })


# change password for user

def change_password(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check current password
        if user.Password != current_password:
            messages.error(request, "Current password is incorrect")
            return redirect("change_password")

        # Check new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect("change_password")

        # Change password
        user.Password = new_password
        user.save()

        messages.success(request, "Password changed successfully")
        return redirect("change_password")

    return render(request, "change_password.html")



# Artisan Sections

def seller_home(request):
    return render(request,"seller_home.html")

# Artisan Register page

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
                # If something goes wrong while sending email, show the error.
                fail_silently=False,
            )

            return render(request, "artisan_register.html", {
                "show_otp": True,
                "email": email
            })

        # VERIFY OTP
        elif "verify_otp" in request.POST:
            # what user entered
            user_otp = request.POST.get("otp")
            # what you generated earlier (stored in session)
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
                password=password, 
                phone=request.POST.get("phone"),
                shop_name=request.POST.get("shop_name"),
                address=request.POST.get("address"),
                city=request.POST.get("city"),
                state=request.POST.get("state"),
                pincode=request.POST.get("pincode"),
            )
            # clear everything and send user to login page
            request.session.flush()
            return redirect("artisan_login")

    return render(request, "artisan_register.html")

# Artisan Login

def artisan_login(request):

    message = ""

    if request.method == "POST":

        email = request.POST["email"]
        password = request.POST["password"]

        try:
            artisan = Artisan.objects.get(email=email,password=password)

            # Django gives every user a session (a temporary storage tied to their browser).
            # It works like a dictionary (key-value pair storage).
            request.session["artisan_id"] = artisan.id

            return redirect("artisan_dashboard")

        except Artisan.DoesNotExist:

            message = "Invalid Email or Password"

    return render(request,"artisan_login.html",{"message":message})



def artisan_dashboard(request):

    artisan_id = request.session.get("artisan_id")

    if not artisan_id:
        return redirect("artisan_login")

    #  Gets number of products created by this artisan
    total_products = Product.objects.filter(artisan_id=artisan_id).count()

    # Gets all orders related to this artisan’s products
    # This is called double underscore (__) lookup
    # Go through relationships
    # product → from Order → Product
    # artisan_id → from Product → Artisan ID
    # Get all orders where
    # the product’s artisan_id = logged-in artisan_id

    orders = Order.objects.filter(product__artisan_id=artisan_id)

    total_orders = orders.count()

    pending_orders = orders.filter(status="Pending").count()

    #  FIXED REVENUE LOGIC

    SUCCESS_STATUSES = ["Shipped", "Delivered", "Completed"]
        #pending will not calculate in the revenue
        # Find all successful orders and calculate total revenue.
        # If no orders, return 0
    total_revenue = orders.filter(
        status__in=SUCCESS_STATUSES
    ).aggregate(
        total=Sum("total_price")
    )["total"] or 0

    # Left = name used in template
    # Right = actual data/value
    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "total_products": total_products
    }

    return render(request, "artisan_dashboard.html", context)

# aritsan Product display

def artisan_products(request):

    artisan_id = request.session.get("artisan_id")

    # Fetches only products belonging to that artisan
    products = Product.objects.filter(artisan_id=artisan_id)
    categories = Category.objects.all()
    product_types = SubCategory.objects.all()

    return render(request, "artisan_products.html", {"products": products,  "categories": categories,
        "product_types": product_types})

# adding artisan products in artisan page

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

        #  SAVE IMAGES CORRECTLY
        if request.FILES.get("front_image"):
            product.front_image = request.FILES.get("front_image")

        if request.FILES.get("left_image"):
            product.left_image = request.FILES.get("left_image")

        if request.FILES.get("right_image"):
            product.right_image = request.FILES.get("right_image")

        product.save()

        return redirect("artisan_products")
    
# in the add product we using ai generate description 
# It is an API that generates product description and returns it.

@csrf_exempt
def generate_description_api(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)

            name = data.get("name")
            category = data.get("category")
            product_type = data.get("product_type")

            # safety check
            if not name or not category or not product_type:
                return JsonResponse({"error": "Missing data"}, status=400)

            description = generate_description(name, category, product_type)

            return JsonResponse({
                "description": description
            })

        return JsonResponse({"error": "Invalid request"}, status=400)

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

# eidting the product in the artisan section 

def Artisan_edit_product(request, id):

    artisan_id = request.session.get("artisan_id")

    if not artisan_id:
        return redirect("login")

    product = get_object_or_404(Product, id=id, artisan_id=artisan_id)

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

        product.save()

        return redirect("artisan_products")

    return render(request, "Artisan_edit_product.html", {"product": product})



def delete_product(request, id):

    artisan_id = request.session.get("artisan_id")

     #  Check login
    if not artisan_id:
        return redirect("login")


     #  Allow only POST (security)
    if request.method == "POST":
        product = get_object_or_404(Product, id=id, artisan_id=artisan_id)
        product.delete()

    return redirect("artisan_products")

# artisan order control section

def artisan_orders(request):
    artisan_id = request.session.get("artisan_id")

    if not artisan_id:
        return redirect("login")

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        action = request.POST.get("action")

        order = get_object_or_404(
            Order,
            id=order_id,
            product__artisan_id=artisan_id
        )

        if action == "ship" and order.status == "Pending":
            order.status = "Shipped"
            messages.success(request, "Order shipped successfully")


        elif action == "deliver" and order.status == "Shipped":
            order.status = "Delivered"
            messages.success(request, "Order delivered successfully")


        elif action == "cancel" and order.status not in ["Delivered", "Cancelled"]:
            order.status = "Cancelled"
            messages.success(request, "Order cancelled successfully")


        order.save()
        return redirect("artisan_orders")

    #  Show orders
    orders = Order.objects.filter(
        product__artisan_id=artisan_id
    ).order_by("-id")

    return render(request, "artisan_orders.html", {"orders": orders})

# artisan profile management

def artisan_profile(request):

    artisan_id = request.session.get("artisan_id")

    #  Check login
    if not artisan_id:
        return redirect("artisan_login")

    artisan = get_object_or_404(Artisan, id=artisan_id)

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

        #  Image upload
        if request.FILES.get("profile_image"):
            artisan.profile_image = request.FILES.get("profile_image")

        artisan.save()

        #  Success message
        messages.success(request, "Profile updated successfully")

        return redirect("artisan_profile")

    context = {
        "artisan": artisan
    }

    return render(request, "artisan_profile.html", context)

# artisan Logout

def artisan_logout(request):

    if "artisan_id" in request.session:
        del request.session["artisan_id"]

    return redirect("artisan_login")

# PRODUCT list view VIEW PAGE
def product_list(request, subcategory_id):

    products = Product.objects.filter(subcategory_id=subcategory_id)
    subcategory = SubCategory.objects.get(id=subcategory_id)

    user_id = request.session.get("user_id")

    wishlist_products = []

    if user_id:
        wishlist_products = Wishlist.objects.filter(
            user_id=user_id
        ).values_list('product_id', flat=True)

    #  Calculate save amount
    for product in products:
        product.save_amount = product.Actual_price - product.Offer_price

    return render(request, "product_list.html", {
        "products": products,
        "subcategory": subcategory,
        "wishlist_products": wishlist_products  
    })

# product detail VIEW
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    product.savings = product.Actual_price - product.Offer_price

    return render(request, "product_detail.html", {
        "product": product
    })

def address(request):
    return render(request, "address.html")

def logout_view(request):
    request.session.flush()
    return redirect("/")

def home(request):
    categories = Category.objects.all()
    return render(request, "home.html", {"categories": categories})

# show full cateogry

def category_products(request, category_id):

    category = Category.objects.get(id=category_id)

    products = Product.objects.filter(category_id=category_id)

    # Calculate save amount
    for product in products:
        if product.Actual_price and product.Offer_price:
            product.save_amount = product.Actual_price - product.Offer_price
        else:
            product.save_amount = 0

    return render(request, "product_list.html", {
        "products": products,
        "category": category
    })
