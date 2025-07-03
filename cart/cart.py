from django.conf import settings
from main.models import ClothingItem, ClothingItemSize, Size

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def generate_item_key(self, clothing_item_id, size):
        """Генерирует уникальный ключ для товара+размер"""
        return f"{clothing_item_id}_{size}"

    def add(self, clothing_item, size, quantity=1, replace_quantity=False):
        item_key = self.generate_item_key(clothing_item.id, size)

        # Проверка доступности размера
        try:
            size_obj = Size.objects.get(name=size)
            item_size = ClothingItemSize.objects.get(
                clothing_item=clothing_item,
                size=size_obj
            )
            if not item_size.available:
                return False
        except (Size.DoesNotExist, ClothingItemSize.DoesNotExist):
            return False

        if item_key in self.cart:
            if replace_quantity:
                self.cart[item_key]['quantity'] = quantity
            else:
                self.cart[item_key]['quantity'] += quantity
        else:
            self.cart[item_key] = {
                'clothing_item_id': clothing_item.id,
                'size': size,
                'quantity': quantity
            }

        # Ограничение количества по доступному на складе
        if self.cart[item_key]['quantity'] > item_size.stock_quantity:
            self.cart[item_key]['quantity'] = item_size.stock_quantity

        self.save()
        return True

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, clothing_item, size):
        item_key = self.generate_item_key(clothing_item.id, size)
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def update(self, clothing_item, size, quantity):
        item_key = self.generate_item_key(clothing_item.id, size)
        if item_key in self.cart and quantity > 0:
            # Проверка доступного количества
            try:
                size_obj = Size.objects.get(name=size)
                item_size = ClothingItemSize.objects.get(
                    clothing_item=clothing_item,
                    size=size_obj
                )
                if quantity > item_size.stock_quantity:
                    quantity = item_size.stock_quantity
            except (Size.DoesNotExist, ClothingItemSize.DoesNotExist):
                pass

            self.cart[item_key]['quantity'] = quantity
            self.save()
        elif quantity <= 0:
            self.remove(clothing_item, size)

    def get_total_price(self):
        total = 0
        for item_key, item_data in self.cart.items():
            try:
                clothing_item = ClothingItem.objects.get(id=item_data['clothing_item_id'])
                total += clothing_item.get_price_with_discount() * item_data['quantity']
            except ClothingItem.DoesNotExist:
                continue
        return total

    def __iter__(self):
        # Получаем все ID товаров одним запросом
        clothing_item_ids = [item['clothing_item_id'] for item in self.cart.values()]
        clothing_items = ClothingItem.objects.filter(id__in=clothing_item_ids)
        clothing_items_dict = {item.id: item for item in clothing_items}

        # Создаем копию корзины для итерации
        cart = self.cart.copy()

        for item_key, item_data in cart.items():
            clothing_item_id = item_data['clothing_item_id']
            if clothing_item_id in clothing_items_dict:
                clothing_item = clothing_items_dict[clothing_item_id]
                quantity = item_data['quantity']
                size = item_data['size']
                total_price = clothing_item.get_price_with_discount() * quantity

                # Получаем доступное количество для данного товара и размера
                max_quantity = 99  # значение по умолчанию
                try:
                    size_obj = Size.objects.get(name=size)
                    item_size = ClothingItemSize.objects.get(
                        clothing_item=clothing_item,
                        size=size_obj
                    )
                    max_quantity = item_size.stock_quantity
                except (Size.DoesNotExist, ClothingItemSize.DoesNotExist):
                    pass

                yield {
                    'item_key': item_key,
                    'item': clothing_item,
                    'quantity': quantity,
                    'size': size,
                    'total_price': total_price,
                    'max_quantity': max_quantity
                }

    def __len__(self):
        """Общее количество товаров в корзине (сумма количеств)"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_items_count(self):
        """Количество позиций в корзине (разных товаров+размеров)"""
        return len(self.cart)

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True
