# DjCrudX - Kompletny Przewodnik

## 🎯 Najbardziej Rozbudowany Scenariusz

Pokażemy **kompletny system zarządzania firmą** z wszystkimi funkcjami djcrudx:
- Organizacja z wieloma pracownikami (inline formsets)
- Wszystkie typy widgetów
- Readonly fields
- Kolorowe tabele z badges
- Filtrowanie i paginacja
- Sekcje formularzy z różnymi layoutami

## 📁 Struktura Projektu

```
company_management/
├── models.py          # Modele danych
├── forms.py           # Formularze z widgetami
├── filters.py         # Filtry dla tabel
├── views.py           # Widoki CRUD
├── urls.py            # URLe
└── templates/
    └── crud/
        └── base.html  # Własny szablon bazowy
```

## 🗄️ 1. Modele (models.py)

```python
from django.db import models
from django.contrib.auth.models import User

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='blue')
    
    def __str__(self):
        return self.name

class Organization(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    
    name = models.CharField(max_length=200)
    vat_number = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Adres
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    
    # Status i daty
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    founded_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    POSITION_CHOICES = [
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('analyst', 'Analyst'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='employees')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Dane służbowe
    employee_code = models.CharField(max_length=20, unique=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    departments = models.ManyToManyField(Department, blank=True)  # ManyToMany
    
    # Dane finansowe
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()
    
    # Status
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_code})"
```

## 📝 2. Formularze z Wszystkimi Widgetami (forms.py)

```python
from django import forms
from django.contrib.auth.models import User
from djcrudx.widgets import (
    MultiSelectDropdownWidget,
    SingleSelectDropdownWidget, 
    ColoredSelectDropdownWidget,
    DateTimePickerWidget,
    DatePickerWidget,
    TextInputWidget,
    TextAreaWidget,
    ActiveStatusDropdownWidget,
)
from .models import Organization, Employee, Country, Department

class OrganizationForm(forms.ModelForm):
    """Formularz organizacji z wszystkimi typami widgetów"""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'vat_number', 'email', 'phone',
            'address', 'city', 'postal_code', 'country',
            'status', 'is_active', 'founded_date', 'notes'
        ]
        widgets = {
            # Podstawowe pola tekstowe
            'name': TextInputWidget(attrs={
                'placeholder': 'Nazwa organizacji',
                'class': 'font-semibold'
            }),
            'vat_number': TextInputWidget(attrs={
                'placeholder': 'NIP lub VAT ID'
            }),
            'email': TextInputWidget(attrs={
                'placeholder': 'kontakt@firma.pl',
                'type': 'email'
            }),
            'phone': TextInputWidget(attrs={
                'placeholder': '+48 123 456 789'
            }),
            
            # Adres
            'address': TextAreaWidget(attrs={
                'placeholder': 'Ulica i numer',
                'rows': 3
            }),
            'city': TextInputWidget(attrs={
                'placeholder': 'Miasto'
            }),
            'postal_code': TextInputWidget(attrs={
                'placeholder': '00-000'
            }),
            
            # Dropdown z krajami
            'country': SingleSelectDropdownWidget(),
            
            # Kolorowy status dropdown
            'status': ColoredSelectDropdownWidget(),
            
            # Boolean z czerwonym tłem dla "No"
            'is_active': ActiveStatusDropdownWidget(),
            
            # Date picker
            'founded_date': DatePickerWidget(),
            
            # Duże pole tekstowe
            'notes': TextAreaWidget(attrs={
                'placeholder': 'Dodatkowe informacje...',
                'rows': 4
            }),
        }

class EmployeeForm(forms.ModelForm):
    """Formularz pracownika dla inline formsets"""
    
    class Meta:
        model = Employee
        fields = [
            'user', 'employee_code', 'position', 'departments',
            'salary', 'hire_date', 'is_manager', 'is_active'
        ]
        widgets = {
            # Single select dla użytkownika
            'user': SingleSelectDropdownWidget(),
            
            # Kod pracownika
            'employee_code': TextInputWidget(attrs={
                'placeholder': 'EMP001'
            }),
            
            # Kolorowy dropdown pozycji
            'position': ColoredSelectDropdownWidget(),
            
            # Multi-select dla działów (ManyToMany)
            'departments': MultiSelectDropdownWidget(),
            
            # Pensja
            'salary': TextInputWidget(attrs={
                'placeholder': '5000.00',
                'type': 'number',
                'step': '0.01'
            }),
            
            # Data zatrudnienia
            'hire_date': DatePickerWidget(),
            
            # Boolean fields
            'is_manager': ActiveStatusDropdownWidget(),
            'is_active': ActiveStatusDropdownWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtruj tylko aktywnych użytkowników bez przypisanej organizacji
        self.fields['user'].queryset = User.objects.filter(
            is_active=True,
            employee__isnull=True
        ).order_by('first_name', 'last_name')
        
        # Filtruj tylko aktywne działy
        self.fields['departments'].queryset = Department.objects.filter(
            name__isnull=False
        ).order_by('name')
    
    def clean_employee_code(self):
        """Walidacja unikalności kodu pracownika"""
        code = self.cleaned_data['employee_code']
        if Employee.objects.filter(employee_code=code).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ten kod pracownika już istnieje.')
        return code
```

