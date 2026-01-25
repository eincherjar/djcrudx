# filters.py - DjCrudX Filters Example

import django_filters
from django.db.models import Q
from djcrudx.widgets import (
    MultiSelectDropdownWidget,
    DateRangePickerWidget,
    ActiveStatusDropdownWidget,
    TextInputWidget,
)
from .models import Product, Category, Status


class ProductFilter(django_filters.FilterSet):
    """Example filter using DjCrudX widgets"""

    # Global search
    search = django_filters.CharFilter(
        method="filter_search",
        widget=TextInputWidget(attrs={"placeholder": "Search products..."}),
    )

    # Text filters
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=TextInputWidget(attrs={"placeholder": "Product name"}),
    )

    # Multi-select filters
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(), widget=MultiSelectDropdownWidget()
    )

    status = django_filters.ModelMultipleChoiceFilter(
        queryset=Status.objects.all(), widget=MultiSelectDropdownWidget()
    )

    assigned_users = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.filter(is_active=True), widget=MultiSelectDropdownWidget()
    )

    # Boolean filter
    is_active = django_filters.BooleanFilter(widget=ActiveStatusDropdownWidget())

    # Date range filter
    created_at = django_filters.DateFromToRangeFilter(
        widget=DateRangePickerWidget(), label="Created Date"
    )

    # Price range filters
    price_min = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        widget=TextInputWidget(attrs={"placeholder": "Min price"}),
    )

    price_max = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        widget=TextInputWidget(attrs={"placeholder": "Max price"}),
    )

    def filter_search(self, queryset, name, value):
        """Global search across multiple fields"""
        if value:
            return queryset.filter(
                Q(name__icontains=value)
                | Q(description__icontains=value)
                | Q(category__name__icontains=value)
                | Q(status__name__icontains=value)
            )
        return queryset

    class Meta:
        model = Product
        fields = [
            "search",
            "name",
            "category",
            "status",
            "assigned_users",
            "is_active",
            "created_at",
            "price_min",
            "price_max",
        ]


class CategoryFilter(django_filters.FilterSet):
    """Simple category filter example"""

    search = django_filters.CharFilter(
        method="filter_search",
        widget=TextInputWidget(attrs={"placeholder": "Search categories..."}),
    )

    parent = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.filter(parent__isnull=True),  # Only root categories
        widget=MultiSelectDropdownWidget(),
    )

    is_active = django_filters.BooleanFilter(widget=ActiveStatusDropdownWidget())

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) | Q(description__icontains=value)
            )
        return queryset

    class Meta:
        model = Category
        fields = ["search", "parent", "is_active"]
