from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Add any additional product-specific URLs here
    path('category/<slug:slug>/', views.CategoryViewSet.as_view({'get': 'retrieve'}), name='category-detail'),
    path('product/<slug:slug>/', views.ProductViewSet.as_view({'get': 'retrieve'}), name='product-detail'),
]