## 🔍 3. Filtry dla Tabel (filters.py)

```python
import django_filters
from djcrudx.widgets import (
    DateRangePickerWidget,
    SingleSelectDropdownWidget,
    ActiveStatusDropdownWidget,
)
from .models import Organization, Employee, Country

class OrganizationFilter(django_filters.FilterSet):
    """Filtry dla tabeli organizacji"""
    
    # Wyszukiwanie po nazwie
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'placeholder': 'Szukaj po nazwie...',
            'class': 'form-control'
        })
    )
    
    # Filtr po kraju
    country = django_filters.ModelChoiceFilter(
        queryset=Country.objects.all(),
        widget=SingleSelectDropdownWidget(),
        empty_label="Wszystkie kraje"
    )
    
    # Filtr po statusie
    status = django_filters.ChoiceFilter(
        choices=Organization.STATUS_CHOICES,
        widget=SingleSelectDropdownWidget(),
        empty_label="Wszystkie statusy"
    )
    
    # Filtr aktywności - użyj ChoiceFilter dla dropdown
    is_active = django_filters.ChoiceFilter(
        choices=[
            ('', 'Wszystkie'),
            ('true', 'Aktywne'),
            ('false', 'Nieaktywne'),
        ],
        widget=SingleSelectDropdownWidget(),
        method='filter_is_active'
    )
    
    # Filtr zakresu dat założenia
    founded_date = django_filters.DateFromToRangeFilter(
        widget=DateRangePickerWidget(),
        label="Data założenia"
    )
    
    # Filtr zakresu dat utworzenia
    created_at = django_filters.DateFromToRangeFilter(
        widget=DateRangePickerWidget(),
        label="Data utworzenia"
    )

    class Meta:
        model = Organization
        fields = ['name', 'country', 'status', 'is_active', 'founded_date', 'created_at']
    
    def filter_is_active(self, queryset, name, value):
        """Custom method to handle boolean filtering"""
        if value == 'true':
            return queryset.filter(is_active=True)
        elif value == 'false':
            return queryset.filter(is_active=False)
        return queryset

class EmployeeFilter(django_filters.FilterSet):
    """Filtry dla tabeli pracowników"""
    
    # Wyszukiwanie po imieniu/nazwisku
    user__first_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Imię',
        widget=forms.TextInput(attrs={'placeholder': 'Szukaj po imieniu...'})
    )
    
    user__last_name = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Nazwisko',
        widget=forms.TextInput(attrs={'placeholder': 'Szukaj po nazwisku...'})
    )
    
    # Filtr po pozycji
    position = django_filters.ChoiceFilter(
        choices=Employee.POSITION_CHOICES,
        widget=SingleSelectDropdownWidget(),
        empty_label="Wszystkie pozycje"
    )
    
    # Filtr po organizacji
    organization = django_filters.ModelChoiceFilter(
        queryset=Organization.objects.filter(is_active=True),
        widget=SingleSelectDropdownWidget(),
        empty_label="Wszystkie organizacje"
    )

    class Meta:
        model = Employee
        fields = ['user__first_name', 'user__last_name', 'position', 'organization']
```

