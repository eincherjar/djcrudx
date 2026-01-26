# views.py - Przykład z modelami Organization, Employee, Position

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from djcrudx.mixins import CrudListMixin, render_with_readonly
from djcrudx.widgets import MultiSelectDropdownWidget, ColoredSelectDropdownWidget
from .models import Organization, Employee, Position
from .forms import OrganizationForm, EmployeeForm, PositionForm
from .filters import OrganizationFilter, EmployeeFilter

# =============================================================================
# ORGANIZATION VIEWS
# =============================================================================

# Sekcje formularza organizacji
ORGANIZATION_FORM_SECTIONS = [
    {
        "title": "Podstawowe informacje",
        "columns": 2,
        "fields": ["name", "vat_number"]
    },
    {
        "title": "Adres",
        "columns": 3,
        "fields": ["address", "postal_code", "city", "country"]
    },
    {
        "title": "Role i członkowie",
        "columns": 1,  # Pełna szerokość dla ManyToMany
        "fields": ["role", "members"]
    }
]

def organization_list(request):
    """Lista organizacji"""
    organizations = Organization.objects.all().prefetch_related('role', 'members')
    org_filter = OrganizationFilter(request.GET, queryset=organizations)

    table_config = [
        {
            "label": "Nazwa",
            "field": "name",
            "value": lambda obj: obj.name,
            "url": lambda obj: ("accounts:organization_update", {"pk": obj.pk}),
        },
        {
            "label": "NIP",
            "field": "vat_number",
            "value": lambda obj: obj.vat_number or "-",
        },
        {
            "label": "Miasto",
            "field": "city",
            "value": lambda obj: obj.city or "-",
        },
        {
            "label": "Role",
            "field": "role",
            "value": lambda obj: ", ".join([role.name for role in obj.role.all()]),
        },
        {
            "label": "Członkowie",
            "field": "members",
            "value": lambda obj: obj.members.count(),
        },
    ]

    mixin = CrudListMixin()
    context = mixin.get_datatable_context(
        org_filter.qs, org_filter, table_config, request
    )

    context.update({
        "page_title": "Organizacje",
        "create_url": "accounts:organization_create"
    })

    return render(request, "crud/list_view.html", context)

def organization_create(request):
    """Tworzenie organizacji"""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = form.save()
            messages.success(request, f'Organizacja {org.name} została utworzona.')
            return redirect('accounts:organization_list')
    else:
        form = OrganizationForm()

    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': ORGANIZATION_FORM_SECTIONS,
        'page_title': 'Nowa organizacja',
        'back_url': 'accounts:organization_list',
        'submit_label': 'Utwórz organizację'
    })

def organization_update(request, pk):
    """Edycja organizacji"""
    org = get_object_or_404(Organization, pk=pk)
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request, f'Organizacja {org.name} została zaktualizowana.')
            return redirect('accounts:organization_list')
    else:
        form = OrganizationForm(instance=org)

    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': ORGANIZATION_FORM_SECTIONS,
        'page_title': f'Edytuj {org.name}',
        'back_url': 'accounts:organization_list',
        'submit_label': 'Zapisz zmiany'
    })

# =============================================================================
# EMPLOYEE VIEWS
# =============================================================================

# Sekcje formularza pracownika
EMPLOYEE_FORM_SECTIONS = [
    {
        "title": "Podstawowe informacje",
        "columns": 2,
        "fields": ["user", "code"]
    },
    {
        "title": "Praca",
        "columns": 3,
        "fields": ["organization", "position", "is_manager"]
    },
    {
        "title": "Metadata",
        "columns": 1,
        "fields": ["joined_at"]
    }
]

def employee_list(request):
    """Lista pracowników"""
    employees = Employee.objects.select_related('user', 'organization', 'position')
    emp_filter = EmployeeFilter(request.GET, queryset=employees)

    table_config = [
        {
            "label": "Pracownik",
            "field": "user",
            "value": lambda obj: obj.user.get_full_name(),
            "url": lambda obj: ("accounts:employee_update", {"pk": obj.pk}),
        },
        {
            "label": "Kod",
            "field": "code",
            "value": lambda obj: obj.code or "-",
        },
        {
            "label": "Organizacja",
            "field": "organization",
            "value": lambda obj: obj.organization.name,
        },
        {
            "label": "Stanowisko",
            "field": "position",
            "value": lambda obj: obj.position.name,
        },
        {
            "label": "Manager",
            "field": "is_manager",
            "value": lambda obj: "Tak" if obj.is_manager else "Nie",
            "is_badge": True,
            "badge_data": lambda obj: [
                {
                    "name": "Manager" if obj.is_manager else "Pracownik",
                    "background_color": "blue-100" if obj.is_manager else "gray-100",
                    "text_color": "blue-800" if obj.is_manager else "gray-800"
                }
            ],
        },
    ]

    mixin = CrudListMixin()
    context = mixin.get_datatable_context(
        emp_filter.qs, emp_filter, table_config, request
    )

    context.update({
        "page_title": "Pracownicy",
        "create_url": "accounts:employee_create"
    })

    return render(request, "crud/list_view.html", context)

