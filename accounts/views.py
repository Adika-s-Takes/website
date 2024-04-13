from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string, get_template
from django.contrib.auth.models import User, auth
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from .models import ShippingInfo, Country, City
from products.models import Order
import json


def login(request):
    user = request.user

    if user.is_authenticated:
        return redirect('dashboard')

    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())

    context = {
        'title' : 'Login',
        'total_items_in_cart' : total_quantity_in_cart,
    }

    if request.method == 'POST':
        username = request.POST['username'] #Requesting Username
        password = request.POST['password'] #Requesting Password

        user = auth.authenticate(username=username, password=password)

        if user is not None: #Cheking If User Exists in the database
            auth.login(request, user) # Logs in User
            return redirect('dashboard') # Redirects to home view
        else:
            messages.error(request, 'Invalid Username or Password') #Conditional Checking if credentials are correct
            return redirect('login')#Redirects to login if invalid



    else:
        return render(request, 'login.html', context)



def register(request):
    user = request.user

    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())


    if user.is_authenticated:
        return redirect('dashboard')

    context = {
        'title' : 'Sign Up',
        'total_items_in_cart' : total_quantity_in_cart,
    }
    if request.method == 'POST':
        #Requesting POST data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['pass']
        password2 = request.POST['pass2']


        #Condition is executed if both passwords are the same
        if password == password2:
            if User.objects.filter(email=email).exists(): #Checking databse for existing data
                messages.error(request, "This email is already in use")#Returns Error Message
                return redirect(register)
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Username Taken")
                return redirect('register')

            #Else condition executed if the above conditions are not fulfilled
            else:
                ctx = {
                    'user' : username
                }
                message = get_template('mail.html').render(ctx)
                msg = EmailMessage(
                    'Welcome Aboard✌',
                    message,
                    'The Adikastakes Team',
                    [email],
                )
                msg.content_subtype ="html"# Main content is now text/html
                msg.send()
                user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name )
                user.save()
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)#Logs in USER



            #Create user model and redirect to edit-profile
            return redirect('shipping')
        else:
            messages.info(request, "Passwords do not match")
            return redirect("register")

    else:
        return render(request, 'register.html', context)


# from django.http import JsonResponse

@login_required
def shipping(request):
    user = request.user
    countries = Country.objects.all()
    cities_data = []

    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())


    if request.method == "POST":
        house_number = request.POST['house_number']
        street_name = request.POST['street_name']
        phone_number = request.POST['phone_number']
        address = request.POST['address']
        city_id = request.POST['city']  # Assuming 'city' is the ID of the selected city
        country_id = request.POST['country']  # Assuming 'country' is the ID of the selected country

        try:
            city = City.objects.get(id=city_id)
            country = Country.objects.get(id=country_id)

            shipping_info = ShippingInfo.objects.create(user=user, house_number=house_number, street_name=street_name, phone_number=phone_number, address=address, city=city, country=country)
            shipping_info.save()

            messages.info(request, "Shipping info added successfully 😁.")

            return redirect('dashboard')

        except (City.DoesNotExist, Country.DoesNotExist) as e:
            # Handle the case where the selected city or country doesn't exist
            messages.error(request, "An error occurred while adding shipping info. Please try again.")
            return redirect('shipping')

    for country in countries:
        cities = list(country.city_set.values('id', 'name'))
        cities_data.append({'country_id': str(country.id), 'cities': cities})

    context = {
        'countries': countries,
        'title' : 'Add shipping information',
        'cities_json': json.dumps(cities_data),
        'total_items_in_cart' : total_quantity_in_cart,
    }
    return render(request, 'shipping.html', context)


@login_required
def shipping_detail(request):
    locations = ShippingInfo.objects.filter(user=request.user)
    context = {
        'title' : 'Shiiping Info',
        'shipping_info' : locations,
    }
    return render(request, 'shipping_detail.html', context)

@login_required
def delete_shipping(request, pk):
    ShippingInfo.objects.get(id=pk).delete()
    messages.info(request, "Shipping information deleted successfully.")


@login_required
def get_cities_by_country(request, country_id):
    try:
        country = Country.objects.get(id=country_id)
        cities = list(country.city_set.values('id', 'name'))
        return JsonResponse({'cities': cities})
    except Country.DoesNotExist:
        return JsonResponse({'error': 'Country not found'}, status=404)

@login_required
def account(request):
    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())

    context ={
        'title' : 'Account Management',
        'total_items_in_cart' : total_quantity_in_cart,
    }

    return render(request, 'accounts.html', context)

@login_required
def account_info(request):
    shipping_info = ShippingInfo.objects.filter(user=request.user)

    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())
    orders = Order.objects.filter(customer=request.user)[:4]

    context = {
        'shipping_info' : shipping_info,
        'total_items_in_cart' : total_quantity_in_cart,
        'title' : 'Account Overview',
        'orders' : orders,
    }
    return render(request, 'account_info.html', context)

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user)
    context = {
        'title' : 'My Orders',
        'orders' : orders
    }
    return render(request, 'orders.html', context)


# Create your views here.
