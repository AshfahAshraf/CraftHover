import re
import random
import json
import time

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .models import Order, Complaint, User
from .utils.ai_description import generate_description
# Create your views here.



def index(request):

    context = {}

    if request.method == 'POST':

        # ================= REGISTER =================
        if "register" in request.POST:

            username = request.POST.get("textUsername")
            email = request.POST.get("textEmail")
            password = request.POST.get("textPassword")
            confirm_password = request.POST.get("textConfirmPassword")

            # Email validation
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not email or not re.match(email_pattern, email):
                context["register_error"] = "Invalid email format"
                return render(request, "register.html", context)

            # OTP check
            if not request.session.get("signup_verified"):
                context["register_error"] = "Please verify OTP first"
                return render(request, "register.html", context)

            # Password match
            if password != confirm_password:
                context["register_error"] = "Passwords do not match"
                return render(request, "register.html", context)

            # Email exists
            if User.objects.filter(Email=email).exists():
                context["register_error"] = "Email already registered"
                return render(request, "register.html", context)

            # Save user
            User.objects.create(
                Username=username,
                Email=email,
                Password=password
            )

            # clear OTP session
            request.session.pop("signup_verified", None)
            request.session.pop("signup_otp", None)

            context["success"] = "Registration successful"
            return render(request, "register.html", context)


        # ================= LOGIN =================
        elif "login" in request.POST:

            email = request.POST.get("textEmail")
            password = request.POST.get("textPassword")

            try:
                user = User.objects.get(Email=email)

                if user.Password != password:
                    context["login_error"] = "Incorrect password"
                    return render(request, "register.html", context)

                # success
                request.session["user_id"] = user.id
                request.session["user_name"] = user.Username
                request.session["email"] = user.Email

                return redirect("home")

            except User.DoesNotExist:
                context["login_error"] = "Email does not exist"
                return render(request, "register.html", context)

    return render(request, "register.html", context)


# ================= SIGNUP OTP =================

def signup_send_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            return JsonResponse({"status": "error"})

        if User.objects.filter(Email=email).exists():
            return JsonResponse({"status": "exists"})

        otp = str(random.randint(100000, 999999))
        request.session["signup_otp"] = otp

        try:
            send_mail(
                "Your OTP Code",
                f"Your OTP is: {otp}",
                "your_email@gmail.com",  # change this
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print("Email error:", e)
            return JsonResponse({"status": "email_error"})

        return JsonResponse({"status": "success"})


def signup_verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        real_otp = request.session.get("signup_otp")

        if user_otp == real_otp:
            request.session["signup_verified"] = True
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "failed"})
########
#email 

# send otp 
# ================= SEND OTP =================
def send_otp(request, user_type):

    if request.method == "POST":
        email = request.POST.get("email")

        # choose model
        if user_type == "user":
            model = User
        elif user_type == "artisan":
            model = Artisan
        else:
            return redirect("login")

        # check email
        if not model.objects.filter(Email=email).exists():
            return render(request, "send_otp.html", {
                "error": "Email not registered"
            })

        otp = str(random.randint(100000, 999999))

        # store session
        request.session['email'] = email
        request.session['otp'] = otp
        request.session['user_type'] = user_type
        request.session['otp_time'] = time.time()

        send_mail(
            "Reset Your Crafthover Password",
            f"Your OTP is: {otp}",
            "yourgmail@gmail.com",
            [email],
            fail_silently=False,
        )

        return redirect("verify_otp")

    return render(request, "send_otp.html")


# ================= VERIFY OTP =================
def verify_otp(request):

    if request.method == "POST":
        user_otp = request.POST.get("otp")
        saved_otp = request.session.get("otp")
        otp_time = request.session.get("otp_time")

        # check expiry (2 minutes)
        if otp_time and (time.time() - otp_time > 120):
            return render(request, "verify_otp.html", {
                "error": "OTP expired"
            })

        if user_otp == saved_otp:
            request.session["otp_verified"] = True
            return redirect("reset_password")

        else:
            return render(request, "verify_otp.html", {
                "error": "Invalid OTP"
            })

    return render(request, "verify_otp.html")