def employee_create(request):
    """Tworzenie pracownika"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            emp = form.save()
            messages.success(request, f'Pracownik {emp.user.get_full_name()} został dodany.')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeForm()

    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': EMPLOYEE_FORM_SECTIONS,
        'page_title': 'Nowy pracownik',
        'back_url': 'accounts:employee_list',
        'submit_label': 'Dodaj pracownika'
    })

def employee_update(request, pk):
    """Edycja pracownika"""
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pracownik {emp.user.get_full_name()} został zaktualizowany.')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeForm(instance=emp)

    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': EMPLOYEE_FORM_SECTIONS,
        'page_title': f'Edytuj {emp.user.get_full_name()}',
        'back_url': 'accounts:employee_list',
        'submit_label': 'Zapisz zmiany'
    }, readonly_fields=['joined_at'])  # Data dołączenia readonly

# =============================================================================
# POSITION VIEWS
# =============================================================================

# Prosty formularz stanowiska
POSITION_FORM_SECTIONS = [
    {
        "title": "Informacje o stanowisku",
        "columns": 1,
        "fields": ["name", "description"]
    }
]

def position_create(request):
    """Tworzenie stanowiska"""
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            pos = form.save()
            messages.success(request, f'Stanowisko {pos.name} zostało utworzone.')
            return redirect('accounts:position_list')
    else:
        form = PositionForm()

    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': POSITION_FORM_SECTIONS,
        'page_title': 'Nowe stanowisko',
        'back_url': 'accounts:position_list',
        'submit_label': 'Utwórz stanowisko'
    })

# =============================================================================
# FORMS.PY - Przykładowe formularze z widgetami
# =============================================================================

"""
# forms.py
from django import forms
from djcrudx.widgets import MultiSelectDropdownWidget, ColoredSelectDropdownWidget, TextInputWidget
from .models import Organization, Employee, Position, Role, User

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            "name",
            "vat_number",
            "address",
            "postal_code",
            "city",
            "country",
            "role",        # ManyToMany field
            "members",     # ManyToMany field
        ]
        widgets = {
            "name": TextInputWidget(attrs={"placeholder": "Nazwa"}),
            "vat_number": TextInputWidget(attrs={"placeholder": "NIP"}),
            "address": TextInputWidget(attrs={"placeholder": "Adres"}),
            "postal_code": TextInputWidget(attrs={"placeholder": "Kod pocztowy"}),
            "city": TextInputWidget(attrs={"placeholder": "Miasto"}),
            "country": TextInputWidget(attrs={"placeholder": "Kraj"}),
            "role": MultiSelectDropdownWidget(),     # ManyToMany widget
            "members": MultiSelectDropdownWidget(),  # ManyToMany widget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Konfiguracja pól ManyToMany
        self.fields["role"].queryset = Role.objects.all()
        self.fields["role"].label_from_instance = lambda obj: obj.name
        
        self.fields["members"].queryset = User.objects.filter(is_active=True)
        self.fields["members"].label_from_instance = (
            lambda obj: f"{obj.get_full_name() or obj.username}"
        )

    def save(self, commit=True):
        organization = super().save(commit=False)
        
        if commit:
            organization.save()
            # Zapisz relacje ManyToMany
            organization.role.set(self.cleaned_data.get("role", []))
            organization.members.set(self.cleaned_data.get("members", []))
            
        return organization

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'is_manager': ColoredSelectDropdownWidget(),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
"""

# =============================================================================
# UNIWERSALNE UŻYCIE INLINE FORMSETS
# =============================================================================

"""
# views.py - Uniwersalne użycie inline formsets
from djcrudx.mixins import render_with_inlines
from .models import Organization, Employee, Position, Role, User
from .forms import OrganizationForm, EmployeeInlineForm

def organization_create(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        
        # Konfiguracja inline formsets
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeInlineForm,  # Opcjonalne
                'extra': 3,
                'can_delete': True,
                'section_title': 'Pracownicy',
                'columns': 4  # Layout kolumn
            }
        ]
        
        # Walidacja głównego formularza
        if form.is_valid():
            # Sprawdź inline formsets
            formsets = {}
            for config in inline_config:
                formset_class = inlineformset_factory(
                    config['parent_model'],
                    config['child_model'],
                    form=config.get('form_class'),
                    fields=config['fields'],
                    extra=config.get('extra', 3),
                    can_delete=config.get('can_delete', True)
                )
                formsets[config['name']] = formset_class(request.POST)
            
            # Walidacja wszystkich formsets
            if all(formset.is_valid() for formset in formsets.values()):
                # Zapisz główny obiekt
                organization = form.save()
                
                # Zapisz inline formsets
                for formset in formsets.values():
                    formset.instance = organization
                    formset.save()
                
                messages.success(request, f'Organizacja {organization.name} została utworzona.')
                return redirect('accounts:organization_list')
    else:
        form = OrganizationForm()
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeInlineForm,
                'extra': 3,
                'can_delete': True,
                'section_title': 'Pracownicy',
                'columns': 4
            }
        ]
    
    # Sekcje głównego formularza
    form_sections = [
        {
            "title": "Podstawowe informacje",
            "columns": 2,
            "fields": ["name", "vat_number"]
        },
        {
            "title": "Adres",
            "columns": 3,
            "fields": ["address", "postal_code", "city", "country"]
        },
        {
            "title": "Role organizacji",
            "columns": 1,
            "fields": ["role"]
        }
    ]
    
    return render_with_inlines(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': form_sections,
        'page_title': 'Nowa organizacja',
        'back_url': 'accounts:organization_list',
        'submit_label': 'Utwórz organizację'
    }, inline_config=inline_config)

