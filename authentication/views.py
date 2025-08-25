from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from main.error import exception
from profiles.models import Address
from products.models import Product, Category
from .models import CustomUser
from django.contrib import messages
from .models import EmailTemplate, EmailConstants
from django.core.mail import EmailMultiAlternatives

from .utils import generate_otp, mailer
from orders.models import Order
from django.core.paginator import Paginator


@login_required
def user_home_view(request, user_id):

    try:
        user = CustomUser.objects.filter(pk=user_id).first()
        if user is None:
            messages.error(request, "User not found")
            return redirect("home")
        else:
            match user.role:
                case 1:
                    return redirect("/admin/")
                case 2:
                    return redirect("deliverymanager_dashboard")
                case 3:
                    return redirect("seller_dashboard")
                case 4:
                    return redirect("customer_dashboard")
                case _:
                    messages.error(request, "invalid user role")
                    return redirect("home")

    except Exception as e:
        return exception(request, exception=e, exception_view="user_home_view")


def register_view(request):
    try:
        if request.method == "GET":
            return render(request, "auth/Register.html")

        data = request.POST

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone_no = data.get("phone_no")
        password = data.get("password")
        confrim_password = data.get("confirmpassword")
        role = data.get("role")

        match role:
            case "customer":
                role = CustomUser.CUSTOMER
            case "seller":
                role = CustomUser.SELLER
            case "delivery_manager":
                role = CustomUser.DELIVERY_MANAGER
            case _:
                messages.warning(request, "Invalid Role")
                return redirect("register")

        if password != confrim_password:
            messages.warning(request, "Password and Confirm Password must be same")
            return redirect("register")

        is_unverfied_user = CustomUser.objects.filter(email=email).first()

        if is_unverfied_user is not None and is_unverfied_user.is_verified == False:
            otp = generate_otp()

            template_obj = EmailTemplate.objects.get(
                identifier=EmailConstants.REGISTRATION_OTP
            )
            email_body = template_obj.template.format(
                app_name="CUBEXO SOFTWARE SOLUTIONS",
                username=first_name,
                otp=otp,
                app_contact_url="https://cubexo.io/Contactus",
            )
            mailer(template_obj.subject, email_body, [email])

            is_unverfied_user.otp = otp
            is_unverfied_user.save()
            context = {"email": email, "user_id": is_unverfied_user.pk}
            print("Unverified User")
            return render(request, "auth/OTPPage.html", context=context)

        if is_unverfied_user is not None and is_unverfied_user.is_verified == True:
            messages.warning(request, f"Email has been already taken")
            return redirect("register")
        else:
            otp = generate_otp()

            template_obj = EmailTemplate.objects.get(
                identifier=EmailConstants.REGISTRATION_OTP
            )
            email_body = template_obj.template.format(
                app_name="CUBEXO SOFTWARE SOLUTIONS",
                username=first_name,
                otp=otp,
                app_contact_url="https://cubexo.io/Contactus",
            )
            mailer(template_obj.subject, email_body, [email])

            print("new user")
            user = CustomUser.objects.create_user(
                first_name, last_name, email, phone_no, role, password
            )
            user.otp = otp
            user.is_verified = False
            user.save()

        context = {"email": email, "user_id": user.pk}

        return render(request, "auth/OTPPage.html", context=context)
    except Exception as e:
        return exception(
            request, exception=e, exception_view="register_view", redirect_to="register"
        )


def verify_otp_view(request, user_id):
    try:
        if request.method == "GET":
            return render(request, "OTPPage.html")

        user = CustomUser.objects.get(pk=user_id)
        otp = request.POST.get("otp")
        if user.otp == otp:

            template_obj = EmailTemplate.objects.get(
                identifier=EmailConstants.REGISTRATION_CONFIRMATION
            )
            email_body = template_obj.template.format(
                app_contact_url="https://cubexo.io/Contactus",
                login_url="http://127.0.0.1:8000/auth/login",
                app_name="CUBEXO SOFTWARE SOLUTIONS",
                username=user.first_name,
            )

            mailer(template_obj.subject, email_body, [user.email])

            user.is_verified = True
            user.save()
            return redirect("login")

        messages.warning(request, "Enter Correct OTP")
        context = {"email": user.email, "user_id": user.pk}
        return render(request, "OTPPage.html", context=context)
    except Exception as e:
        return exception(
            request,
            exception=e,
            exception_view="verify_otp_view",
            redirect_to="register",
        )


def login_view(request):
    try:
        if request.user.is_authenticated:
            redirect("home")

        if request.method == "GET":
            return render(request, "auth/Login.html")

        data = request.POST

        email = data.get("email")
        password = data.get("password")

        existing_user = CustomUser.objects.filter(email=email).first()

        if existing_user is None:
            messages.warning(request, f"User not exist using this {email}")
            return redirect("login")
        elif existing_user.is_verified == False and not existing_user.role == 1:
            otp = generate_otp()
            existing_user.otp = otp
            existing_user.save()
            context = {"email": email, "user_id": existing_user.pk}
            return render(request, "auth/OTPPage.html", context=context)

        # for delivery manager admin approval is required
        if existing_user.is_active == False:
            messages.warning(request, "Wait for admin approval")
            return redirect("login")

        authenticated_user = authenticate(request, username=email, password=password)

        if authenticated_user is None:
            messages.error(request, "Invalid Credentials")
            return redirect("login")

        login(request, authenticated_user)

        context = {"user": existing_user}

        match existing_user.role:
            case 1:
                return redirect("/admin/")
            case 2:
                dashboard = "deliverymanager_dashboard"
            case 3:
                dashboard = "seller_dashboard"
            case 4:
                dashboard = "customer_dashboard"
            case _:
                dashboard = "home"

        return redirect(dashboard)
    except Exception as e:
        return exception(
            request, exception=e, exception_view="login_view", redirect_to="login"
        )


