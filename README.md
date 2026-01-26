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
from djcrudx.mixins import render_with_readonly
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

# List view - automatic base template handling
product_list = crud['list'](
    TABLE_CONFIG,
    page_title="Products",
    create_url="app:product_create"
)

# Form views with automatic base template and readonly support
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:product_list')
    else:
        form = ProductForm()
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': FORM_SECTIONS,
        'page_title': 'New Product'
    })

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('app:product_list')
    else:
        form = ProductForm(instance=product)
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': FORM_SECTIONS,
        'page_title': 'Edit Product'
    }, readonly_fields=['created_at', 'id'])  # Automatic readonly handling
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

DjCrudX provides **automatic base template handling** - no manual context needed!

### Base Template Configuration

**Global configuration (settings.py):**
```python
# Use your own base template globally - automatically applied!
DJCRUDX_BASE_TEMPLATE = "your_base.html"

# Customize UI colors
DJCRUDX_UI_COLORS = {
    'primary': 'orange-500',
    'primary_hover': 'orange-600', 
    'primary_text': 'orange-600',
    'primary_ring': 'orange-500',
    'primary_border': 'orange-500',
    'secondary': 'slate-500',
    'secondary_hover': 'slate-600'
}
```

**Automatic handling:**
```python
# ✅ Base template automatically added - no manual work!
from djcrudx.mixins import render_with_readonly

def my_view(request):
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        # base_template automatically added from settings!
    })
```

**Manual override (optional):**
```python
# Only if you need different template per view
context.update({
    "base_template": "special_base.html",  # Overrides global setting
})
```

**Priority order:**
1. View context (`base_template` in context) - highest
2. Settings (`DJCRUDX_BASE_TEMPLATE`) - **automatic**
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

### Readonly Fields - Automatic Handling

```python
# ✅ Automatic readonly with render_with_readonly helper
from djcrudx.mixins import render_with_readonly

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('app:product_list')
    else:
        form = ProductForm(instance=product)
    
    # Automatic readonly + base template handling!
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': FORM_SECTIONS,
        'page_title': 'Edit Product'
    }, readonly_fields=['created_at', 'id'])  # Auto-applied!

# ✅ Or use ReadonlyFormMixin in class-based views
from djcrudx.mixins import ReadonlyFormMixin

class ProductUpdateView(ReadonlyFormMixin, UpdateView):
    model = Product
    form_class = ProductForm
    readonly_fields = ['created_at', 'id']  # Automatic!
    template_name = 'crud/form_view.html'
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

## 🔧 Helper Functions

### render_with_readonly()
Automatic base template and readonly field handling:

```python
from djcrudx.mixins import render_with_readonly

# Automatic base template + readonly fields
return render_with_readonly(request, template, context, readonly_fields=['id'])
```

### Mixins Available
- **CrudListMixin** - Complete list view with pagination and filtering
- **ReadonlyFormMixin** - Automatic readonly fields for class-based views
- **PaginationMixin** - Easy pagination handling
- **DataTableMixin** - Table generation from configuration

### Frontend Dependencies

DjCrudX templates include Tailwind CSS and Alpine.js via CDN:

```html
<!-- Tailwind CSS for styling -->
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

<!-- Alpine.js for interactive widgets -->
<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

If you prefer to use your own Tailwind CSS setup, you can override the base template.

## 🚀 Key Features & Improvements

- ✅ **Automatic base template handling** - No manual context needed!
- ✅ **Automatic readonly fields** - Use `render_with_readonly()` helper
- ✅ **Smart template inheritance** - `{% extends base_template|default:"crud/base.html" %}`
- ✅ **UI color customization** - `DJCRUDX_UI_COLORS` in settings
- ✅ **Fixed pagination** - Correct template paths and variables
- ✅ **Fixed template tags** - All imports working correctly
- ✅ **Polish translations** - Built-in i18n support
- ✅ **Mixin architecture** - Reusable components for custom views

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
