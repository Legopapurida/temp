#!/usr/bin/env python
"""
Brickaria Setup Script
Run this script to set up the initial project structure and data.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_project():
    """Set up the Brickaria project"""
    
    print("🎮 Setting up Brickaria Gaming Website...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brickaria.settings.dev')
    django.setup()
    
    print("📦 Running migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("🏠 Creating initial pages...")
    create_initial_pages()
    
    print("📊 Creating sample data...")
    create_sample_data()
    
    print("✅ Setup complete!")
    print("\n🚀 Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the server: python manage.py runserver")
    print("3. Visit http://localhost:8000/admin to manage content")
    print("4. Visit http://localhost:8000 to see your site")

def create_initial_pages():
    """Create initial page structure"""
    from wagtail.models import Site
    from apps.home.models import HomePage
    from apps.games.models import GamesIndexPage
    from apps.blog.models import BlogIndexPage
    from apps.shop.models import ShopIndexPage
    from apps.community.models import CommunityIndexPage
    from apps.events.models import EventsIndexPage
    
    # Get the root page
    from wagtail.models import Page
    root = Page.objects.get(slug='root')
    
    # Create home page if it doesn't exist
    if not HomePage.objects.exists():
        # Check if a page with slug 'home' already exists
        existing_home = Page.objects.filter(slug='home').first()
        if existing_home:
            print("✅ Home page already exists")
            home = existing_home
        else:
            home = HomePage(
                title="Home",
                slug="brickaria-home",
                hero_title="Welcome to Brickaria",
                hero_subtitle="Building amazing gaming experiences with creativity and community at heart."
            )
            root.add_child(instance=home)
            print("✅ Created home page")
        
        # Set as site root
        site = Site.objects.get(is_default_site=True)
        site.root_page = home
        site.save()
    else:
        home = HomePage.objects.first()
        print("✅ Home page already exists")
    
    # Get home page
    home = HomePage.objects.first() or Page.objects.filter(slug__in=['home', 'brickaria-home']).first()
    
    sections = [
        (GamesIndexPage, "Games", "games", "Discover our amazing games"),
        (BlogIndexPage, "Blog", "blog", "Latest news and updates"),
        (ShopIndexPage, "Shop", "shop", "Browse our products"),
        (CommunityIndexPage, "Community", "community", "Join our gaming community"),
        (EventsIndexPage, "Events", "events", "Upcoming gaming events"),
    ]
    
    for model_class, title, slug, intro in sections:
        if not model_class.objects.filter(slug=slug).exists():
            page = model_class(
                title=title,
                slug=slug,
                intro=f"<p>{intro}</p>"
            )
            home.add_child(instance=page)
            print(f"✅ Created {title} page")

def create_sample_data():
    """Create sample categories and snippets"""
    from apps.games.models import GameCategory
    from apps.blog.models import BlogCategory
    from apps.shop.models import ProductCategory, Brand
    
    # Game categories
    game_categories = [
        ("Action", "Fast-paced action games", "lightning"),
        ("Puzzle", "Mind-bending puzzle games", "puzzle"),
        ("Adventure", "Epic adventure games", "map"),
        ("Building", "Creative building games", "bricks"),
    ]
    
    for name, desc, icon in game_categories:
        GameCategory.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'icon': icon}
        )
    
    # Blog categories
    blog_categories = [
        ("News", "Latest company news", "#007bff"),
        ("Updates", "Game updates and patches", "#28a745"),
        ("Community", "Community highlights", "#ffc107"),
        ("Development", "Behind the scenes", "#6f42c1"),
    ]
    
    for name, desc, color in blog_categories:
        BlogCategory.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'color': color}
        )
    
    # Product categories
    product_categories = [
        ("Toys", "Physical toys and figures", "gift"),
        ("Merch", "Branded merchandise", "bag"),
        ("Digital", "Digital products and DLC", "download"),
        ("Clothing", "Apparel and accessories", "person"),
    ]
    
    for name, desc, icon in product_categories:
        ProductCategory.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'icon': icon}
        )
    
    # Brands
    brands = ["Brickaria", "BrickTech", "GameCraft"]
    for brand_name in brands:
        Brand.objects.get_or_create(name=brand_name)
    
    print("✅ Created sample categories and brands")

if __name__ == '__main__':
    setup_project()