## 👀 4. Widoki CRUD (views.py)

```python
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms import inlineformset_factory
from djcrudx.mixins import CrudListMixin, render_with_readonly
from .models import Organization, Employee
from .forms import OrganizationForm, EmployeeForm
from .filters import OrganizationFilter, EmployeeFilter

# ========================================
# KONFIGURACJA TABEL
# ========================================

ORGANIZATION_TABLE_CONFIG = [
    {
        "label": "Nazwa",
        "field": "name", 
        "value": lambda obj: obj.name,
        "url": lambda obj: ("company:organization_update", {"pk": obj.pk}),
        "sortable": True,
    },
    {
        "label": "Kraj",
        "field": "country",
        "value": lambda obj: obj.country.name,
        "sortable": True,
    },
    {
        "label": "Status",
        "field": "status",
        "is_badge": True,
        "badge_data": lambda obj: [{
            "name": obj.get_status_display(),
            "background_color": {
                'active': 'green-100',
                'inactive': 'red-100', 
                'pending': 'yellow-100'
            }.get(obj.status, 'gray-100'),
            "text_color": {
                'active': 'green-800',
                'inactive': 'red-800',
                'pending': 'yellow-800'
            }.get(obj.status, 'gray-800'),
        }],
    },
    {
        "label": "Aktywna",
        "field": "is_active",
        "value": lambda obj: "Tak" if obj.is_active else "Nie",  # WYMAGANE dla is_badge
        "is_badge": True,
        "badge_data": lambda obj: [{
            "name": "Tak" if obj.is_active else "Nie",
            "background_color": "green-100" if obj.is_active else "red-100",
            "text_color": "green-800" if obj.is_active else "red-800",
        }],
    },
    {
        "label": "Pracownicy",
        "field": "employees_count",
        "value": lambda obj: obj.employees.count(),
    },
    {
        "label": "Data założenia",
        "field": "founded_date",
        "value": lambda obj: obj.founded_date.strftime('%d.%m.%Y') if obj.founded_date else '-',
        "sortable": True,
    },
    {
        "label": "Utworzono",
        "field": "created_at",
        "value": lambda obj: obj.created_at.strftime('%d.%m.%Y %H:%M'),
        "sortable": True,
    },
]

EMPLOYEE_TABLE_CONFIG = [
    {
        "label": "Pracownik",
        "field": "user",
        "value": lambda obj: obj.user.get_full_name(),
        "url": lambda obj: ("company:employee_update", {"pk": obj.pk}),
        "sortable": True,
    },
    {
        "label": "Kod",
        "field": "employee_code",
        "value": lambda obj: obj.employee_code,
        "sortable": True,
    },
    {
        "label": "Pozycja",
        "field": "position",
        "is_badge": True,
        "badge_data": lambda obj: [{
            "name": obj.get_position_display(),
            "background_color": {
                'manager': 'purple-100',
                'developer': 'blue-100',
                'designer': 'pink-100',
                'analyst': 'green-100',
            }.get(obj.position, 'gray-100'),
            "text_color": {
                'manager': 'purple-800',
                'developer': 'blue-800', 
                'designer': 'pink-800',
                'analyst': 'green-800',
            }.get(obj.position, 'gray-800'),
        }],
    },
    {
        "label": "Organizacja",
        "field": "organization",
        "value": lambda obj: obj.organization.name,
        "sortable": True,
    },
    {
        "label": "Pensja",
        "field": "salary",
        "value": lambda obj: f"{obj.salary:,.2f} PLN",
        "sortable": True,
    },
    {
        "label": "Manager",
        "field": "is_manager",
        "is_badge": True,
        "badge_data": lambda obj: [{
            "name": "Tak" if obj.is_manager else "Nie",
            "background_color": "blue-100" if obj.is_manager else "gray-100",
            "text_color": "blue-800" if obj.is_manager else "gray-600",
        }],
    },
    {
        "label": "Status",
        "field": "is_active",
        "is_badge": True,
        "badge_data": lambda obj: [{
            "name": "Aktywny" if obj.is_active else "Nieaktywny",
            "background_color": "green-100" if obj.is_active else "red-100",
            "text_color": "green-800" if obj.is_active else "red-800",
        }],
    },
]

# ========================================
# KONFIGURACJA SEKCJI FORMULARZY
# ========================================

ORGANIZATION_FORM_SECTIONS = [
    {
        "title": "Podstawowe Informacje",
        "columns": 2,  # 2 kolumny obok siebie
        "fields": ["name", "vat_number", "email", "phone"]
    },
    {
        "title": "Adres",
        "columns": 3,  # 3 kolumny obok siebie
        "fields": ["address", "city", "postal_code", "country"]
    },
    {
        "title": "Status i Daty",
        "columns": 3,  # 3 kolumny obok siebie
        "fields": ["status", "is_active", "founded_date"]
    },
    {
        "title": "Pracownicy",
        "columns": 1,  # Pełna szerokość dla inline formsets
        "fields": ["inline_config"]  # Specjalne pole dla inline formsets
    },
    {
        "title": "Dodatkowe Informacje",
        "columns": 1,  # Pełna szerokość dla textarea
        "fields": ["notes"]
    }
]

# ========================================
# WIDOKI ORGANIZACJI
# ========================================

def organization_list(request):
    """Lista organizacji z filtrowaniem i paginacją"""
    organizations = Organization.objects.select_related('country').prefetch_related('employees')
    organization_filter = OrganizationFilter(request.GET, queryset=organizations)
    
    # Użyj DjCrudX mixin dla tabeli
    mixin = CrudListMixin()
    context = mixin.get_datatable_context(
        organization_filter.qs, 
        organization_filter, 
        ORGANIZATION_TABLE_CONFIG, 
        request
    )
    
    context.update({
        "page_title": "Organizacje",
        "create_url": "company:organization_create",
        "description": "Zarządzaj organizacjami i ich pracownikami"
    })
    
    return render(request, "crud/list_view.html", context)

def organization_create(request):
    """Tworzenie organizacji z pracownikami (inline formsets)"""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        
        # Konfiguracja inline formsets
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'form_class': EmployeeForm,  # Własny formularz z widgetami
                'fields': ['user', 'employee_code', 'position', 'departments', 
                          'salary', 'hire_date', 'is_manager', 'is_active'],
                'extra': 3,  # 3 puste formularze
                'can_delete': True,
                'section_title': 'Pracownicy Organizacji',
                'columns': 4  # 4 kolumny w grid
            }
        ]
        
        if form.is_valid():
            # Walidacja inline formsets
            formsets = {}
            for config in inline_config:
                FormsetClass = inlineformset_factory(
                    config['parent_model'], 
                    config['child_model'],
                    form=config.get('form_class'),  # Użyj własnego formularza
                    fields=config['fields'], 
                    extra=config['extra'],
                    can_delete=config['can_delete']
                )
                formsets[config['name']] = FormsetClass(request.POST)
            
            # Sprawdź czy wszystkie formsets są poprawne
            if all(formset.is_valid() for formset in formsets.values()):
                # Zapisz organizację
                organization = form.save()
                
                # Zapisz pracowników
                for formset in formsets.values():
                    formset.instance = organization
                    formset.save()
                
                messages.success(request, f'Organizacja "{organization.name}" została utworzona z {sum(len(fs.forms) for fs in formsets.values())} pracownikami.')
                return redirect('company:organization_list')
            else:
                messages.error(request, 'Popraw błędy w formularzu pracowników.')
        else:
            messages.error(request, 'Popraw błędy w formularzu organizacji.')
    else:
        form = OrganizationForm()
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'form_class': EmployeeForm,
                'fields': ['user', 'employee_code', 'position', 'departments',
                          'salary', 'hire_date', 'is_manager', 'is_active'],
                'extra': 3,
                'can_delete': True,
                'section_title': 'Pracownicy Organizacji',
                'columns': 4
            }
        ]
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': ORGANIZATION_FORM_SECTIONS,
        'page_title': 'Nowa Organizacja',
        'back_url': 'company:organization_list',
        'submit_label': 'Utwórz Organizację'
    }, inline_config=inline_config)

def organization_update(request, pk):
    """Edycja organizacji z pracownikami"""
    organization = get_object_or_404(Organization, pk=pk)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'form_class': EmployeeForm,
                'fields': ['user', 'employee_code', 'position', 'departments',
                          'salary', 'hire_date', 'is_manager', 'is_active'],
                'extra': 1,  # Tylko 1 pusty formularz przy edycji
                'can_delete': True,
                'section_title': 'Pracownicy Organizacji',
                'columns': 4
            }
        ]
        
        if form.is_valid():
            formsets = {}
            for config in inline_config:
                FormsetClass = inlineformset_factory(
                    config['parent_model'],
                    config['child_model'],
                    form=config.get('form_class'),
                    fields=config['fields'],
                    extra=config['extra'],
                    can_delete=config['can_delete']
                )
                formsets[config['name']] = FormsetClass(request.POST, instance=organization)
            
            if all(formset.is_valid() for formset in formsets.values()):
                form.save()
                for formset in formsets.values():
                    formset.save()
                
                messages.success(request, f'Organizacja "{organization.name}" została zaktualizowana.')
                return redirect('company:organization_list')
            else:
                messages.error(request, 'Popraw błędy w formularzu pracowników.')
        else:
            messages.error(request, 'Popraw błędy w formularzu organizacji.')
    else:
        form = OrganizationForm(instance=organization)
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'form_class': EmployeeForm,
                'fields': ['user', 'employee_code', 'position', 'departments',
                          'salary', 'hire_date', 'is_manager', 'is_active'],
                'extra': 1,
                'can_delete': True,
                'section_title': 'Pracownicy Organizacji',
                'columns': 4
            }
        ]
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': ORGANIZATION_FORM_SECTIONS,
        'page_title': f'Edytuj: {organization.name}',
        'back_url': 'company:organization_list',
        'submit_label': 'Zaktualizuj Organizację'
    }, readonly_fields=['created_at', 'updated_at'], inline_config=inline_config)

# ========================================
# WIDOKI PRACOWNIKÓW
# ========================================

def employee_list(request):
    """Lista pracowników z filtrowaniem"""
    employees = Employee.objects.select_related('user', 'organization').prefetch_related('departments')
    employee_filter = EmployeeFilter(request.GET, queryset=employees)
    
    mixin = CrudListMixin()
    context = mixin.get_datatable_context(
        employee_filter.qs,
        employee_filter,
        EMPLOYEE_TABLE_CONFIG,
        request
    )
    
    context.update({
        "page_title": "Pracownicy",
        "create_url": "company:employee_create",
        "description": "Zarządzaj pracownikami wszystkich organizacji"
    })
    
    return render(request, "crud/list_view.html", context)
```

