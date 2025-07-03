from django.views.generic import ListView, DetailView
from .models import ClothingItem, Category, Size, ClothingItemSize
from django.db.models import Q
from django.core.exceptions import ValidationError


class CatalogView(ListView):
    model = ClothingItem
    template_name = 'main/list.html'
    context_object_name = 'clothing_items'
    paginate_by = 24  # Добавлена пагинация

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related(
            'sizes', 
            'clothingitemsize_set'
        )
        
        category_slugs = self.request.GET.getlist('category')
        size_names = self.request.GET.getlist('size')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        ordering = self.request.GET.get('ordering', 'name')  # Сортировка по умолчанию

        # Фильтр по категориям
        if category_slugs:
            queryset = queryset.filter(category__slug__in=category_slugs)
        
        # Фильтр по размерам
        if size_names:
            queryset = queryset.filter(
                clothingitemsize__size__name__in=size_names,
                clothingitemsize__available=True
            ).distinct()
        
        # Фильтр по цене
        try:
            min_price_val = float(min_price) if min_price else None
            max_price_val = float(max_price) if max_price else None
        except (TypeError, ValueError):
            min_price_val = None
            max_price_val = None

        if min_price_val is not None:
            queryset = queryset.filter(price__gte=min_price_val)
        if max_price_val is not None:
            queryset = queryset.filter(price__lte=max_price_val)

        # Сортировка
        valid_ordering = ['name', 'price', '-price', '-created_at']
        if ordering in valid_ordering:
            queryset = queryset.order_by(ordering)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context['sizes'] = Size.objects.all()
        context['selected_categories'] = self.request.GET.getlist('category')
        context['selected_sizes'] = self.request.GET.getlist('size')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['ordering'] = self.request.GET.get('ordering', 'name')
        return context


class ClothingItemDetailView(DetailView):
    model = ClothingItem
    template_name = 'main/detail.html'
    context_object_name = 'clothing_item'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related(
            'clothingitemsize_set__size'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clothing_item = self.object 
        
        # Получаем все доступные размеры с информацией о количестве
        available_sizes = clothing_item.clothingitemsize_set.filter(
            available=True
        ).select_related('size')
        
        context['available_sizes'] = available_sizes
        return context