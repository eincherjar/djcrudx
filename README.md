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
# views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from djcrudx.mixins import CrudListMixin, render_with_readonly
from .models import Product
from .forms import ProductForm
from .filters import ProductFilter

# Table configuration
TABLE_CONFIG = [
    {
        "label": "Name",
        "field": "name",
        "value": lambda obj: obj.name,
        "url": lambda obj: ("app:product_update", {"pk": obj.pk}),
    },
    {
        "label": "Price",
        "field": "price",
        "value": lambda obj: f"${obj.price}",
    },
]

# Form sections - kontroluje layout i grupowanie pól
FORM_SECTIONS = [
    {
        "title": "Basic Information",
        "columns": 2,  # 2 kolumny w grid
        "fields": ["name", "description", "category"]
    },
    {
        "title": "Pricing & Stock", 
        "columns": 3,  # 3 kolumny w grid
        "fields": ["price", "cost", "stock_quantity"]
    },
    {
        "title": "Metadata",
        "columns": 1,  # 1 kolumna - pełna szerokość
        "fields": ["created_at", "updated_at"]
    }
]

def product_list(request):
    """List view with automatic datatable"""
    products = Product.objects.all()
    product_filter = ProductFilter(request.GET, queryset=products)
    
    # Use DjCrudX mixin for datatable
    mixin = CrudListMixin()
    context = mixin.get_datatable_context(
        product_filter.qs, product_filter, TABLE_CONFIG, request
    )
    
    context.update({
        "page_title": "Products",
        "create_url": "app:product_create"
    })
    
    return render(request, "crud/list_view.html", context)

def product_create(request):
    """Create view with form sections"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('app:product_list')
    else:
        form = ProductForm()
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': FORM_SECTIONS,  # Sekcje kontrolują layout
        'page_title': 'New Product',
        'back_url': 'app:product_list',  # URL powrotu
        'submit_label': 'Create Product'  # Tekst przycisku
    })

def product_update(request, pk):
    """Update view with readonly fields"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('app:product_list')
    else:
        form = ProductForm(instance=product)
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': FORM_SECTIONS,  # Te same sekcje
        'page_title': 'Edit Product',
        'back_url': 'app:product_list',
        'submit_label': 'Update Product'
    }, readonly_fields=['created_at', 'updated_at', 'id'])  # Readonly metadata
```

### 2. Advanced Widgets

```python
from django import forms
from djcrudx.widgets import (
    MultiSelectDropdownWidget,
    SingleSelectDropdownWidget,
    ColoredSelectDropdownWidget,
    DateTimePickerWidget,
    DateRangePickerWidget,
    TextInputWidget,
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'categories': MultiSelectDropdownWidget(),      # ManyToMany
            'category': SingleSelectDropdownWidget(),       # ForeignKey
            'status': ColoredSelectDropdownWidget(),        # Colored options
            'created_at': DateTimePickerWidget(),           # DateTime picker
            'name': TextInputWidget(attrs={'placeholder': 'Product name'}),
        }
```

### 3. Forms with Inline Formsets (Related Objects)

```python
# views.py - Universal inline formsets
from djcrudx.inline_mixins import render_with_inlines
from django.forms import inlineformset_factory

def organization_create(request):
    """Create organization with employees"""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        
        # Inline configuration
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'extra': 3,
                'can_delete': True,
                'section_title': 'Pracownicy',
                'columns': 4
            }
        ]
        
        # Validate main form
        if form.is_valid():
            # Validate inline formsets
            formsets = {}
            for config in inline_config:
                formset_class = inlineformset_factory(
                    config['parent_model'], config['child_model'],
                    fields=config['fields'], extra=config['extra'],
                    can_delete=config['can_delete']
                )
                formsets[config['name']] = formset_class(request.POST)
            
            if all(formset.is_valid() for formset in formsets.values()):
                organization = form.save()
                for formset in formsets.values():
                    formset.instance = organization
                    formset.save()
                return redirect('app:organization_list')
    else:
        form = OrganizationForm()
        inline_config = [{
            'name': 'employees',
            'parent_model': Organization,
            'child_model': Employee,
            'fields': ['user', 'code', 'position', 'is_manager'],
            'extra': 3,
            'can_delete': True,
            'section_title': 'Pracownicy',
            'columns': 4
        }]
    
    form_sections = [
        {
            "title": "Organization Info",
            "columns": 2,
            "fields": ["name", "vat_number"]
        }
    ]
    
    return render_with_inlines(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': form_sections,
        'page_title': 'New Organization'
    }, inline_config=inline_config)
```

### 4. URL Configuration

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

- **MultiSelectDropdownWidget** - Multi-select with checkboxes (ManyToMany fields)
- **SingleSelectDropdownWidget** - Single select with radio buttons (ForeignKey fields)
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

## 🔧 Helper Functions

### render_with_readonly()
Automatic base template and readonly field handling:

```python
from djcrudx.mixins import render_with_readonly

# Automatic base template + readonly fields
return render_with_readonly(request, 'crud/form_view.html', context, readonly_fields=['id'])
```

### render_with_inlines()
Universal inline formsets support:

```python
from djcrudx.inline_mixins import render_with_inlines