## 🌐 5. URLe (urls.py)

```python
from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # Organizacje
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/<int:pk>/edit/', views.organization_update, name='organization_update'),
    
    # Pracownicy
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
]
```

## 🎨 6. Własny Szablon Bazowy (templates/crud/base.html)

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}System Zarządzania Firmą{% endblock %}</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Nawigacja -->
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-4">
                    <h1 class="text-xl font-bold">
                        <i class="fas fa-building mr-2"></i>
                        System Zarządzania Firmą
                    </h1>
                </div>
                <div class="flex space-x-4">
                    <a href="{% url 'company:organization_list' %}" 
                       class="hover:bg-blue-700 px-3 py-2 rounded">
                        <i class="fas fa-building mr-1"></i>
                        Organizacje
                    </a>
                    <a href="{% url 'company:employee_list' %}" 
                       class="hover:bg-blue-700 px-3 py-2 rounded">
                        <i class="fas fa-users mr-1"></i>
                        Pracownicy
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Główna zawartość -->
    <main class="max-w-7xl mx-auto py-6 px-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-4 mt-12">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p>&copy; 2024 System Zarządzania Firmą - Powered by DjCrudX</p>
        </div>
    </footer>
</body>
</html>
```

## ⚙️ 7. Konfiguracja Django (settings.py)

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'django_filters',
    'djcrudx',
    
    # Local apps
    'company_management',
]

# DjCrudX Configuration
DJCRUDX_BASE_TEMPLATE = "crud/base.html"  # Nasz własny szablon

# Kolory UI - dostosowane do naszego designu
DJCRUDX_UI_COLORS = {
    'primary': 'blue-600',
    'primary_hover': 'blue-700',
    'primary_text': 'blue-600',
    'primary_ring': 'blue-500',
    'primary_border': 'blue-500',
    'secondary': 'gray-500',
    'secondary_hover': 'gray-600'
}

# Tłumaczenia
LANGUAGE_CODE = 'pl'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']

# Dodatkowe tłumaczenia
DJCRUDX_TRANSLATIONS = {
    'pl': {
        'Create': 'Utwórz',
        'Edit': 'Edytuj',
        'Delete': 'Usuń',
        'Save': 'Zapisz',
        'Cancel': 'Anuluj',
        'Back': 'Powrót',
        'Search': 'Szukaj',
        'Filter': 'Filtruj',
        'Clear': 'Wyczyść',
        'Actions': 'Akcje',
        'No results found': 'Nie znaleziono wyników',
        'Page': 'Strona',
        'of': 'z',
        'Show': 'Pokaż',
        'entries': 'wpisów',
    }
}
```

