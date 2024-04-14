from django.shortcuts import render, redirect
import requests
from django.http import HttpResponse
from products.models import Order, Item
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from .models import DripGuide
from django.contrib.auth.decorators import login_required


def index(request):
    items = Item.objects.filter(active=True)[:8]
    drips = DripGuide.objects.filter(active=True)
    cart = request.session.get('cart', {})
    try:
        total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())
    except Exception as e:
        total_quantity_in_cart = 0

    context = {
        'items': items,
        'drips' : drips,
        'title': "Homepage",
        'total_items_in_cart' : total_quantity_in_cart,
    }

    return render(request, 'index.html', context)

def dashboard(request):
    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())

    context = {
        'total_items_in_cart' : total_quantity_in_cart
    }

    return render(request, 'dashboard.html', context)

def contact(request):
    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())

    context = {
        'total_items_in_cart' : total_quantity_in_cart,
        'title' : 'Contact Us'
    }

    return render(request, 'contact.html', context)

def about(request):
    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())

    context = {
        'total_items_in_cart' : total_quantity_in_cart,
        'title' : "About Adikastakes"
    }
    return render(request, 'about.html', context)

@login_required
def thank_you(request):
    if 'tx_ref' in request.GET and 'transaction_id' in request.GET and 'status' in request.GET:
        tx_ref = request.GET.get('tx_ref')
        transaction_id = request.GET.get('transaction_id')
        status = request.GET.get('status')

        # Verify the transaction using Flutterwave API
        verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
        headers = {'Authorization': 'Bearer FLWSECK_TEST-fe94cd04e4ef7456b433e70e84c96ea9-X'}
        response = requests.get(verify_url, headers=headers)

        if response.status_code == 200:
            # Transaction verified successfully
            data = response.json()
            print(data)
            if data['status'] == 'success':
                # Fetch orders with the same tx_ref
                orders = Order.objects.filter(ref=tx_ref)
                order = orders[0]
                # print(orders)

                # Update each order
                for order in orders:
                    order.paid = True
                    order.flutterwave_ref = transaction_id
                    order.status = "ORDER PLACED"
                    order.save()

                # Send email notification
                username = request.user.username
                email = request.user.email
                ctx = {
                    'user': username,
                    'orders': orders,
                    'order' : order,
                }
                message = get_template('thanks.html').render(ctx)
                msg = EmailMessage(
                    'Order Placed',
                    message,
                    'The Adikastakes Logistics Team',
                    [email],
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()

                # Clear the cart
                request.session['cart'] = {}
                cart = request.session.get('cart', {})
                total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())


                context = {
                    'title': 'Thank You!',
                    'total_items_in_cart' : total_quantity_in_cart,
                }

                # Payment was successful, render the thank you page
                return render(request, 'thank-you.html', context)
            else:
                # Payment was not successful, handle accordingly
                return HttpResponse("<h1>Payment Verification Error! (You no smart)</h1>")
        else:
            # Unable to verify transaction, handle accordingly
            return HttpResponse("<h1>Transaction Verification Failed!</h1>")
    else:
        # Redirect parameters not found, handle accordingly
        return HttpResponse("<h1>Invalid Request!</h1>")

def clear(request):
    request.session['cart'] = {}
    return redirect('shop')

def faq(request):
    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())

    context = {
        'title' : "FAQs(Frequently Asked Questions)",
        'total_items_in_cart' : total_quantity_in_cart,
    }
    return render(request, 'faq.html', context)





# Create your views here.
