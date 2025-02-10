from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductSpecification
import random

class Command(BaseCommand):
    help = 'Setup sample products'

    def handle(self, *args, **options):
        sample_products = [
            {
                'category': 'Smart Lighting',
                'products': [
                    {
                        'name': 'Smart LED Bulb',
                        'price': 29.99,
                        'brand': 'SmartLight',
                        'specs': {
                            'Wattage': '9W',
                            'Color': 'RGB',
                            'Connectivity': 'WiFi'
                        }
                    },
                    # Add more products here
                ]
            },
            {
                'category': 'Storage Solutions',
                'products': [
                    {
                        'name': 'Enterprise SSD',
                        'price': 299.99,
                        'brand': 'StoragePro',
                        'specs': {
                            'Capacity': '1TB',
                            'Interface': 'NVMe',
                            'Read Speed': '3500MB/s'
                        }
                    },
                    # Add more products here
                ]
            }
        ]

        for category_data in sample_products:
            category = Category.objects.get(name=category_data['category'])
            
            for product_data in category_data['products']:
                product = Product.objects.create(
                    category=category,
                    name=product_data['name'],
                    price=product_data['price'],
                    brand=product_data['brand'],
                    stock=random.randint(10, 100),
                    short_description=f"High-quality {product_data['name']}",
                    description=f"Detailed description for {product_data['name']}"
                )

                for spec_name, spec_value in product_data['specs'].items():
                    ProductSpecification.objects.create(
                        product=product,
                        name=spec_name,
                        value=spec_value
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created sample products'))
