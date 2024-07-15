from django.contrib import admin
from .models import Restaurant, Delivery, Order


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'email', 'opening_hours')
    search_fields = ('name', 'address')
    list_filter = ('opening_hours',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user_address', 'delivery_time', 'delivery_fee')
    search_fields = ('restaurant__name', 'user_address__city', 'user_address__street')
    list_filter = ('delivery_time', 'restaurant')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'restaurant', 'delivery', 'order_time', 'total_amount', 'user', 'order_status', 'is_pickup')
    search_fields = ('user',)
    list_filter = ('order_time', 'order_status', 'restaurant', 'is_pickup')
    list_display_links = ('id', 'user')
