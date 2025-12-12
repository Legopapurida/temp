# Localization Setup

## Overview
The system now supports multi-language and multi-currency based on user preferences.

## Features Implemented

### 1. Language Support
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)

### 2. Currency Support
- USD - US Dollar ($)
- EUR - Euro (€)
- GBP - British Pound (£)
- CAD - Canadian Dollar (CA$)
- AUD - Australian Dollar (A$)

## How It Works

### User Preferences
When a user selects their language and currency in their profile:
1. The middleware automatically activates their language for all pages
2. The currency is stored in session and used throughout the site
3. Emails are sent in the user's preferred language with their currency

### Template Usage

#### Display prices with user's currency:
```django
{% load shop_tags %}
{{ product.price|convert_currency:user_currency|currency_format:user_currency }}
```

#### Simple currency format:
```django
{% load shop_tags %}
{{ order.total_amount|currency_format:user_currency }}
```

### Email Localization
All order emails (confirmation, shipped, delivered) are automatically sent in the user's preferred language with their currency.

## Setup Instructions

### 1. Generate Translation Files
```bash
python manage.py makemessages -l es -a --ignore=venv/*
python manage.py makemessages -l fr -a --ignore=venv/*
python manage.py makemessages -l de -a --ignore=venv/*
python manage.py makemessages -l it -a --ignore=venv/*
```

### 2. Translate Messages
Edit the `.po` files in `locale/[language]/LC_MESSAGES/django.po`

### 3. Compile Translations
```bash
python manage.py compilemessages --ignore=venv/*
```

## Components

### Middleware
- `apps.shop.middleware.UserPreferencesMiddleware` - Applies user language/currency preferences

### Context Processors
- `apps.shop.context_processors.user_preferences` - Makes preferences available in templates

### Template Filters
- `currency_format` - Format price with currency symbol
- `convert_currency` - Convert price to target currency

## Notes

- Currency conversion uses simplified rates. For production, integrate a real exchange rate API
- Translation strings need to be added to templates using `{% trans %}` and `{% blocktrans %}` tags
- User preferences are automatically applied on login
- Guest users see default language (English) and currency (USD)
