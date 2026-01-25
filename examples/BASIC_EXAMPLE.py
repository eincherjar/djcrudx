# views.py - Traditional Django Views with DjCrudX

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from djcrudx.mixins import CrudListMixin, render_with_readonly

from .models import Product
from .forms import ProductForm
from .filters import ProductFilter


@login_required
def product_list(request):
    """List all products with filtering and pagination"""
    products = Product.objects.all().order_by('-created_at')
    
    # Apply filters
    product_filter = ProductFilter(request.GET, queryset=products)
    
    # Table configuration
    table_config = [
        {
            "label": "Name",
            "field": "name",
            "value": lambda obj: obj.name,
            "url": lambda obj: ("products:product_update", {"pk": obj.pk}),
        },
        {
            "label": "Price",
            "field": "price",
            "value": lambda obj: f"${obj.price}",
        },
        {
            "label": "Status",
            "field": "is_active",
            "value": lambda obj: "Active" if obj.is_active else "Inactive",
            "is_badge": True,
            "badge_data": lambda obj: [
                {
                    "name": "Active" if obj.is_active else "Inactive",
                    "background_color": "green-100" if obj.is_active else "red-100",
                    "text_color": "green-800" if obj.is_active else "red-800"
                }
            ],
        },
    ]
    
    # Use DjCrudX mixin for datatable
    mixin = CrudListMixin()
    context = mixin.get_datatable_context(
        product_filter.qs, product_filter, table_config, request
    )
    
    # Add page configuration
    context.update({
        "page_title": "Products",
        "create_url": "products:product_create",
        "create_label": "Add Product"
    })
    
    return render(request, "crud/list_view.html", context)


@login_required
def product_create(request):
    """Create a new product"""
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product {product.name} created successfully.")
            return redirect("products:product_list")
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form[field].label}: {error}")
    else:
        form = ProductForm()
    
    # Form sections configuration
    form_sections = [
        {
            "title": "Basic Information",
            "columns": 2,
            "fields": ["name", "price"]
        },
        {
            "title": "Details",
            "columns": 3,
            "fields": ["category", "description", "is_active"]
        },
    ]
    
    context = {
        "form": form,
        "form_sections": form_sections,
        "page_title": "New Product",
        "back_url": "products:product_list",
        "submit_label": "Create Product",
    }
    
    return render(request, "crud/form_view.html", context)


@login_required
def product_update(request, pk):
    """Update an existing product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product {product.name} updated successfully.")
            return redirect("products:product_list")
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form[field].label}: {error}")
    else:
        form = ProductForm(instance=product)
    
    # Form sections configuration
    form_sections = [
        {
            "title": "Basic Information",
            "columns": 2,
            "fields": ["name", "price"]
        },
        {
            "title": "Details",
            "columns": 3,
            "fields": ["category", "description", "is_active"]
        },
    ]
    
    # Define readonly fields
    readonly_fields = ["created_at"]
    
    context = {
        "form": form,
        "form_sections": form_sections,
        "page_title": f"Edit {product.name}",
        "back_url": "products:product_list",
        "submit_label": "Save Changes",
        "object": product,
    }
    
    return render_with_readonly(request, "crud/form_view.html", context, readonly_fields)


@login_required
def product_detail(request, pk):
    """Display product details"""
    product = get_object_or_404(Product, pk=pk)
    
    context = {
        "object": product,
        "page_title": f"Product: {product.name}",
        "back_url": "products:product_list",
        "edit_url": "products:product_update",
    }
    
    return render(request, "crud/detail_view.html", context)


@login_required
def product_delete(request, pk):
    """Delete a product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == "POST":
        product_name = str(product)
        product.delete()
        messages.success(request, f"{product_name} deleted successfully.")
        return redirect("products:product_list")
    
    context = {
        "object": product,
        "page_title": "Delete Product",
        "back_url": "products:product_list",
    }
    
    return render(request, "crud/delete_confirm.html", context)


# urls.py - URL Configuration Example
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/edit/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
]
"""