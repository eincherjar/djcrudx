s# DjCrudX

Universal Django CRUD library with advanced widgets and features.

## 🚀 Features

- **Automatic CRUD views** - List, Create, Update, Delete, Detail
- **Advanced widgets** - MultiSelect, DateRange, ColoredSelect, DateTime
- **Filtering & Sorting** - Built-in django-filter integration
- **Pagination** - Automatic pagination with customizable page sizes
- **Permissions** - Optional permission system integration
- **Responsive design** - Tailwind CSS + Alpine.js
- **Readonly fields** - Automatic readonly field handling
- **Badges & Colors** - Rich table display with colored badges

## 📦 Installation

```bash
pip install djcrudx
```

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'djcrudx',
    # ...
]
```

## 🎯 Quick Start

### 1. Basic CRUD Views

```python
from djcrudx import create_crud
from .models import Product
from .forms import ProductForm
from .filters import ProductFilter

# Table configuration with filters
TABLE_CONFIG = [
    {
        "label": "Name",
        "field": "name",
        "value": lambda obj: obj.name,
        "url": lambda obj: ("app:product_update", {"pk": obj.pk}),
        "filter_field": product_filter.form['name'],  # Add filter input to column
    },
    {
        "label": "Price",
        "field": "price",
        "value": lambda obj: f"${obj.price}",
        # No filter for this column
    },
]

# Form sections
FORM_SECTIONS = [
    {
        "title": "Basic Info",
        "columns": 2,
        "fields": ["name", "price"]
    }
]

# Create CRUD views
crud = create_crud(Product, ProductForm, ProductFilter)

product_list = crud['list'](
    TABLE_CONFIG,
    page_title="Products",
    create_url="app:product_create",
    base_template="admin_base.html"  # Optional: custom base template
)

product_create = crud['create'](
    FORM_SECTIONS,
    page_title="New Product"
)
```

### 2. Advanced Widgets

```python
from django import forms
from djcrudx.widgets import (
    MultiSelectDropdownWidget,
    ColoredSelectDropdownWidget,
    DateTimePickerWidget,
    DateRangePickerWidget,
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'categories': MultiSelectDropdownWidget(),
            'status': ColoredSelectDropdownWidget(),
            'created_at': DateTimePickerWidget(),
        }
```

### 3. URL Configuration

```python
# urls.py
from django.urls import path

urlpatterns = [
    path('products/', product_list, name='product_list'),
    path('products/create/', product_create, name='product_create'),
    path('products/<int:pk>/edit/', product_update, name='product_update'),
    path('products/<int:pk>/', product_detail, name='product_detail'),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),
]
```

## 🎨 Template Customization

DjCrudX allows flexible template customization:

### Base Template Configuration

**Global configuration (settings.py):**
```python
# Use your own base template globally
DJCRUDX_BASE_TEMPLATE = "your_base.html"

# Customize UI colors
DJCRUDX_UI_COLORS = {
    'primary': 'blue-500',
    'primary_hover': 'blue-600', 
    'primary_text': 'blue-600',
    'primary_ring': 'blue-500',
    'primary_border': 'blue-500',
    'secondary': 'slate-500',
    'secondary_hover': 'slate-600'
}
```

**Per-view configuration:**
```python
# In your view
context.update({
    "base_template": "special_base.html",  # Overrides global setting
})
```

**Priority order:**
1. View context (`base_template` in context) - highest
2. Settings (`DJCRUDX_BASE_TEMPLATE`)
3. Default (`crud/base.html`) - fallback

### Template Override

You can also override any template by creating the same path in your project:
```
your_project/
├── templates/
│   └── crud/
│       ├── base.html          # Your custom base
│       ├── list_view.html     # Custom list view
│       └── _partials/
│           └── pagination.html # Custom pagination
```

## 🌍 Internationalization

DjCrudX supports **3 translation methods** in priority order:

### 1. Django i18n (highest priority)
```python
# settings.py
LANGUAGE_CODE = 'pl'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### 2. Custom translations in settings
```python
# settings.py
DJCRUDX_TRANSLATIONS = {
    'pl': {
        'Create': 'Dodaj nowy',
        'Edit': 'Modyfikuj',
    }
}
```

### 3. Built-in translations (fallback)
```python
# settings.py - JUST THIS!
LANGUAGE_CODE = 'pl'  # Automatic Polish translations
```

## 🎨 Available Widgets

- **MultiSelectDropdownWidget** - Multi-select with checkboxes
- **SingleSelectDropdownWidget** - Single select with radio buttons
- **ColoredSelectDropdownWidget** - Select with colored options
- **DateTimePickerWidget** - Date and time picker
- **DateRangePickerWidget** - Date range picker for filters
- **ActiveStatusDropdownWidget** - Boolean field with red background for "No"
- **TextInputWidget** - Styled text input

## 📊 Table Features

- **Sorting** - Click headers to sort (add `?ordering=field_name`)
- **Filtering** - Automatic filter forms with django-filter
- **Pagination** - Navigate pages with `?page=2&per_page=50`
- **Badges** - Colored badges in table cells
- **Links** - Clickable cells with URLs
- **Search** - Built-in search functionality

## 🔒 Permissions (Optional)

The library supports optional permission integration:

```python
from djcrudx import create_crud_views  # Full version with permissions

# Requires permissions app with:
# - @require_view_permission decorator
# - get_filtered_queryset function
```

## 🎯 Examples

### Colored Status Badges

```python
{
    "label": "Status",
    "field": "status",
    "is_badge": True,
    "badge_data": lambda obj: [
        {
            "name": obj.status.name,
            "background_color": "green-100" if obj.is_active else "red-100",
            "text_color": "green-800" if obj.is_active else "red-800"
        }
    ],
}
```

### Readonly Fields

```python
product_update = crud['update'](
    FORM_SECTIONS,
    readonly_fields=["created_at", "id"],  # These fields will be readonly
    page_title="Edit Product"
)
```

### Custom Filters

```python
class ProductFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter(
        widget=DateRangePickerWidget(),
        label="Created Date"
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'is_active']
```

## 🚀 Requirements

- Python 3.8+
- Django 4.0+
- django-filter 22.0+
- **Tailwind CSS** - Required for styling (included via CDN in templates)
- **Alpine.js** - Required for interactive widgets (included via CDN in templates)

### Frontend Dependencies

DjCrudX templates include Tailwind CSS and Alpine.js via CDN:

```html
<!-- Tailwind CSS for styling -->
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

<!-- Alpine.js for interactive widgets -->
<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

If you prefer to use your own Tailwind CSS setup, you can override the base template.

## 🔧 Fixed Issues

- ✅ Fixed pagination template path (`simple_pagination.html` → `pagination.html`)
- ✅ Fixed template variable names (`table_headers/table_rows` → `headers/rows`)
- ✅ Fixed import error in templatetags (`auto_translate` → `smart_translate`)
- ✅ Fixed missing pagination context variables
- ✅ Removed non-functional table views and column config buttons
- ✅ Added configurable base template support
- ✅ Fixed Polish translations in pagination

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
