# views.py - Complete DjCrudX Widgets Example

from django import forms
import django_filters
from djcrudx import create_crud
from djcrudx.widgets import (
    MultiSelectDropdownWidget,
    SingleSelectDropdownWidget, 
    ColoredSelectDropdownWidget,
    DateTimePickerWidget,
    DateRangePickerWidget,
    ActiveStatusDropdownWidget,
    TextInputWidget
)
from .models import Product, Category

# Form with all widgets
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            # Multi-select
            'tags': MultiSelectDropdownWidget(),
            'categories': MultiSelectDropdownWidget(),
            
            # Single select
            'primary_category': SingleSelectDropdownWidget(),
            
            # Colored select (automatically gets bg_color, txt_color)
            'status': ColoredSelectDropdownWidget(),
            
            # Date and time
            'created_at': DateTimePickerWidget(),
            'updated_at': DateTimePickerWidget(),
            
            # Active status (red background for "No")
            'is_active': ActiveStatusDropdownWidget(),
            
            # Styled text inputs
            'name': TextInputWidget(),
            'sku': TextInputWidget(attrs={'placeholder': 'Product SKU'}),
            'description': TextInputWidget(),
        }

# Filters with widgets
class ProductFilter(django_filters.FilterSet):
    # Date range
    created_at = django_filters.DateFromToRangeFilter(
        widget=DateRangePickerWidget(),
        label="Created Date"
    )
    
    # Multi-select categories
    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=MultiSelectDropdownWidget(),
        label="Categories"
    )
    
    # Active status
    is_active = django_filters.BooleanFilter(
        widget=ActiveStatusDropdownWidget(),
        label="Active"
    )
    
    class Meta:
        model = Product
        fields = ['name', 'sku', 'is_active', 'categories']

# Table configuration with colors and badges
TABLE_CONFIG = [
    {
        "label": "Name",
        "field": "name",
        "value": lambda obj: obj.name,
        "url": lambda obj: ("app:product_update", {"pk": obj.pk}),
    },
    {
        "label": "Status",
        "field": "status__name", 
        "value": lambda obj: obj.status.name if obj.status else "-",
        "is_badge": True,
        "badge_data": lambda obj: [
            {
                "name": obj.status.name,
                "background_color": obj.status.bg_color.replace('#', ''),
                "text_color": obj.status.txt_color.replace('#', '')
            }
        ] if obj.status else [],
    },
    {
        "label": "Active",
        "field": "is_active",
        "value": lambda obj: "Active" if obj.is_active else "Inactive",
        "is_badge": True,
        "badge_data": lambda obj: [
            {
                "name": "Active" if obj.is_active else "Inactive",
                "background_color": "green-100" if obj.is_active else "red-600",
                "text_color": "green-800" if obj.is_active else "white"
            }
        ],
    },
]

# Form sections
FORM_SECTIONS = [
    {
        "title": "Basic Info",
        "columns": 4,
        "fields": ["name", "sku", "status", "is_active"]
    },
    {
        "title": "Categories",
        "columns": 2,
        "fields": ["categories", "primary_category"]
    },
    {
        "title": "Timestamps",
        "columns": 2,
        "fields": ["created_at", "updated_at"]
    },
]

# Create CRUD views
crud = create_crud(Product, ProductForm, ProductFilter)

product_list = crud['list'](
    TABLE_CONFIG,
    page_title="Products with Colors and Badges"
)

product_create = crud['create'](
    FORM_SECTIONS,
    page_title="New Product with Custom Widgets"
)

product_update = crud['update'](
    FORM_SECTIONS,
    readonly_fields=["sku", "created_at"],
    page_title="Edit Product"
)