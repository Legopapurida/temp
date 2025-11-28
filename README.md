# Brickaria - Gaming Enterprise Website

A comprehensive Django + Wagtail CMS website for a gaming company focused on brick/lego-style content, games, and community engagement.

## Features

### Core Functionality
- **Django 4.2** + **Wagtail CMS 5.2**
- **PostgreSQL** database
- **Bootstrap 5** responsive design
- Modern gaming-themed UI/UX
- SEO-optimized with Wagtail SEO plugins

### Website Sections
1. **Home/Landing Page** - Hero slider, featured games, community stats
2. **Games Section** - Game listings, individual game pages, categories, tags
3. **Blog System** - News, updates, categories, SEO-friendly
4. **Shop System** - Products, categories, basic cart functionality
5. **Community** - User profiles, posts, screenshots, videos
6. **Events** - Upcoming events, registration
7. **Authentication** - Login/logout, user profiles
8. **Support** - Contact forms, helpdesk integration

### Key Technologies
- **Wagtail StreamFields** for flexible content
- **Django Allauth** for authentication
- **Bootstrap 5** for responsive design
- **Wagtail SEO** for search optimization
- **Django Crispy Forms** for form styling

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Node.js (for frontend assets)

### Installation

1. **Clone and setup virtual environment:**
```bash
git clone <repository-url>
cd Brickaria
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Environment setup:**
```bash
copy .env.example .env
# Edit .env with your database and other settings
```

4. **Database setup:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. **Run development server:**
```bash
python manage.py runserver
```

6. **Access the site:**
- Website: http://localhost:8000
- Admin: http://localhost:8000/admin

## Project Structure

```
Brickaria/
├── apps/
│   ├── core/          # Base models and utilities
│   ├── home/          # Homepage
│   ├── games/         # Games section
│   ├── blog/          # Blog/news
│   ├── shop/          # E-commerce
│   ├── community/     # User community
│   ├── events/        # Events management
│   ├── accounts/      # User accounts
│   └── support/       # Support/helpdesk
├── brickaria/
│   ├── settings/      # Environment-specific settings
│   └── urls.py        # Main URL configuration
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── media/            # User uploads
```

## Key Models

### Games App
- `GamePage` - Individual game pages with media, descriptions, links
- `GameCategory` - Game categorization
- `GamesIndexPage` - Games listing page

### Shop App
- `ProductPage` - Product details, pricing, inventory
- `ProductCategory` - Product categorization
- `Brand` - Product brands

### Blog App
- `BlogPost` - Blog articles with categories and tags
- `BlogCategory` - Blog categorization

### Community App
- `UserProfile` - Extended user profiles
- `Post` - Community posts (screenshots, videos, streams)

## Wagtail Features Used

- **StreamFields** for flexible page content
- **Snippets** for reusable content (categories, brands)
- **Image management** with automatic resizing
- **SEO optimization** with meta tags and structured data
- **Form builder** for contact forms
- **Search functionality** with database backend

## Customization

### Adding New Page Types
1. Create model in appropriate app
2. Add to `INSTALLED_APPS` if new app
3. Create templates in `templates/app_name/`
4. Run migrations

### Styling
- Main styles in `static/css/style.css`
- Bootstrap 5 classes used throughout
- Gaming theme colors defined in CSS variables

### Content Management
- Access Wagtail admin at `/admin/`
- Create pages using the page tree
- Manage snippets (categories, etc.) in admin
- Upload images through the media library

## Production Deployment

1. **Environment setup:**
```bash
export DJANGO_SETTINGS_MODULE=brickaria.settings.prod
```

2. **Static files:**
```bash
python manage.py collectstatic
```

3. **Database:**
```bash
python manage.py migrate
```

4. **Web server:**
- Use Gunicorn + Nginx
- Configure SSL certificates
- Set up Redis for caching

## Recommended Plugins

The project includes several Wagtail plugins:
- `wagtail-seo` - Advanced SEO features
- `wagtailmenus` - Navigation menus
- `wagtail-localize` - Multi-language support
- `django-allauth` - Social authentication
- `django-helpdesk` - Support ticketing

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## License

This project is licensed under the MIT License.