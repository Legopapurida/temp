from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, View
from django.contrib import messages
from .models import ProductPage, ProductCategory, Brand


class ProductsByCategoryView(ListView):
    model = ProductPage
    template_name = 'shop/products_by_category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(ProductCategory, name__iexact=self.kwargs['category_slug'])
        return ProductPage.objects.live().filter(categories=self.category).order_by('-first_published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProductsByBrandView(ListView):
    model = ProductPage
    template_name = 'shop/products_by_brand.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.brand = get_object_or_404(Brand, name__iexact=self.kwargs['brand_slug'])
        return ProductPage.objects.live().filter(brand=self.brand).order_by('-first_published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand'] = self.brand
        return context


class CartView(TemplateView):
    template_name = 'shop/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Basic cart implementation using session
        cart = self.request.session.get('cart', {})
        cart_items = []
        total = 0
        
        for product_id, quantity in cart.items():
            try:
                product = ProductPage.objects.get(id=product_id)
                item_total = product.current_price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
            except ProductPage.DoesNotExist:
                pass
        
        context.update({
            'cart_items': cart_items,
            'cart_total': total,
        })
        return context


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(ProductPage, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        request.session['cart'] = cart
        
        messages.success(request, f'{product.title} added to cart!')
        return redirect('shop:cart')