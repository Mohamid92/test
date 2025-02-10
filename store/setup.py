import os
import subprocess

def setup_project():

    
    # Install requirements
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

    
    # Create main apps
    apps = [
        'accounts',
        'products',
        'orders',
        'cart',
        'analytics',
        'seo',
    ]
    
    for app in apps:
        subprocess.run(['python', 'manage.py', 'startapp', app])

if __name__ == "__main__":
    setup_project()
