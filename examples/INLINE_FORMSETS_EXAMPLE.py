# views.py - Complete Django Views Example with Inline Formsets

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms import inlineformset_factory
from djcrudx.mixins import CrudListMixin, render_with_readonly
from djcrudx.widgets import SingleSelectDropdownWidget, MultiSelectDropdownWidget, TextInputWidget
from .models import Organization, Employee, Position, Role, User
from .forms import OrganizationForm, EmployeeForm
from .filters import OrganizationFilter, EmployeeFilter


# =============================================================================
# ORGANIZATION VIEWS WITH INLINE EMPLOYEES
# =============================================================================

def organization_list(request):
    """Lista organizacji z tabelą"""
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
            "label": "Pracownicy",
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
    """Tworzenie organizacji z pracownikami"""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        
        # Konfiguracja inline formsets
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeForm,  # Opcjonalne
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
                messages.error(request, 'Popraw błędy w formularzu.')
        else:
            messages.error(request, 'Popraw błędy w formularzu.')
    else:
        form = OrganizationForm()
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeForm,
                'extra': 3,
                'can_delete': True,
                'section_title': 'Pracownicy',
                'columns': 4
            }
        ]
    
    # Sekcje głównego formularza z inline formsets
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
            "title": "Role i pracownicy",
            "columns": 1,
            "fields": ["role", "inline_config"]  # inline_config jako specjalne pole
        },
        {
            "title": "Dodatkowe informacje",
            "columns": 1,
            "fields": ["notes"]  # Jeśli masz takie pole
        }
    ]
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': form_sections,
        'page_title': 'Nowa organizacja',
        'back_url': 'accounts:organization_list',
        'submit_label': 'Utwórz organizację'
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
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeForm,
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
                messages.error(request, 'Popraw błędy w formularzu.')
        else:
            messages.error(request, 'Popraw błędy w formularzu.')
    else:
        form = OrganizationForm(instance=organization)
        inline_config = [
            {
                'name': 'employees',
                'parent_model': Organization,
                'child_model': Employee,
                'fields': ['user', 'code', 'position', 'is_manager'],
                'form_class': EmployeeForm,
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
    
    return render_with_readonly(request, 'crud/form_view.html', {
        'form': form,
        'form_sections': form_sections,
        'page_title': f'Edytuj {organization.name}',
        'back_url': 'accounts:organization_list',
        'submit_label': 'Zapisz zmiany'
    }, inline_config=inline_config)


# =============================================================================
# FORMS.PY - Formularze z widgetami
# =============================================================================

"""
# forms.py
from django import forms
from djcrudx.widgets import MultiSelectDropdownWidget, SingleSelectDropdownWidget, TextInputWidget
from .models import Organization, Employee, Position, Role, User

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            "name", "vat_number", "address", "postal_code", "city", "country", "role"
        ]
        widgets = {
            "name": TextInputWidget(attrs={"placeholder": "Nazwa"}),
            "vat_number": TextInputWidget(attrs={"placeholder": "NIP"}),
            "address": TextInputWidget(attrs={"placeholder": "Adres"}),
            "postal_code": TextInputWidget(attrs={"placeholder": "Kod pocztowy"}),
            "city": TextInputWidget(attrs={"placeholder": "Miasto"}),
            "country": TextInputWidget(attrs={"placeholder": "Kraj"}),
            "role": MultiSelectDropdownWidget(),     # ManyToMany dla ról
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].queryset = Role.objects.all()
        self.fields["role"].label_from_instance = lambda obj: obj.name

    def save(self, commit=True):
        organization = super().save(commit=False)
        if commit:
            organization.save()
            organization.role.set(self.cleaned_data.get("role", []))
        return organization

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['user', 'code', 'position', 'is_manager']
        widgets = {
            'user': SingleSelectDropdownWidget(),        # ForeignKey = Single
            'position': SingleSelectDropdownWidget(),     # ForeignKey = Single
            'is_manager': SingleSelectDropdownWidget(),   # Boolean = Single
            'code': TextInputWidget(attrs={'placeholder': 'Kod pracownika'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.filter(is_active=True)
        self.fields["user"].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username}"
        
        self.fields["position"].queryset = Position.objects.all()
        self.fields["position"].label_from_instance = lambda obj: obj.name
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
]
"""