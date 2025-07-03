from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'session_key')
    date_hierarchy = 'created_at'
    readonly_fields = ('session_key', 'created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('clothing_item', 'size', 'quantity', 'cart')
    list_filter = ('size',)
    search_fields = ('clothing_item__name', 'cart__id')
    autocomplete_fields = ('clothing_item', 'size', 'cart')
