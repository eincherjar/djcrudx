# forms.py - DjCrudX Forms Example

from django import forms
from django.contrib.auth import get_user_model
from djcrudx.widgets import (
    MultiSelectDropdownWidget,
    SingleSelectDropdownWidget,
    ColoredSelectDropdownWidget,
    DateTimePickerWidget,
    ActiveStatusDropdownWidget,
    TextInputWidget,
)
from .models import Product, Category, Status

User = get_user_model()


class ProductForm(forms.ModelForm):
    """Example form using DjCrudX widgets"""

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "category",
            "tags",
            "status",
            "is_active",
            "created_at",
            "assigned_users",
        ]
        widgets = {
            # Text inputs
            "name": TextInputWidget(attrs={"placeholder": "Product name"}),
            "description": TextInputWidget(
                attrs={"placeholder": "Product description"}
            ),
            "price": TextInputWidget(attrs={"placeholder": "0.00"}),
            # Single select with colors
            "status": ColoredSelectDropdownWidget(),
            # Multi-select dropdowns
            "tags": MultiSelectDropdownWidget(),
            "assigned_users": MultiSelectDropdownWidget(),
            # Single select dropdown
            "category": SingleSelectDropdownWidget(),
            # Active status with red background for "No"
            "is_active": ActiveStatusDropdownWidget(),
            # DateTime picker
            "created_at": DateTimePickerWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize querysets and labels
        self.fields["assigned_users"].queryset = User.objects.filter(is_active=True)
        self.fields["assigned_users"].label_from_instance = (
            lambda obj: f"{obj.get_full_name() or obj.username}"
        )

        self.fields["category"].queryset = Category.objects.filter(is_active=True)
        self.fields["category"].empty_label = "Select category"

        # For editing - limit some fields
        if self.instance and self.instance.pk:
            self.fields["created_at"].widget.attrs["readonly"] = True

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError("Product name is required.")

        # Check uniqueness (exclude current instance in edit mode)
        existing = Product.objects.filter(name=name)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise forms.ValidationError("Product with this name already exists.")

        return name

    def save(self, commit=True):
        product = super().save(commit=False)

        if commit:
            product.save()
            # Save many-to-many relationships
            product.tags.set(self.cleaned_data.get("tags", []))
            product.assigned_users.set(self.cleaned_data.get("assigned_users", []))

        return product


class CategoryForm(forms.ModelForm):
    """Simple category form example"""

    class Meta:
        model = Category
        fields = ["name", "description", "parent", "is_active"]
        widgets = {
            "name": TextInputWidget(attrs={"placeholder": "Category name"}),
            "description": TextInputWidget(
                attrs={"placeholder": "Optional description"}
            ),
            "parent": SingleSelectDropdownWidget(),
            "is_active": ActiveStatusDropdownWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prevent circular references in parent selection
        if self.instance and self.instance.pk:
            self.fields["parent"].queryset = Category.objects.exclude(
                pk=self.instance.pk
            ).exclude(parent=self.instance)
        else:
            self.fields["parent"].queryset = Category.objects.all()

        self.fields["parent"].empty_label = "No parent category"
