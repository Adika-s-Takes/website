from django.shortcuts import render, get_object_or_404
from collections import defaultdict
from .models import Item, ProductImage, ProductDetail, Order, ProductReview
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import uuid
from accounts.models import ShippingInfo
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Count
from django.db.models.functions import Length
from fuzzywuzzy import fuzz

# @login_required
def shop(request):
    # Get all active items
    items = Item.objects.filter(active=True)

    # Get the cart dictionary from the session
    cart = request.session.get('cart', {})
    print(cart)

    # Add quantity information to each item
    for item in items:
        item.quantity_in_cart = cart.get(str(item.id), 0)

    # Calculate total number of items in the cart
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())

    # Example filters based on choices
    league_filter = request.GET.get('league')
    product_type_filter = request.GET.get('product_type')
    kit_type_filter = request.GET.get('kit_type')
    version_filter = request.GET.get('version')
    season_filter = request.GET.get('season')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    customizable_filter = request.GET.get('customizable')

    # Apply filters if provided
    if league_filter:
        items = items.filter(league=league_filter)
    if product_type_filter:
        items = items.filter(type=product_type_filter)
    if kit_type_filter:
        items = items.filter(kit_type=kit_type_filter)
    if version_filter:
        items = items.filter(version=version_filter)
    if customizable_filter:
        items = items.filter(customizable=customizable_filter)
    if season_filter:
        items = items.filter(season=season_filter)
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    # Paginate the queryset
    paginator = Paginator(items, 20)  # 10 items per page
    page_number = request.GET.get('page')
    try:
        paginated_items = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_items = paginator.page(1)
    except EmptyPage:
        paginated_items = paginator.page(paginator.num_pages)

    context = {
        'title': 'Shop',
        'items': paginated_items,
        'cart': cart,  # Include cart information in the context
        'total_items_in_cart': total_quantity_in_cart,  # Include total items in cart
    }
    return render(request, 'shop.html', context)

# @login_required
def item_details(request, pk):
    if request.method == "POST":
        product_id = request.POST.get('product')
        size = request.POST.get('size')
        name = request.POST.get('name')  # New field for the name on the jersey
        number = request.POST.get('number')  # New field for the number on the jersey
        quantity = int(request.POST.get('quantity', 1))
        remove = request.POST.get('remove')

        # Update the cart with the specified quantity
        cart = request.session.get('cart', {})
        if cart:
            if remove:
                if product_id in cart and size in cart[product_id] and name == cart[product_id][size]['name'] and number == cart[product_id][size]['number']:
                    if cart[product_id][size]['quantity'] <= 1:
                        cart[product_id].pop(size)
                        if not cart[product_id]:
                            cart.pop(product_id)
                        messages.success(request, "Product removed successfully👌")
                    else:
                        cart[product_id][size]['quantity'] -= quantity
                        messages.success(request, "Item removed successfully👌")
                else:
                    messages.error(request, "Invalid request to remove item from cart😞")
            else:
                cart.setdefault(product_id, {}).setdefault(size, {'quantity': 0, 'name': '', 'number': ''})
                cart[product_id][size]['quantity'] += quantity
                messages.success(request, "Item added to cart👌")
                cart[product_id][size]['name'] = name
                cart[product_id][size]['number'] = number
        else:
            cart = {product_id: {size: {'quantity': quantity, 'name': name, 'number': number}}}

        request.session['cart'] = cart



    item = Item.objects.get(id=pk)
    product_images = ProductImage.objects.filter(product=item)
    product_details = ProductDetail.objects.filter(product=item)
    cart = request.session.get('cart', {})
    related_items = Item.objects.filter(
        league=item.league,
    ).exclude(id=pk)

    # Filter items based on fuzzy string matching
    related_items = [related_item for related_item in related_items if fuzz.ratio(item.name, related_item.name) >= 60]

    # Limit the queryset to 10 related items
    related_items = related_items[:10]

    # Rename loop variable from 'item' to 'related_item'
    for related_item in related_items:
        related_item.quantity_in_cart = cart.get(str(related_item.id), 0)

    item.quantity_in_cart = cart.get(str(item.id), 0)


    try:
        total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())
    except Exception:
        total_quantity_in_cart = 0

    available_sizes = item.sizes.all()

    context = {
        'item' : item,
        'product_images' : product_images,
        'product_details' : product_details,
        'title' : item,
        'description' : item.description,
        'related_items': related_items,
        'cart' : cart,
        'total_items_in_cart': total_quantity_in_cart,
        'available_sizes' : available_sizes
    }
    return render(request, 'single-product.html', context)