def logout_view(request):
    try:
        logout(request)
        return redirect("home")
    except Exception as e:
        return exception(request, exception=e, exception_view="logout_view")


def reset_password_view(request):
    try:

        if request.method == "GET":
            return render(request, "auth/ResetPassword.html")

        data = request.POST
        email = data.get("email")

        existing_user = CustomUser.objects.filter(email=email).first()

        if existing_user is not None:
            if existing_user.is_verified == False:
                messages.warning(
                    request, f"Please complete the registration process first {email}"
                )
                return redirect("register")

            otp = generate_otp()

            template_obj = EmailTemplate.objects.get(
                identifier=EmailConstants.RESET_PASSWORD_OTP
            )
            email_body = template_obj.template.format(
                app_contact_url="https://cubexo.io/Contactus",
                app_name="CUBEXO SOFTWARE SOLUTIONS",
                username=existing_user.first_name,
                otp=otp,
            )

            mailer(template_obj.subject, email_body, [existing_user.email])

            existing_user.otp = otp
            existing_user.save()
            context = {"email": email, "user_id": existing_user.pk}
            return render(request, "auth/ResetPasswordOTPPage.html", context=context)
        else:
            messages.warning(request, f"User not exist with email {email}")
            return redirect("reset-password")

    except Exception as e:
        return exception(request, exception=e, exception_view="reset_password_view")


def verify_reset_password_otp(request, user_id):
    try:
        if request.method == "GET":
            return render(request, "auth/ResetPasswordOTPPage.html")

        user = CustomUser.objects.filter(id=user_id).first()
        if user is not None:
            otp = request.POST.get("otp")
            if user.otp == otp:
                context = {"user_id": user.pk}
                return render(request, "auth/NewPasswordPage.html", context=context)

            else:
                messages.warning(request, "Enter Correct OTP")
                context = {"email": user.email, "user_id": user.pk}
                return render(
                    request, "auth/ResetPasswordOTPPage.html", context=context
                )
        else:
            return render(request, "auth/OTPPage.html")

    except Exception as e:
        return exception(
            request, exception=e, exception_view="verify_reset_password_otp"
        )


def update_password_view(request, user_id):

    try:
        user = CustomUser.objects.filter(id=user_id).first()
        context = {"user_id": user_id}

        if request.method == "GET":
            return render(request, "auth/NewPasswordPage.html", context=context)
        else:
            data = request.POST
            password = data.get("password")
            confrim_password = data.get("confirmpassword")

            if password != confrim_password:
                messages.warning(request, "Password and Confirm Password must be same")
                return render(request, "auth/NewPasswordPage.html", context=context)

            if user is not None:
                user.set_password(password)
                user.save()

                template_obj = EmailTemplate.objects.get(
                    identifier=EmailConstants.RESET_PASSWORD
                )
                email_body = template_obj.template.format(
                    app_contact_url="https://cubexo.io/Contactus",
                    login_url="http://127.0.0.1:8000/auth/login",
                    app_name="CUBEXO SOFTWARE SOLUTIONS",
                    username=user.first_name,
                )

                mailer(template_obj.subject, email_body, [user.email])

                messages.success(request, "Password Reset successfully")
                return redirect("login")
            else:
                messages.warning(request, "User not exist")
                return render(request, "auth/NewPasswordPage.html", context=context)
    except Exception as e:
        return exception(request, exception=e, exception_view="update_password_view")


@login_required(login_url="login")
def delivery_manager_dashboard_view(request):
    try:
        id = request.user.id
        user = CustomUser.objects.filter(pk=id).first()
        orders = Order.objects.all()
        categories = Category.objects.all()
        context = {"user": user, "orders": orders, "categories": categories}
        return render(request, "dashboards/delivery_manager.html", context=context)
    except Exception as e:
        return exception(
            request, exception=e, exception_view="delivery_manager_dashboard_view"
        )


@login_required(login_url="login")
def seller_dashboard_view(request):
    try:
        id = request.user.id
        user = CustomUser.objects.filter(pk=id).first()
        products = Product.objects.filter(seller=id)
        categories = Category.objects.all()
        paginator = Paginator(products, 3)
        page = request.GET.get("page")
        products = paginator.get_page(page)
        context = {"user": user, "products": products, "categories": categories}
        return render(request, "dashboards/seller.html", context=context)
    except Exception as e:
        return exception(
            request, exception=e, exception_view="delivery_manager_dashboard_view"
        )


@login_required(login_url="login")
def customer_dashboard_view(request):
    try:
        # query = request.GET['search']
        id = request.user.id
        user = CustomUser.objects.filter(pk=id).first()
        products = Product.objects.all()
        addresses = Address.objects.filter(user=user)
        paginator = Paginator(products, 3)
        page = request.GET.get("page")
        products = paginator.get_page(page)

        categories = Category.objects.all()
        context = {
            "user": user,
            "products": products,
            "categories": categories,
            "addresses": addresses,
        }
        return render(request, "dashboards/customer.html", context=context)
    except Exception as e:
        return exception(request, exception=e, exception_view="customer_dashboard_view")
