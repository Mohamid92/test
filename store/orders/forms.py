"""
Order Forms

Form classes for order management in admin interface.
Includes validation and processing logic.
"""

from django import forms
from .models import Order, Refund, StoreConfiguration

class OrderAdminForm(forms.ModelForm):
    """
    Admin form for order management
    Includes custom validation and processing
    """
    
    class Meta:
        model = Order
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('order_status') == 'SHIPPED' and not cleaned_data.get('tracking_number'):
            raise forms.ValidationError(
                "Tracking number is required for shipped orders"
            )
        return cleaned_data

# ...more form classes...
