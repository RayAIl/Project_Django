from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from .cart import Cart
from main.models import ClothingItem, ClothingItemSize, Size

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_add(request, item_id):
    cart = Cart(request)
    clothing_item = get_object_or_404(ClothingItem, id=item_id)
    size_name = request.POST.get('size')

    # Проверка и получение размера
    if not size_name:
        messages.error(request, 'Пожалуйста, выберите размер')
        return redirect('cart:cart_detail')

    try:
        size_obj = Size.objects.get(name=size_name)
        item_size = ClothingItemSize.objects.get(
            clothing_item=clothing_item, 
            size=size_obj
        )
        
        # Проверка доступности и количества
        if not item_size.available:
            messages.error(request, 'Этот размер временно недоступен')
            return redirect('cart:cart_detail')
            
    except Size.DoesNotExist:
        messages.error(request, 'Неверно указан размер')
        return redirect('cart:cart_detail')
    except ClothingItemSize.DoesNotExist:
        messages.error(request, 'Этот размер не доступен для данного товара')
        return redirect('cart:cart_detail')

    # Добавление в корзину
    cart.add(clothing_item, size_name)
    messages.success(request, f'{clothing_item.name} ({size_name}) добавлен в корзину')
    return redirect('cart:cart_detail')

def cart_remove(request, item_id, size=None):
    cart = Cart(request)
    clothing_item = get_object_or_404(ClothingItem, id=item_id)
    
    # Удаление конкретного размера
    if size:
        cart.remove(clothing_item, size)
        messages.success(request, f'{clothing_item.name} ({size}) удален из корзины')
    else:
        # Удаление всех размеров товара
        cart.remove(clothing_item)
        messages.success(request, f'{clothing_item.name} удален из корзины')
    
    return redirect('cart:cart_detail')

class CartUpdateView(View):
    def post(self, request, item_id, size):
        cart = Cart(request)
        clothing_item = get_object_or_404(ClothingItem, id=item_id)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1
        
        # Проверка доступного количества
        try:
            size_obj = Size.objects.get(name=size)
            item_size = ClothingItemSize.objects.get(
                clothing_item=clothing_item, 
                size=size_obj
            )
            
            if quantity > item_size.stock_quantity:
                quantity = item_size.stock_quantity
                messages.warning(request, f'Максимально доступное количество: {item_size.stock_quantity}')
        except (Size.DoesNotExist, ClothingItemSize.DoesNotExist):
            pass
        
        # Обновление количества
        cart.update(clothing_item, size, quantity)
        messages.success(request, f'Количество {clothing_item.name} ({size}) обновлено')
        
        return redirect('cart:cart_detail')