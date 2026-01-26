from django.forms import inlineformset_factory
from django.shortcuts import render
from .inline_widgets import InlineFormsetWidget


class InlineFormsetMixin:
    """Universal mixin for handling inline formsets in views"""
    
    inline_config = []  # List of inline configurations
    
    def get_inline_config(self):
        """Override this method to define inline formsets"""
        return getattr(self, 'inline_config', [])
    
    def get_inline_formsets(self, request, instance=None):
        """Create inline formsets based on configuration"""
        formsets = {}
        
        for config in self.get_inline_config():
            formset_class = inlineformset_factory(
                config['parent_model'],
                config['child_model'],
                form=config.get('form_class'),
                fields=config['fields'],
                extra=config.get('extra', 3),
                can_delete=config.get('can_delete', True),
                can_delete_extra=True
            )
            
            if request.method == 'POST':
                formset = formset_class(request.POST, instance=instance)
            else:
                formset = formset_class(instance=instance)
                
            formsets[config['name']] = formset
            
        return formsets
    
    def save_inline_formsets(self, formsets, instance):
        """Save all inline formsets"""
        for name, formset in formsets.items():
            if formset.is_valid():
                formset.instance = instance
                formset.save()
    
    def validate_inline_formsets(self, formsets):
        """Validate all inline formsets"""
        return all(formset.is_valid() for formset in formsets.values())


def render_with_inlines(request, template_name, context, inline_config=None, readonly_fields=None):
    """
    Universal render function with inline formsets support
    
    Args:
        request: HttpRequest
        template_name: Template path
        context: Template context
        inline_config: List of inline configurations
        readonly_fields: List of readonly field names
        
    Example inline_config:
    [
        {
            'name': 'employees',
            'parent_model': Organization,
            'child_model': Employee,
            'fields': ['user', 'code', 'position', 'is_manager'],
            'form_class': EmployeeInlineForm,  # Optional
            'extra': 3,
            'can_delete': True,
            'section_title': 'Pracownicy'
        }
    ]
    """
    from .mixins import add_base_template_context, apply_readonly_fields
    
    # Add base template
    context = add_base_template_context(context)
    
    # Handle readonly fields
    if readonly_fields and "form" in context:
        form = context["form"]
        if hasattr(form, "instance") and form.instance and form.instance.pk:
            apply_readonly_fields(form, readonly_fields)
            context["readonly_fields"] = readonly_fields
    
    # Handle inline formsets
    if inline_config:
        formsets = {}
        instance = context.get('form').instance if context.get('form') else None
        
        for config in inline_config:
            formset_class = inlineformset_factory(
                config['parent_model'],
                config['child_model'],
                form=config.get('form_class'),
                fields=config['fields'],
                extra=config.get('extra', 3),
                can_delete=config.get('can_delete', True),
                can_delete_extra=True
            )
            
            if request.method == 'POST':
                formset = formset_class(request.POST, instance=instance)
            else:
                formset = formset_class(instance=instance)
                
            formsets[config['name']] = {
                'formset': formset,
                'config': config
            }
        
        context['inline_formsets'] = formsets
    
    return render(request, template_name, context)