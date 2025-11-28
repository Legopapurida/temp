from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('category/<slug:category_slug>/', views.ProductsByCategoryView.as_view(), name='products_by_category'),
    path('brand/<slug:brand_slug>/', views.ProductsByBrandView.as_view(), name='products_by_brand'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
]