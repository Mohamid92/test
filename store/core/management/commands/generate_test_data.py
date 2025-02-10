from django.core.management.base import BaseCommand
from products.models import Category, Product
from django.utils.text import slugify
import random
from decimal import Decimal
from datetime import datetime

class Command(BaseCommand):
    help = 'Generates test product data'

    def handle(self, *args, **kwargs):
        # Get timestamp for unique SKUs
        timestamp = datetime.now().strftime('%y%m%d%H%M')

        # Category data
        categories = [
            # Smartphones and Accessories
            ("Smartphones", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"),
            ("Phone Cases", "https://images.unsplash.com/photo-1541877944-ac135a41d8d5"),
            ("Screen Protectors", "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd"),
            
            # Laptops and Accessories
            ("Gaming Laptops", "https://images.unsplash.com/photo-1537211261771-e6dd757ffd6e"),
            ("Business Laptops", "https://images.unsplash.com/photo-1531297484001-80022131f5a1"),
            ("Laptop Bags", "https://images.unsplash.com/photo-1547949003-9792a18a2601"),
            
            # Tablets
            ("iPads", "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0"),
            ("Android Tablets", "https://images.unsplash.com/photo-1587033411391-5d9e51cce126"),
            ("Tablet Accessories", "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e"),
        ]

        brands_by_category = {
            'Smartphones': ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Huawei', 'Sony'],
            'Gaming Laptops': ['Razer', 'Alienware', 'ASUS ROG', 'MSI', 'Lenovo Legion'],
            'Business Laptops': ['Dell', 'HP', 'Lenovo ThinkPad', 'Apple', 'Microsoft Surface'],
            'iPads': ['iPad Pro', 'iPad Air', 'iPad mini', 'iPad'],
            'Android Tablets': ['Samsung Galaxy Tab', 'Lenovo Tab', 'Huawei MatePad', 'Amazon Fire'],
        }

        # Product images by category
        product_images = {
            'Smartphones': [
                'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9',
                'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf',
                'https://images.unsplash.com/photo-1565849904461-04a58ad377e0',
                'https://images.unsplash.com/photo-1578872159942-8f4607047986',
            ],
            'Gaming Laptops': [
                'https://images.unsplash.com/photo-1537211261771-e6dd757ffd6e',
                'https://images.unsplash.com/photo-1544652478-6653e09f18a2',
                'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2',
            ],
            'Business Laptops': [
                'https://images.unsplash.com/photo-1531297484001-80022131f5a1',
                'https://images.unsplash.com/photo-1541807084-5c52b6b3adef',
                'https://images.unsplash.com/photo-1496181133206-80ce9b88a853',
            ],
            'iPads': [
                'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0',
                'https://images.unsplash.com/photo-1632679840765-761c4035c890',
            ],
            'Android Tablets': [
                'https://images.unsplash.com/photo-1587033411391-5d9e51cce126',
                'https://images.unsplash.com/photo-1589739900243-4b52cd9b104e',
            ]
        }

        # Clear existing data
        Category.objects.all().delete()
        Product.objects.all().delete()
        self.stdout.write("Cleared existing data")

        # Create categories
        for index, (cat_name, cat_image) in enumerate(categories, 1):
            category = Category.objects.create(
                name=cat_name,
                slug=slugify(cat_name),
                image=cat_image,
                is_active=True,
                is_featured=True if cat_name in brands_by_category else False,
                meta_keywords=f"{cat_name}, electronics, tech",
                meta_description=f"Shop our selection of {cat_name} at great prices",
                order=index
            )
            self.stdout.write(f"Created category: {cat_name}")
            
            # Generate products for main categories
            if (cat_name in brands_by_category):
                for prod_index in range(30):  # 30 products per category
                    brand = random.choice(brands_by_category[cat_name])
                    model_number = f"{random.randint(1, 999):03d}"
                    name = f"{brand} {cat_name[:-1] if cat_name.endswith('s') else cat_name} {model_number}"
                    
                    # Generate unique SKU using timestamp, category index, and product index
                    sku = f"{slugify(brand)[:4]}{timestamp}{index:02d}{prod_index:03d}"
                    
                    # Price ranges by category
                    price_ranges = {
                        'Smartphones': (499, 1499),
                        'Gaming Laptops': (999, 3999),
                        'Business Laptops': (699, 2999),
                        'iPads': (399, 1699),
                        'Android Tablets': (199, 999)
                    }
                    
                    price_range = price_ranges.get(cat_name, (99, 999))
                    price = Decimal(random.randint(price_range[0], price_range[1]))
                    sale_price = price * Decimal('0.85') if random.random() > 0.7 else None
                    
                    try:
                        Product.objects.create(
                            name=name,
                            slug=f"{slugify(name)}-{timestamp}{prod_index}",  # Make slug unique
                            sku=sku,
                            category=category,
                            description=f"Experience the power of {name} with its amazing features and capabilities.",
                            short_description=f"Latest {brand} {cat_name[:-1] if cat_name.endswith('s') else cat_name}",
                            price=price,
                            sale_price=sale_price,
                            stock=random.randint(0, 100),
                            brand=brand,
                            image=random.choice(product_images.get(cat_name, [])),
                            is_active=True,
                            meta_keywords=f"{brand}, {cat_name}, electronics",
                            meta_description=f"Buy the {name} at the best price"
                        )
                        self.stdout.write(f"Created product: {name} (SKU: {sku})")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error creating product {name}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Successfully generated categories and products'))