def organization_update(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeInlineForm,
                'extra': 1,  # Mniej pustych formularzy przy edycji
                'can_delete': True,
                'section_title': 'Pracownicy',
                'columns': 4
            }
        ]
        
        if form.is_valid():
            formsets = {}
            for config in inline_config:
                formset_class = inlineformset_factory(
                    config['parent_model'],
                    config['child_model'],
                    form=config.get('form_class'),
                    fields=config['fields'],
                    extra=config.get('extra', 1),
                    can_delete=config.get('can_delete', True)
                )
                formsets[config['name']] = formset_class(request.POST, instance=organization)
            
            if all(formset.is_valid() for formset in formsets.values()):
                form.save()
                for formset in formsets.values():
                    formset.save()
                
                messages.success(request, f'Organizacja {organization.name} została zaktualizowana.')
                return redirect('accounts:organization_list')
    else:
        form = OrganizationForm(instance=organization)
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeInlineForm,
                'extra': 1,
                'can_delete': True,
                'section_title': 'Pracownicy',
                'columns': 4
            }
        ]
    
    form_sections = [
        {
            "title": "Podstawowe informacje",
            "columns": 2,
            "fields": ["name", "vat_number"]
        },
        {
            "title": "Adres",
            "columns": 3,
            "fields": ["address", "postal_code", "city", "country"]
        },
        {
            "title": "Role organizacji",
            "columns": 1,
            "fields": ["role"]
        }
    ]
    
    return render_with_inlines(request, 'crud/form_with_inlines.html', {
        'form': form,
        'form_sections': form_sections,
        'page_title': f'Edytuj {organization.name}',
        'back_url': 'accounts:organization_list',
        'submit_label': 'Zapisz zmiany'
    }, inline_config=inline_config)
"""osition

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = '__all__'
        widgets = {
            'role': MultiSelectDropdownWidget(),  # ManyToMany z checkboxami
            'members': MultiSelectDropdownWidget(),  # ManyToMany z checkboxami
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'is_manager': ColoredSelectDropdownWidget(),  # Boolean z kolorami
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
"""

# =============================================================================
# URLS.PY - Konfiguracja URL
# =============================================================================

"""
# urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Organization URLs
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/<int:pk>/edit/', views.organization_update, name='organization_update'),

    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),

    # Position URLs
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/edit/', views.position_update, name='position_update'),
]
"""
