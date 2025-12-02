from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.shop.models import (
    ProductCategory, Brand, ShippingMethod, Coupon, 
    ProductAttribute, ProductAttributeValue
)
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Set up initial e-commerce data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up e-commerce data...')
        
        # Create product categories
        self.create_categories()
        
        # Create brands
        self.create_brands()
        
        # Create shipping methods
        self.create_shipping_methods()
        
        # Create sample coupons
        self.create_coupons()
        
        # Create product attributes
        self.create_attributes()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up e-commerce data!')
        )

    def create_categories(self):
        """Create product categories"""
        categories = [
            {
                'name': 'Building Sets',
                'description': 'Complete building sets and kits',
                'icon': 'fas fa-cubes'
            },
            {
                'name': 'Minifigures',
                'description': 'Individual minifigures and accessories',
                'icon': 'fas fa-user'
            },
            {
                'name': 'Vehicles',
                'description': 'Cars, planes, ships and other vehicles',
                'icon': 'fas fa-car'
            },
            {
                'name': 'Architecture',
                'description': 'Buildings and architectural sets',
                'icon': 'fas fa-building'
            },
            {
                'name': 'Space',
                'description': 'Space-themed sets and vehicles',
                'icon': 'fas fa-rocket'
            },
            {
                'name': 'City',
                'description': 'City and town themed sets',
                'icon': 'fas fa-city'
            },
        ]
        
        for cat_data in categories:
            category, created = ProductCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

    def create_brands(self):
        """Create brands"""
        brands = [
            'LEGO',
            'Mega Construx',
            'K\'NEX',
            'Playmobil',
            'Brickmania',
            'Custom Bricks',
        ]
        
        for brand_name in brands:
            brand, created = Brand.objects.get_or_create(name=brand_name)
            if created:
                self.stdout.write(f'Created brand: {brand.name}')

    def create_shipping_methods(self):
        """Create shipping methods"""
        shipping_methods = [
            {
                'name': 'Standard Shipping',
                'description': 'Delivery in 5-7 business days',
                'base_cost': Decimal('9.99'),
                'cost_per_kg': Decimal('2.00'),
                'min_delivery_days': 5,
                'max_delivery_days': 7,
                'free_shipping_threshold': Decimal('50.00'),
            },
            {
                'name': 'Express Shipping',
                'description': 'Delivery in 2-3 business days',
                'base_cost': Decimal('19.99'),
                'cost_per_kg': Decimal('3.00'),
                'min_delivery_days': 2,
                'max_delivery_days': 3,
                'free_shipping_threshold': Decimal('100.00'),
            },
            {
                'name': 'Overnight Shipping',
                'description': 'Next business day delivery',
                'base_cost': Decimal('29.99'),
                'cost_per_kg': Decimal('5.00'),
                'min_delivery_days': 1,
                'max_delivery_days': 1,
                'free_shipping_threshold': None,
            },
        ]
        
        for method_data in shipping_methods:
            method, created = ShippingMethod.objects.get_or_create(
                name=method_data['name'],
                defaults=method_data
            )
            if created:
                self.stdout.write(f'Created shipping method: {method.name}')

    def create_coupons(self):
        """Create sample coupons"""
        now = timezone.now()
        
        coupons = [
            {
                'code': 'WELCOME10',
                'name': 'Welcome 10% Off',
                'description': 'Get 10% off your first order',
                'discount_type': 'percentage',
                'discount_value': Decimal('10.00'),
                'minimum_amount': Decimal('25.00'),
                'valid_from': now,
                'valid_until': now + timedelta(days=365),
                'first_order_only': True,
            },
            {
                'code': 'FREESHIP',
                'name': 'Free Shipping',
                'description': 'Free shipping on any order',
                'discount_type': 'free_shipping',
                'discount_value': Decimal('0.00'),
                'minimum_amount': Decimal('0.00'),
                'valid_from': now,
                'valid_until': now + timedelta(days=30),
                'usage_limit': 100,
            },
            {
                'code': 'SAVE20',
                'name': '$20 Off',
                'description': 'Get $20 off orders over $100',
                'discount_type': 'fixed',
                'discount_value': Decimal('20.00'),
                'minimum_amount': Decimal('100.00'),
                'valid_from': now,
                'valid_until': now + timedelta(days=60),
                'usage_limit': 50,
            },
        ]
        
        for coupon_data in coupons:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )
            if created:
                self.stdout.write(f'Created coupon: {coupon.code}')

    def create_attributes(self):
        """Create product attributes"""
        attributes_data = [
            {
                'name': 'Color',
                'type': 'color',
                'values': [
                    {'value': 'Red', 'color_code': '#FF0000'},
                    {'value': 'Blue', 'color_code': '#0000FF'},
                    {'value': 'Green', 'color_code': '#00FF00'},
                    {'value': 'Yellow', 'color_code': '#FFFF00'},
                    {'value': 'Black', 'color_code': '#000000'},
                    {'value': 'White', 'color_code': '#FFFFFF'},
                ]
            },
            {
                'name': 'Size',
                'type': 'text',
                'values': [
                    {'value': 'Small'},
                    {'value': 'Medium'},
                    {'value': 'Large'},
                    {'value': 'Extra Large'},
                ]
            },
            {
                'name': 'Age Range',
                'type': 'text',
                'values': [
                    {'value': '4-6 years'},
                    {'value': '6-8 years'},
                    {'value': '8-12 years'},
                    {'value': '12+ years'},
                    {'value': 'Adult'},
                ]
            },
            {
                'name': 'Piece Count',
                'type': 'number',
                'values': [
                    {'value': '1-50'},
                    {'value': '51-100'},
                    {'value': '101-500'},
                    {'value': '501-1000'},
                    {'value': '1000+'},
                ]
            },
        ]
        
        for attr_data in attributes_data:
            attribute, created = ProductAttribute.objects.get_or_create(
                name=attr_data['name'],
                defaults={'type': attr_data['type']}
            )
            
            if created:
                self.stdout.write(f'Created attribute: {attribute.name}')
                
                # Create attribute values
                for value_data in attr_data['values']:
                    ProductAttributeValue.objects.create(
                        attribute=attribute,
                        value=value_data['value'],
                        color_code=value_data.get('color_code', '')
                    )