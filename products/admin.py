from django.contrib import admin
from .models import Item, ProductImage, ProductTag, ProductDetail, Order, Size, ProductReview, Wishlist


class ProductImageAdmin(admin.TabularInline):
    model = ProductImage

class ProductDetailAdmin(admin.TabularInline):
    model = ProductDetail

class ItemAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin, ProductDetailAdmin]
    list_display = ['name', 'id', 'price', 'initial_price', 'type', 'stock', 'active', 'custom_item_id', 'kit_type', 'customizable']


class WishlistAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'user']

    def item_name(self, obj):
        if obj.item:
            return obj.item.name

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_name', 'quantity', 'price', 'customer', 'status', 'shipping_info_address', 'customer_phone_number', 'customer_email', 'paid']

    def item_name(self, obj):
        return obj.item.name
    
    def shipping_info_address(self, obj):
        if obj.shipping_info:
            return f"{obj.shipping_info.address}, {obj.shipping_info.city}, {obj.shipping_info.country}"
        return "N/A"
    
    def customer_phone_number(self, obj):
        if obj.shipping_info:
            return f"{obj.shipping_info.phone_number}"
        return "N/A"
    
    def customer_email(self, obj):
        if obj.customer:
            return f"{obj.customer.email}"
        return "N/A"

    def get_related_orders(self, obj):
        return Order.objects.filter(ref=obj.ref).exclude(id=obj.id)  # Exclude the current order from the related orders

    def related_orders_display(self, obj):
        related_orders = self.get_related_orders(obj)
        if related_orders.exists():
            details = []
            for order in related_orders:
                details.append(f"Order ID: {order.id}, Item: {order.item.name}, Quantity: {order.quantity}, Price: {order.price}, Customer: {order.customer.username}, Status: {order.status}, Paid: {order.paid}")
            return ', '.join(details)
        return "No related orders"

    item_name.short_description = 'Item Name'
    shipping_info_address.short_description = 'Shipping Address'
    related_orders_display.short_description = 'Related Orders'
    related_orders_display.admin_order_field = 'ref'  # Allow sorting by reference
    
    readonly_fields = ['related_orders_display']


admin.site.register(Item, ItemAdmin)
admin.site.register(ProductTag)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductReview)
admin.site.register(Size)
admin.site.register(Wishlist, WishlistAdmin)
# Register your models here.