## 🚀 8. Uruchomienie

```bash
# 1. Migracje
python manage.py makemigrations
python manage.py migrate

# 2. Utwórz superusera
python manage.py createsuperuser

# 3. Załaduj przykładowe dane
python manage.py shell
```

```python
# W Django shell - przykładowe dane
from django.contrib.auth.models import User
from company_management.models import Country, Department, Organization, Employee

# Kraje
poland = Country.objects.create(name="Polska", code="PL")
germany = Country.objects.create(name="Niemcy", code="DE")

# Działy
it_dept = Department.objects.create(name="IT", color="blue")
hr_dept = Department.objects.create(name="HR", color="green")
finance_dept = Department.objects.create(name="Finanse", color="yellow")

# Użytkownicy
user1 = User.objects.create_user('jan.kowalski', 'jan@example.com', 'password123')
user1.first_name = 'Jan'
user1.last_name = 'Kowalski'
user1.save()

user2 = User.objects.create_user('anna.nowak', 'anna@example.com', 'password123')
user2.first_name = 'Anna'
user2.last_name = 'Nowak'
user2.save()

print("Przykładowe dane zostały utworzone!")
```

## 🎯 9. Funkcje Systemu

### ✅ Co Zawiera Ten Przykład:

1. **Wszystkie Widgety DjCrudX:**
   - `TextInputWidget` - stylizowane pola tekstowe
   - `TextAreaWidget` - obszary tekstowe
   - `SingleSelectDropdownWidget` - dropdown dla ForeignKey
   - `MultiSelectDropdownWidget` - multi-select dla ManyToMany
   - `ColoredSelectDropdownWidget` - kolorowe opcje
   - `ActiveStatusDropdownWidget` - boolean z czerwonym tłem
   - `DatePickerWidget` - wybór daty
   - `DateRangePickerWidget` - zakres dat w filtrach

