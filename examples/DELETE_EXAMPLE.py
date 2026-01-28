# DELETE VIEW EXAMPLE - DjCrudX
# Przykład widoku usuwania z potwierdzeniem

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.shortcuts import render
from django.conf import settings
from .models import Product

def product_delete(request, pk):
    """Delete view with confirmation"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = str(product)  # Zapisz nazwę przed usunięciem
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully.')
        return redirect('app:product_list')
    
    return render(request, 'crud/delete_confirm.html', {
        'object': product,
        'page_title': f'Delete {product.name}',
        'back_url': 'app:product_list',  # URL powrotu
        'base_template': getattr(settings, 'DJCRUDX_BASE_TEMPLATE', 'crud/base.html'),
    })

# URLs Configuration
from django.urls import path

urlpatterns = [
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),
]

# Template Context Variables:
# - object: obiekt do usunięcia
# - page_title: tytuł strony
# - back_url: URL powrotu (Cancel button)

# Template automatically handles:
# - Confirmation dialog with warning
# - Delete/Cancel buttons
# - CSRF protection
# - Responsive design