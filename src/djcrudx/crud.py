from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.safestring import mark_safe

# Optional permissions support
try:
    from permissions.decorators import require_view_permission
    from permissions.utils import get_filtered_queryset
    HAS_PERMISSIONS = True
except ImportError:
    HAS_PERMISSIONS = False
    def require_view_permission(perm):
        def decorator(func):
            return func
        return decorator
    def get_filtered_queryset(model, user, queryset):
        return queryset

from .mixins import CrudListMixin, render_with_readonly


class CRUDFactory:
    """Factory class for creating CRUD views (simple version without permissions)"""
    
    def __init__(self, model, form_class, filter_class=None):
        self.model = model
        self.form_class = form_class
        self.filter_class = filter_class
        self.model_name = model._meta.model_name
        self.app_name = model._meta.app_label
    
    def list_view(self, table_config, **kwargs):
        @login_required
        def view(request):
            queryset = self.model.objects.all()
            
            if self.filter_class:
                filter_obj = self.filter_class(request.GET, queryset=queryset)
                queryset = filter_obj.qs
            else:
                filter_obj = None
            
            mixin = CrudListMixin()
            context = mixin.get_datatable_context(queryset, filter_obj, table_config, request)
            context.update(kwargs)
            
            return render(request, "crud/list_view.html", context)
        return view
    
    def create_view(self, form_sections, readonly_fields=None, **kwargs):
        @login_required
        def view(request):
            if request.method == "POST":
                form = self.form_class(request.POST, request.FILES)
                if form.is_valid():
                    obj = form.save()
                    messages.success(request, f"{obj} created successfully.")
                    return redirect(f"{self.app_name}:{self.model_name}_list")
                else:
                    self._add_form_errors(form, request)
            else:
                form = self.form_class()
            
            context = {
                "form": form,
                "form_sections": form_sections,
                "back_url": f"{self.app_name}:{self.model_name}_list",
                "submit_label": f"Create {self.model._meta.verbose_name}",
            }
            context.update(kwargs)
            
            return render_with_readonly(request, "crud/form_view.html", context, readonly_fields)
        return view
    
    def update_view(self, form_sections, readonly_fields=None, **kwargs):
        @login_required
        def view(request, pk):
            obj = get_object_or_404(self.model, pk=pk)
            
            if request.method == "POST":
                form = self.form_class(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    obj = form.save()
                    messages.success(request, f"{obj} updated successfully.")
                    return redirect(f"{self.app_name}:{self.model_name}_list")
                else:
                    self._add_form_errors(form, request)
            else:
                form = self.form_class(instance=obj)
            
            context = {
                "form": form,
                "form_sections": form_sections,
                "back_url": f"{self.app_name}:{self.model_name}_list",
                "submit_label": "Save changes",
                "object": obj,
            }
            context.update(kwargs)
            
            return render_with_readonly(request, "crud/form_view.html", context, readonly_fields)
        return view
    
    def detail_view(self, detail_config, **kwargs):
        @login_required
        def view(request, pk):
            obj = get_object_or_404(self.model, pk=pk)
            
            context = {
                "object": obj,
                "detail_config": detail_config,
                "back_url": f"{self.app_name}:{self.model_name}_list",
                "edit_url": f"{self.app_name}:{self.model_name}_update",
            }
            context.update(kwargs)
            
            return render(request, "crud/detail_view.html", context)
        return view
    
    def delete_view(self, **kwargs):
        @login_required
        def view(request, pk):
            obj = get_object_or_404(self.model, pk=pk)
            
            if request.method == "POST":
                obj_name = str(obj)
                obj.delete()
                messages.success(request, f"{obj_name} deleted successfully.")
                return redirect(f"{self.app_name}:{self.model_name}_list")
            
            context = {
                "object": obj,
                "back_url": f"{self.app_name}:{self.model_name}_list",
            }
            context.update(kwargs)
            
            return render(request, "crud/delete_confirm.html", context)
        return view
    
    def _add_form_errors(self, form, request):
        for field, errors in form.errors.items():
            for error in errors:
                if field == "__all__":
                    messages.error(request, error)
                else:
                    field_label = form[field].label if field in form.fields else field
                    messages.error(request, f"{field_label}: {error}")


class CRUDView:
    """Advanced CRUD class with permissions support"""
    
    def __init__(self, model, form_class, filter_class=None):
        self.model = model
        self.form_class = form_class
        self.filter_class = filter_class
        self.model_name = model._meta.model_name
        self.app_name = model._meta.app_label
        
    def get_base_context(self):
        """Base context for all views"""
        return {
            'model_name': self.model_name,
            'app_name': self.app_name,
        }
    
    def list_view(self, table_config, **kwargs):
        """List view with permissions"""
        @login_required
        @require_view_permission(f'{self.app_name}:{self.model_name}_list')
        def view(request):
            base_queryset = self.model.objects.all()
            queryset = get_filtered_queryset(self.model, request.user, base_queryset)
            
            if self.filter_class:
                filter_obj = self.filter_class(request.GET, queryset=queryset)
                queryset = filter_obj.qs
            else:
                filter_obj = None
            
            mixin = CrudListMixin()
            context = mixin.get_datatable_context(queryset, filter_obj, table_config, request, 
                                                view_name=f"{self.app_name}:{self.model_name}_list")
            
            context.update(self.get_base_context())
            context.update(kwargs)
            
            return render(request, "crud/list_view.html", context)
        
        return view
    
    def create_view(self, form_sections, readonly_fields=None, **kwargs):
        """Create view with permissions"""
        @login_required
        @require_view_permission(f'{self.app_name}:{self.model_name}_create')
        def view(request):
            if request.method == "POST":
                form = self.form_class(request.POST, request.FILES)
                if form.is_valid():
                    obj = form.save()
                    messages.success(request, f"{obj} created successfully.")
                    return redirect(f"{self.app_name}:{self.model_name}_list")
                else:
                    self._add_form_errors(form, request)
            else:
                form = self.form_class()
            
            context = {
                "form": form,
                "form_sections": form_sections,
                "back_url": f"{self.app_name}:{self.model_name}_list",
                "submit_label": f"Create {self.model._meta.verbose_name}",
            }
            context.update(self.get_base_context())
            context.update(kwargs)
            
            return render_with_readonly(request, "crud/form_view.html", context, readonly_fields)
        
        return view
    
    def update_view(self, form_sections, readonly_fields=None, **kwargs):
        """Update view with permissions"""
        @login_required
        @require_view_permission(f'{self.app_name}:{self.model_name}_update')
        def view(request, pk):
            obj = get_object_or_404(self.model, pk=pk)
            
            if request.method == "POST":
                form = self.form_class(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    obj = form.save()
                    messages.success(request, f"{obj} updated successfully.")
                    return redirect(f"{self.app_name}:{self.model_name}_list")
                else:
                    self._add_form_errors(form, request)
            else:
                form = self.form_class(instance=obj)
            
            context = {
                "form": form,
                "form_sections": form_sections,
                "back_url": f"{self.app_name}:{self.model_name}_list",
                "submit_label": "Save changes",
                "object": obj,
            }
            context.update(self.get_base_context())
            context.update(kwargs)
            
            return render_with_readonly(request, "crud/form_view.html", context, readonly_fields)
        
        return view
    
    def detail_view(self, detail_config, **kwargs):
        """Detail view with permissions"""
        @login_required
        @require_view_permission(f'{self.app_name}:{self.model_name}_detail')
        def view(request, pk):
            obj = get_object_or_404(self.model, pk=pk)
            
            context = {
                "object": obj,
                "detail_config": detail_config,
                "back_url": f"{self.app_name}:{self.model_name}_list",
                "edit_url": f"{self.app_name}:{self.model_name}_update",
            }
            context.update(self.get_base_context())
            context.update(kwargs)
            
            return render(request, "crud/detail_view.html", context)
        
        return view
    
    def delete_view(self, **kwargs):
        """Delete view with permissions"""
        @login_required
        @require_view_permission(f'{self.app_name}:{self.model_name}_delete')
        def view(request, pk):
            obj = get_object_or_404(self.model, pk=pk)
            
            if request.method == "POST":
                obj_name = str(obj)
                obj.delete()
                messages.success(request, f"{obj_name} deleted successfully.")
                return redirect(f"{self.app_name}:{self.model_name}_list")
            
            context = {
                "object": obj,
                "back_url": f"{self.app_name}:{self.model_name}_list",
            }
            context.update(self.get_base_context())
            context.update(kwargs)
            
            return render(request, "crud/delete_confirm.html", context)
        
        return view
    
    def _add_form_errors(self, form, request):
        """Add form errors to messages"""
        for field, errors in form.errors.items():
            for error in errors:
                if field == "__all__":
                    messages.error(request, error)
                else:
                    messages.error(request, f"{form[field].label}: {error}")
        messages.error(request, "Form contains errors. Please check the fields below.")


# Main API functions
def create_crud(model, form_class, filter_class=None):
    """Create simple CRUD views without permissions"""
    crud = CRUDFactory(model, form_class, filter_class)
    return {
        'list': crud.list_view,
        'create': crud.create_view,
        'update': crud.update_view,
        'detail': crud.detail_view,
        'delete': crud.delete_view,
    }


def create_crud_views(model, form_class, filter_class=None):
    """Create advanced CRUD views with permissions support"""
    crud = CRUDView(model, form_class, filter_class)
    return {
        'list': crud.list_view,
        'create': crud.create_view,
        'update': crud.update_view,
        'detail': crud.detail_view,
        'delete': crud.delete_view,
    }