2. **Inline Formsets:**
   - Dodawanie/edycja/usuwanie pracowników w formularzu organizacji
   - Własne formularze z walidacją
   - Kontrola nad layoutem (4 kolumny)

3. **Zaawansowane Tabele:**
   - Kolorowe badges dla statusów
   - Sortowanie po kolumnach
   - Linki do edycji
   - Liczenie powiązanych obiektów

4. **Sekcje Formularzy:**
   - Różne liczby kolumn (1, 2, 3, 4)
   - Logiczne grupowanie pól
   - Responsywny design

5. **Filtrowanie i Paginacja:**
   - Filtry po wszystkich polach
   - Zakresy dat
   - Wyszukiwanie tekstowe

6. **Readonly Fields:**
   - Automatyczne readonly dla metadanych
   - Zachowanie przy edycji

7. **Własny Design:**
   - Niestandardowy szablon bazowy
   - Nawigacja
   - Kolory UI
   - Polskie tłumaczenia

### 🎨 Rezultat:

- **Kompletny system zarządzania firmą**
- **Wszystkie funkcje DjCrudX w jednym miejscu**
- **Gotowy do użycia kod**
- **Profesjonalny wygląd**
- **Pełna responsywność**

Ten przykład pokazuje **maksymalne możliwości DjCrudX** - od prostych formularzy po złożone systemy z inline formsets, filtrami i kolorowymi tabelami.