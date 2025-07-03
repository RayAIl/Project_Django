import stripe

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from cart.cart import Cart
from main.models import Size
from .forms import OrderForm
from .models import OrderItem, Order

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@login_required(login_url='/users/login')
def order_create(request):
    cart = Cart(request)
    total_price = sum(item['total_price'] for item in cart)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            
            try:
                size_instances = {
                    item['size']: Size.objects.get(name=item['size'])
                    for item in cart
                }
            except ObjectDoesNotExist as e:
                return render(request, 'orders/order_form.html', {
                    'form': form,
                    'cart': cart,
                    'total_price': total_price,
                    'error': f"Размер не найден: {str(e)}"
                })

            order = Order(
                user=request.user,
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                middle_name=form.cleaned_data.get('middle_name'),
                city=form.cleaned_data.get('city'),
                street=form.cleaned_data.get('street'),
                house_number=form.cleaned_data.get('house_number'),
                apartment_number=form.cleaned_data.get('apartment_number'),
                postal_code=form.cleaned_data.get('postal_code'),
            )
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    clothing_item=item['item'],
                    size=size_instances[item['size']],
                    quantity=item['quantity'],
                    total_price=item['total_price'],
                )

            try:
                line_items = []
                for item in cart:
                    unit_price = item['total_price'] / item['quantity']
                    
                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': item['item'].name,
                            },
                            'unit_amount': int(unit_price * 100),
                        },
                        'quantity': item['quantity'],
                    })

                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url='http://localhost:8000/orders/completed',
                    cancel_url='http://localhost:8000/orders/create'
                )
                return redirect(session.url, code=303)
            
            except Exception as ex:
                return render(request, 'orders/order_form.html', {
                    'form': form,
                    'cart': cart,
                    'total_price': total_price,
                    'error': str(ex),
                })
    
    form = OrderForm(initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'middle_name': request.user.middle_name,
        'city': request.user.city,
        'street': request.user.street,
        'house_number': request.user.house_number,
        'apartment_number': request.user.apartment_number,
        'postal_code': request.user.postal_code,
    })
    return render(request, 'orders/order_form.html', {
        'form': form,
        'cart': cart,
        'total_price': total_price,
    })

@login_required(login_url='/users/login')
def order_success(request):
    cart = Cart(request)
    cart.clear()
    return render(request, 'orders/order_success.html')