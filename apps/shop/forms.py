from django import forms
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Address, ProductReview, UserProfile


class AddressForm(forms.ModelForm):
    """Form for managing user addresses"""
    
    class Meta:
        model = Address
        fields = [
            'type', 'first_name', 'last_name', 'company',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'phone', 'is_default'
        ]
        widgets = {
            'country': CountrySelectWidget(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CheckoutForm(forms.Form):
    """Form for checkout process"""
    
    shipping_address = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        empty_label=None
    )
    
    billing_address = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        empty_label=None
    )
    
    shipping_method = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        empty_label=None
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('card', 'Credit/Debit Card'),
            ('paypal', 'PayPal'),
            ('apple_pay', 'Apple Pay'),
            ('google_pay', 'Google Pay'),
            ('cod', 'Cash on Delivery'),
        ],
        widget=forms.RadioSelect
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shipping_address'].queryset = user.addresses.filter(type='shipping')
        self.fields['billing_address'].queryset = user.addresses.filter(type='billing')


class ProductReviewForm(forms.ModelForm):
    """Form for product reviews"""
    
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'review']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class UserProfileForm(forms.ModelForm):
    """Form for user profile"""
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
    ]
    
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'date_of_birth', 'avatar', 'currency', 'language', 'newsletter_subscribed']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'newsletter_subscribed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserForm(forms.ModelForm):
    """Form for basic user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CouponForm(forms.Form):
    """Form for applying coupons"""
    
    coupon_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code'
        })
    )


class AddToCartForm(forms.Form):
    """Form for adding products to cart"""
    
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    variant_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )


class CartUpdateForm(forms.Form):
    """Form for updating cart items"""
    
    item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )