from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'Setup initial product categories'

    def handle(self, *args, **options):
        categories_data = {
            'Smart Home': [
                'Smart Lighting',
                'Smart Locks',
                'Security Cameras',
                'Home Automation',
                'Smart Thermostats'
            ],
            'IT Infrastructure': [
                'Storage Solutions',
                'Networking Equipment',
                'Servers',
                'Data Center Equipment',
                'Network Security'
            ],
            'Consumer Electronics': [
                'Mobile Accessories',
                'Computer Peripherals',
                'Audio Equipment',
                'Smart Wearables',
                'Gaming Accessories'
            ]
        }

        for main_category, subcategories in categories_data.items():
            parent, created = Category.objects.get_or_create(
                name=main_category,
                defaults={
                    'description': f'All {main_category} products',
                    'meta_description': f'Shop for {main_category} products',
                    'meta_keywords': f'{main_category}, electronics, smart devices'
                }
            )
            
            for index, subcat in enumerate(subcategories):
                Category.objects.get_or_create(
                    name=subcat,
                    defaults={
                        'parent': parent,
                        'order': index,
                        'description': f'Shop for {subcat}',
                        'meta_description': f'Buy {subcat} online',
                        'meta_keywords': f'{subcat}, {main_category}, electronics'
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully created categories'))
