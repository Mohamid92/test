from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = 'Sets up test data for the store'

    def handle(self, *args, **kwargs):
        # Create media directories if they don't exist
        media_dirs = ['products', 'categories']
        for dir_name in media_dirs:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, dir_name), exist_ok=True)

        # Copy sample images
        sample_images = {
            'products/iphone14.jpg': 'sample_images/iphone14.jpg',
            'products/macbook.jpg': 'sample_images/macbook.jpg',
            'categories/smartphones.jpg': 'sample_images/smartphones.jpg',
            'categories/laptops.jpg': 'sample_images/laptops.jpg',
        }

        for dest, src in sample_images.items():
            dest_path = os.path.join(settings.MEDIA_ROOT, dest)
            src_path = os.path.join(settings.BASE_DIR, src)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            if os.path.exists(src_path):
                shutil.copy(src_path, dest_path)

        # Load fixtures using absolute path
        fixture_path = os.path.join(settings.BASE_DIR, 'fixtures', 'initial_data.json')
        if os.path.exists(fixture_path):
            call_command('loaddata', fixture_path)
            self.stdout.write(
                self.style.SUCCESS('Successfully loaded fixture data')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Fixture file not found at {fixture_path}')
            )
