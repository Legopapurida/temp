# Currency Conversion Feature

## Overview
Users can now select their preferred currency in their profile settings, and all prices across the site will automatically convert and display in their chosen currency.

## Supported Currencies
- USD (US Dollar) - $
- EUR (Euro) - €
- GBP (British Pound) - £
- CAD (Canadian Dollar) - CA$
- AUD (Australian Dollar) - A$

## How It Works

### 1. User Profile Settings
Users can change their currency preference in the Edit Profile page (`/shop/edit-profile/`).
When they change the currency or language, they'll be prompted to save and reload the page.

### 2. Currency Conversion
- Exchange rates are defined in `apps/shop/templatetags/currency_filters.py`
- All prices are stored in USD in the database
- Prices are converted on-the-fly when displayed using the `format_price` template filter

### 3. Template Usage
To display prices with currency conversion in any template:

```django
{% load currency_filters %}

<!-- Simple price display -->
{{ product.price|format_price:user_currency }}

<!-- Or convert without formatting -->
{{ product.price|convert_currency:user_currency }}
```

### 4. Context Variables
Available globally in all templates:
- `user_currency` - The user's selected currency code (e.g., 'EUR')
- `currency_symbol` - The currency symbol (e.g., '€')
- `user_language` - The user's selected language code (e.g., 'en')

## Files Modified

### Models
- `apps/community/models.py` - Added currency, language, phone, date_of_birth, newsletter_subscribed fields to UserProfile

### Template Filters
- `apps/shop/templatetags/currency_filters.py` - Currency conversion and formatting filters

### Context Processors
- `apps/shop/context_processors.py` - Provides user_currency, currency_symbol, user_language to all templates

### Middleware
- `apps/shop/middleware.py` - Applies user's language and currency preferences to each request

### Templates Updated
- `templates/shop/edit_profile.html` - Added JavaScript to observe currency/language changes
- `templates/shop/product_page.html` - Prices display in user's currency
- `templates/shop/cart.html` - Cart prices display in user's currency
- `templates/shop/shop_index_page.html` - Product listing prices display in user's currency

## Updating Exchange Rates

To update exchange rates, edit the `EXCHANGE_RATES` dictionary in `apps/shop/templatetags/currency_filters.py`:

```python
EXCHANGE_RATES = {
    'USD': Decimal('1.00'),
    'EUR': Decimal('0.92'),  # Update this value
    'GBP': Decimal('0.79'),  # Update this value
    'CAD': Decimal('1.36'),  # Update this value
    'AUD': Decimal('1.52'),  # Update this value
}
```

For production, consider using a real-time exchange rate API.

## Adding New Currencies

1. Add the currency to `EXCHANGE_RATES` in `currency_filters.py`
2. Add the currency symbol to the `symbols` dict in the `format_price` filter
3. Add the currency to `CURRENCY_CHOICES` in `apps/shop/forms.py`
4. Add the currency symbol to `currency_symbols` in `apps/shop/context_processors.py`

## Testing

1. Login to the site
2. Go to Edit Profile
3. Change currency from USD to EUR
4. Click "Update Profile" when prompted
5. Navigate to shop pages - all prices should now display in EUR with € symbol
