"""
DjCrudX - Universal Django CRUD Library

A powerful Django library for creating CRUD views with advanced features:
- Automatic filtering, sorting, and pagination
- Custom widgets (MultiSelect, DateRange, ColoredSelect, etc.)
- Permission system integration
- Responsive templates with Tailwind CSS
- Alpine.js interactive components

Usage:
    from djcrudx import create_crud
    
    crud = create_crud(Model, ModelForm, ModelFilter)
    list_view = crud['list'](table_config, page_title="Items")
"""

__version__ = "0.1.0"
__author__ = "DjCrudX Team"

from .crud import create_crud, create_crud_views, CRUDFactory, CRUDView
from .widgets import (
    MultiSelectDropdownWidget,
    SingleSelectDropdownWidget,
    ColoredSelectDropdownWidget,
    DateTimePickerWidget,
    DateRangePickerWidget,
    ActiveStatusDropdownWidget,
    TextInputWidget,
)

__all__ = [
    'create_crud',
    'create_crud_views', 
    'CRUDFactory',
    'CRUDView',
    'MultiSelectDropdownWidget',
    'SingleSelectDropdownWidget',
    'ColoredSelectDropdownWidget',
    'DateTimePickerWidget',
    'DateRangePickerWidget',
    'ActiveStatusDropdownWidget',
    'TextInputWidget',
]

# Default Django app config
default_app_config = 'djcrudx.apps.DjCrudXConfig'