# ================= RESET PASSWORD =================
def reset_password(request):

    if not request.session.get("otp_verified"):
        return redirect("send_otp", user_type="user")

    if request.method == "POST":
        new_password = request.POST.get("newPassword")
        email = request.session.get("email")
        user_type = request.session.get("user_type")

        # select model
        if user_type == "user":
            user = User.objects.get(Email=email)

        elif user_type == "artisan":
            user = Artisan.objects.get(Email=email)

        else:
            return redirect("login")

        # plain password (as you requested)
        user.Password = new_password
        user.save()

        # clear session
        request.session.flush()

        return redirect("login")

    return render(request, "reset_password.html")

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

def footer(request):
    return render(request,"footer.html")

def aboutus(request):
    return render(request, "aboutUs.html")

# Contact Page

def contact(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    errors = {}

    if request.method == "POST":
        try:
            fullname = request.POST.get("fullname", "").strip()
            email = request.POST.get("email", "").strip()
            phonenumber = request.POST.get("phonenumber", "").strip()
            orderid = request.POST.get("orderid")
            issue_type = request.POST.get("issue_type")
            description = request.POST.get("description", "").strip()
            product_image = request.FILES.get("product_image")

            #  VALIDATIONS
            if not fullname:
                errors["fullname"] = "Full name is required"

            if not email:
                errors["email"] = "Email is required"

            # Phone validation (ONLY 10 digits)
            if not re.fullmatch(r"\d{10}", phonenumber):
                errors["phonenumber"] = "Phone number must be exactly 10 digits"

            if not orderid:
                errors["orderid"] = "Please select an order"

            if not issue_type:
                errors["issue_type"] = "Please select issue type"

            if not description:
                errors["description"] = "Description is required"

            # If errors → show in same page
            if errors:
                orders = Order.objects.filter(
                    user_id=user_id,
                    status="Delivered"
                ).order_by("-id")[:5]

                return render(request, "contact.html", {
                    "orders": orders,
                    "errors": errors,
                    "form_data": request.POST
                })

            #  SAFE ORDER FETCH (instead of get_object_or_404)
            try:
                order = Order.objects.get(
                    id=orderid,
                    user_id=user_id,
                    status="Delivered"
                )
            except Order.DoesNotExist:
                messages.error(request, "Invalid order selected")
                return redirect("contact")

            product = order.product
            artisan = product.artisan

            #  SAVE
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

            #  EMAIL (with try-except)
            try:
                send_mail(
                    "Complaint Received",
                    f"""
                            Hello {fullname},

                            Your complaint has been received successfully.

                            Order ID: {order.id}
                            Product: {product.Product_name}
                            Issue: {issue_type}

                            Our team (artisan: {artisan.name}) will review it soon.

                            Thank you,
                            CraftHover Support
                    """,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )
            except Exception as e:
                print("Email error:", e)

            messages.success(request, "Complaint submitted successfully!")
            return redirect("contact")

        except Exception as e:
            print("Error:", e)
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("contact")

    orders = Order.objects.filter(
        user_id=user_id,
        status="Delivered"
    ).order_by("-id")[:5]

    return render(request, "contact.html", {
        "orders": orders
    })

def artisan_complaints(request):

    artisan_id = request.session.get("artisan_id")

    #  check login
    if not artisan_id:
        return redirect("artisan_login")

    #  get complaints of this artisan
    complaints = Complaint.objects.filter(
        Productname__artisan_id=artisan_id
    ).order_by("-id")

    return render(request, "artisan_complaints.html", {
        "complaints": complaints
    })

def update_complaint(request, id):

    artisan_id = request.session.get("artisan_id")

    try:
        complaint = Complaint.objects.get(
            id=id,
            Productname__artisan_id=artisan_id
        )
    except Complaint.DoesNotExist:
        messages.error(request, "Complaint not found!")
        return redirect("artisan_complaints")

    if request.method == "POST":

        action = request.POST.get("action")

        # ================= RESOLVE =================
        if action == "resolve":

            issue = complaint.Issue_type
            artisan_name = complaint.Productname.artisan.name

            solutions = {
                "Damaged Product": "We sincerely apologize for the inconvenience caused. After reviewing your complaint, we have arranged a replacement for the damaged product. It will be shipped to your address shortly.",
                "Wrong Product Received": "We regret the error in your order. Our team has arranged for the correct product to be delivered to you. The incorrect item may be picked up if required.",
                "Missing Item": "We understand your concern regarding the missing item. After checking your order, we have arranged to send the missing product, which will reach you soon.",
                "Refund Issue": "Your refund request has been successfully processed. The amount will be credited to your original payment method within a few working days.",
                "Delivery Delay": "We apologize for the delay in delivery. Your order has been prioritized and will be delivered to you at the earliest possible time."
            }

            solution_text = solutions.get(issue, "Your issue has been reviewed and resolved successfully.")

            complaint.status = "Resolved"
            complaint.save()

            send_mail(
                "Complaint Resolved",
                f"""
                        Hello {complaint.Fullname},

                        We would like to inform you that your complaint has been carefully reviewed and resolved by our team.

                        Product: {complaint.Productname.Product_name}
                        Issue Reported: {issue}

                        Resolution Details:
                        {solution_text}

                        We truly appreciate your patience and understanding while we worked on your request.

                        Handled by: {artisan_name}

                        Thank you for choosing CraftHover.

                        CraftHover Support
                        """,
                settings.EMAIL_HOST_USER,
                [complaint.Email],
                fail_silently=False
            )

            messages.success(request, "Complaint resolved!")

        # ================= REJECT =================
        elif action == "reject":

            artisan_name = complaint.Productname.artisan.name

            default_reason = "After carefully reviewing your complaint, we found that it does not meet our return or support policy conditions."

            complaint.status = "Rejected"
            complaint.reject_reason = default_reason
            complaint.save()

            send_mail(
                "Complaint Update",
                f"""
                        Hello {complaint.Fullname},

                        Thank you for reaching out to us regarding your concern.

                        After reviewing your complaint, we regret to inform you that we are unable to process your request at this time.

                        Product: {complaint.Productname.Product_name}
                        Issue Reported: {complaint.Issue_type}

                        Reason:
                        {default_reason}

                        Handled by: {artisan_name}

                        If you need further clarification, please contact our support team.

                        We appreciate your understanding.

                        CraftHover Support
                        """,
                settings.EMAIL_HOST_USER,
                [complaint.Email],
                fail_silently=False
            )

            messages.error(request, "Complaint rejected!")

    return redirect("artisan_complaints")
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

    try:
        item = Wishlist.objects.get(id=wishlist_id, user_id=user_id)
        item.delete()
    except Wishlist.DoesNotExist:
        print("Wishlist item not found")
    except Exception as e:
        print("Error:", e)

    return redirect("wishlist")

# move wishlist item to cart

def wishlist_to_cart(request, wishlist_id):

    user_id = request.session.get("user_id")

    try:
        user = User.objects.get(id=user_id)

        wishlist_item = Wishlist.objects.get(
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

    except User.DoesNotExist:
        print("User not found")

    except Wishlist.DoesNotExist:
        print("Wishlist item not found")

    except Exception as e:
        print("Error:", e)

    return redirect("wishlist")

#########

# cart

# add product to cart

from django.shortcuts import render, redirect
from .models import Product, Cart, Address


# ADD TO CART
def add_to_cart(request, product_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect("home")   # or show error page

    cart_item, created = Cart.objects.get_or_create(
        user_id=user_id,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


# CART PAGE
def cart_view(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    cart_items = []
    total_price = 0
    total_items = 0

    try:
        cart_items = Cart.objects.filter(user_id=user_id)
    except Exception:
        cart_items = []

    for item in cart_items:
        item.total = item.product.Offer_price * item.quantity
        total_price += item.total
        total_items += item.quantity

    addresses = Address.objects.filter(user_id=user_id)

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_items": total_items,
        "addresses": addresses
    }

    return render(request, "cart.html", context)


# REMOVE FROM CART
def remove_from_cart(request, cart_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    try:
        item = Cart.objects.get(id=cart_id, user_id=user_id)
        item.delete()
    except Cart.DoesNotExist:
        pass  # silently ignore

    return redirect("cart")


# INCREASE QUANTITY
def increase_quantity(request, cart_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    try:
        item = Cart.objects.get(id=cart_id, user_id=user_id)

        if item.quantity < item.product.Quantity:
            item.quantity += 1
            item.save()

    except Cart.DoesNotExist:
        pass

    return redirect("cart")


# DECREASE QUANTITY
def decrease_quantity(request, cart_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    try:
        item = Cart.objects.get(id=cart_id, user_id=user_id)

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    except Cart.DoesNotExist:
        pass

    return redirect("cart")

# orderss

def orders(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")
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

        try:
            order = Order.objects.get(
                id=order_id,
                user_id=request.session.get("user_id")
            )
        except Order.DoesNotExist:
            return redirect("order")  # or handle error as needed

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
                "Email Verification for Artisan Account",
                f"Dear User,\n\nThank you for registering on our platform.\n\nYour OTP for email verification is: {otp}\n\nPlease enter this OTP to complete your registration. This OTP is valid for 5 minutes.\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nYour Team",
                settings.EMAIL_HOST_USER,
                [email],
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
        return redirect("artisan_login")

    try:
        product = Product.objects.get(id=id, artisan_id=artisan_id)
    except Product.DoesNotExist:
        return redirect("artisan_products")  # or show error page

    # dropdown data
    categories = Category.objects.all()
    product_types = SubCategory.objects.all()

    if request.method == "POST":

        product.Product_name = request.POST.get("product_name")
        product.Actual_price = request.POST.get("actual_price")
        product.Offer_price = request.POST.get("offer_price")
        product.Quantity = request.POST.get("quantity")
        product.Description = request.POST.get("description")

        # category + subcategory
        product.category_id = request.POST.get("category")
        product.subcategory_id = request.POST.get("product_type")

        # images
        if request.FILES.get("front_image"):
            product.front_image = request.FILES.get("front_image")

        if request.FILES.get("left_image"):
            product.left_image = request.FILES.get("left_image")

        if request.FILES.get("right_image"):
            product.right_image = request.FILES.get("right_image")

        product.save()

        return redirect("artisan_products")

    return render(request, "artisan_edit_product.html", {
        "product": product,
        "categories": categories,
        "product_types": product_types
    })
def delete_product(request, id):
    artisan_id = request.session.get("artisan_id")

    #  Check login
    if not artisan_id:
        return redirect("artisan_login")

    #  Allow only POST
    if request.method == "POST":
        try:
            product = Product.objects.get(id=id, artisan_id=artisan_id)
            product.delete()
            messages.success(request, "Product deleted successfully")

        except Product.DoesNotExist:
            messages.error(request, "Product not found or unauthorized")

    return redirect("artisan_products")

# artisan order control section
def artisan_orders(request):
    artisan_id = request.session.get("artisan_id")

    if not artisan_id:
        return redirect("artisan_login")

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        action = request.POST.get("action")

        try:
            order = Order.objects.get(
                id=order_id,
                product__artisan_id=artisan_id
            )
        except Order.DoesNotExist:
            messages.error(request, "Order not found!")
            return redirect("artisan_orders")

        #  STATUS LOGIC
        if action == "ship" and order.status == "Pending":
            order.status = "Shipped"
            messages.success(request, "Order shipped successfully")

        elif action == "deliver" and order.status == "Shipped":
            order.status = "Delivered"
            messages.success(request, "Order delivered successfully")

        elif action == "cancel" and order.status not in ["Delivered", "Cancelled"]:
            order.status = "Cancelled"
            messages.success(request, "Order cancelled successfully")

        else:
            messages.warning(request, "Invalid action!")

        order.save()
        return redirect("artisan_orders")

    #  GET → Show orders
    orders = Order.objects.filter(
        product__artisan_id=artisan_id
    ).order_by("-id")

    return render(request, "artisan_orders.html", {"orders": orders})
# artisan profile management


def artisan_profile(request):

    artisan_id = request.session.get("artisan_id")

    # Check login
    if not artisan_id:
        return redirect("artisan_login")

    try:
        artisan = Artisan.objects.get(id=artisan_id)
    except Artisan.DoesNotExist:
        messages.error(request, "Artisan not found")
        return redirect("artisan_login")

    if request.method == "POST":
        try:
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

            messages.success(request, "Profile updated successfully")
            return redirect("artisan_profile")

        except Exception as e:
            #  Catch unexpected errors
            messages.error(request, f"Something went wrong: {str(e)}")

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

     #  ADD THIS LINE
    if not request.session.get("user_id"):
        return redirect("register")   # go to login/register

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
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect("home")  # or any page you prefer

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

    # find most purchased category
    top_category = Product.objects.values(
        'category'
    ).annotate(
        total=Sum('order__quantity')
    ).order_by('-total').first()

    if top_category:
        trending = Product.objects.filter(
            category_id=top_category['category']
        ).annotate(
            total=Sum('order__quantity')
        ).order_by('-total')[:4]
    else:
        trending = Product.objects.all()[:4]

    return render(request, "home.html", {
        "categories": categories,
        "trending": trending
    })
# show full cateogry

def category_products(request, category_id):

     #  ADD THIS
    if not request.session.get("user_id"):
        return redirect("register")


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