# Same template, with inline formsets
return render_with_inlines(request, 'crud/form_view.html', context, inline_config=inline_config)
```

### Mixins Available
- **CrudListMixin** - Complete list view with pagination and filtering
- **ReadonlyFormMixin** - Automatic readonly fields for class-based views
- **PaginationMixin** - Easy pagination handling
- **DataTableMixin** - Table generation from configuration
- **InlineFormsetMixin** - Universal inline formsets handling

## 🔒 Permissions (Optional)

The library supports optional permission integration:

```python
from djcrudx import create_crud_views  # Full version with permissions

# Requires permissions app with:
# - @require_view_permission decorator
# - get_filtered_queryset function
```

## 🎯 Praktyczne Przykłady

### Kompleksny formularz pracownika

```python
# views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from djcrudx.mixins import render_with_readonly
from .models import Employee
from .forms import EmployeeForm

# Sekcje formularza - kontrolują layout i grupowanie
EMPLOYEE_FORM_SECTIONS = [
    {
        "title": "Personal Information",
        "columns": 2,  # 2 kolumny obok siebie
        "fields": ["first_name", "last_name", "email", "phone"]
    },
    {
        "title": "Job Details",
        "columns": 3,  # 3 kolumny obok siebie
        "fields": ["position", "department", "salary", "hire_date"]
    },
    {
        "title": "Status & Metadata",
        "columns": 1,  # 1 kolumna - pełna szerokość
        "fields": ["is_active", "created_at", "updated_at"]
    }
]

def employee_create(request):
    """Create new employee with sectioned form"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.first_name} {employee.last_name} created.')
            return redirect('app:employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm()
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': EMPLOYEE_FORM_SECTIONS,
        'page_title': 'New Employee',
        'back_url': 'app:employee_list',
        'submit_label': 'Create Employee'
    })

def employee_update(request, pk):
    """Update employee with readonly metadata"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {employee.first_name} {employee.last_name} updated.')
            return redirect('app:employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm(instance=employee)
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': EMPLOYEE_FORM_SECTIONS,  # Te same sekcje
        'page_title': f'Edit {employee.first_name} {employee.last_name}',
        'back_url': 'app:employee_list',
        'submit_label': 'Update Employee'
    }, readonly_fields=['created_at', 'updated_at'])  # Metadata readonly
```

### Różne layouty dla różnych formularzy

```python
# Prosty formularz kategorii - 1 sekcja
CATEGORY_FORM_SECTIONS = [
    {
        "title": "Category Details",
        "columns": 1,
        "fields": ["name", "description", "is_active"]
    }
]

# Złożony formularz produktu - wiele sekcji
PRODUCT_FORM_SECTIONS = [
    {
        "title": "Basic Info",
        "columns": 2,
        "fields": ["name", "code", "category", "brand"]
    },
    {
        "title": "Pricing",
        "columns": 4,  # 4 kolumny dla cen
        "fields": ["price", "cost", "margin", "tax_rate"]
    },
    {
        "title": "Inventory",
        "columns": 3,
        "fields": ["stock_quantity", "min_stock", "max_stock"]
    },
    {
        "title": "Description",
        "columns": 1,  # Pełna szerokość dla textarea
        "fields": ["description", "notes"]
    }
]

def category_create(request):
    """Simple category form"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:category_list')
    else:
        form = CategoryForm()
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': CATEGORY_FORM_SECTIONS,  # Prosty layout
        'page_title': 'New Category'
    })

def product_create(request):
    """Complex product form"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:product_list')
    else:
        form = ProductForm()
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': PRODUCT_FORM_SECTIONS,  # Złożony layout
        'page_title': 'New Product'
    })
```

### Responsywny layout i walidacja

```python
# Responsywne sekcje - automatycznie dostosowują się do ekranu
CONTACT_FORM_SECTIONS = [
    {
        "title": "Contact Info",
        "columns": 2,  # Desktop: 2 kolumny, Mobile: 1 kolumna
        "fields": ["email", "phone", "address", "city"]
    },
    {
        "title": "Social Media",
        "columns": 3,  # Desktop: 3 kolumny, Mobile: 1 kolumna
        "fields": ["facebook", "twitter", "linkedin"]
    }
]

def contact_create(request):
    """Contact form with error handling"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f'Contact {contact.email} created successfully!')
            return redirect('app:contact_list')
        else:
            # Błędy są automatycznie wyświetlane pod polami
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': CONTACT_FORM_SECTIONS,
        'page_title': 'New Contact',
        'back_url': 'app:contact_list'
    })
```

### URLs Configuration

```python
# urls.py
from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    
    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
]
```

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
- ✅ **Universal inline formsets** - Add/edit/delete related objects in one form
- ✅ **Smart template inheritance** - `{% extends base_template|default:"crud/base.html" %}`
- ✅ **UI color customization** - `DJCRUDX_UI_COLORS` in settings
- ✅ **Advanced widgets** - MultiSelect, SingleSelect, ColoredSelect, DateTime
- ✅ **Responsive design** - Tailwind CSS + Alpine.js
- ✅ **Polish translations** - Built-in i18n support
- ✅ **One template for everything** - `crud/form_view.html` handles all cases

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