@login_required
def cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product')
        size = request.POST.get('size')
        name = request.POST.get('name', None)  # New field for the name on the jersey
        number = request.POST.get('number', None)  # New field for the number on the jersey
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})
        if cart:
            if remove:
                if product_id in cart and size in cart[product_id]:
                    # Remove the specified item from the cart
                    cart[product_id].pop(size)
                    # Remove the product from the cart if all sizes are removed
                    if not cart[product_id]:
                        cart.pop(product_id)
                    messages.success(request, "Product removed successfully👌")
                else:
                    messages.error(request, "Invalid request to remove item from cart😞")
            else:
                # If the product and size are already in the cart, update the quantity
                if product_id in cart and size in cart[product_id]:
                    cart[product_id][size]['quantity'] += 1
                else:
                    # If the product or size is not in the cart, add it with quantity 1
                    cart.setdefault(product_id, {}).setdefault(size, {'quantity': 1})
                # Update name and number if provided
                if name:
                    cart[product_id][size]['name'] = name
                if number:
                    cart[product_id][size]['number'] = number
                messages.success(request, "Item added to cart👌")
        else:
            # Create a new cart if it doesn't exist
            cart = {product_id: {size: {'quantity': 1, 'name': name, 'number': number}}}

        request.session['cart'] = cart
        print(cart)

    # Group items in the cart by size
    grouped_items = defaultdict(list)
    for product_id, sizes in request.session.get('cart', {}).items():
        item = get_object_or_404(Item, id=product_id)
        for size, details in sizes.items():
            grouped_items[size].append({
                'item': item,
                'quantity': details['quantity'],
                'total_price': item.price * details['quantity'],
                'name': details.get('name', ''),  # Preserve existing name or use empty string
                'number': details.get('number', ''),  # Preserve existing number or use empty string
            })

    # Calculate total prices for each size group
    total_prices = {size: sum(item['total_price'] for item in items) for size, items in grouped_items.items()}

    # Calculate total price for all items
    total_price_all_items = sum(item['total_price'] for items in grouped_items.values() for item in items)
    total_quantity = sum(item['quantity'] for items in grouped_items.values() for item in items)

    context = {
        'grouped_items': dict(grouped_items),
        'total_prices': total_prices,
        'total_price_all_items': total_price_all_items,
        'total_items_in_cart': total_quantity,
        'title' : 'Cart'
    }

    return render(request, 'cart.html', context)




def generate_unique_reference():
    unique_id = uuid.uuid4()
    unique_id_str = str(unique_id).replace("-", "")
    unique_reference = unique_id_str[:10000]
    return unique_reference



def checkout(request):
    cart = request.session.get('cart', {})
    items = []

    # Group items in the cart by size
    grouped_items = defaultdict(list)
    for product_id, sizes in cart.items():
        item = get_object_or_404(Item, id=product_id)
        for size, details in sizes.items():
            grouped_items[size].append({
                'item': item,
                'quantity': details['quantity'],
                'total_price': item.price * details['quantity'],
                'name': details['name'],
                'number': details['number'],
                'featured_image': item.featured_image,
            })

    # Calculate total prices for each size group
    total_prices = {size: sum(item['total_price'] for item in items) for size, items in grouped_items.items()}

    # Calculate total price for all items
    total_price_all_items = sum(item['total_price'] for items in grouped_items.values() for item in items)

    # Convert the grouped items back into a flat list for rendering
    for items_list in grouped_items.values():
        items.extend(items_list)

    # Generate a unique reference for the order
    unique_reference = generate_unique_reference()
    shipping_info = ShippingInfo.objects.filter(user=request.user)
    cart = request.session.get('cart', {})
    total_quantity_in_cart = sum(sum(details['quantity'] for details in sizes.values()) for sizes in cart.values())


    context = {
        'title': 'Checkout',
        'grouped_items': dict(grouped_items),
        'total_price': total_price_all_items,  # Use the total price for all items
        'unique_reference': unique_reference,
        'shipping_info': shipping_info,
        'total_items_in_cart' : total_quantity_in_cart,
    }

    if request.method == "POST":
        shipping_id = request.POST.get('shipping_address')
        status = "PENDING"
        ref = request.POST.get('tx_ref')
        customer = request.user
        amount = total_price_all_items  # Use the total price for all items

        for product_id, sizes in cart.items():
            item = get_object_or_404(Item, id=product_id)
            for size, details in sizes.items():
                Order.objects.create(
                    ref=ref,
                    item=item,
                    quantity=details['quantity'],
                    customer=customer,
                    price=item.price,
                    status=status,
                    shipping_info=ShippingInfo.objects.get(id=shipping_id),
                    size=size,
                    name=details['name'],
                    number=details['number'],
                )

    return render(request, 'checkout.html', context)

def review(request, pk):
    item = Item.objects.get(id=pk)
    if request.method == "POST":
        item = item
        reviewer = request.user
        rating = request.POST['rating']
        review = request.POST['review']

        new_review = ProductReview.objects.create(item=item, reviewer=reviewer, rating=rating, review=review)
        new_review.save()


    context = {
        'title' : 'Leave a review',
        'item' : item
    }
    return render(request, 'review.html', context)