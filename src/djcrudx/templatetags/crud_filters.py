from django import template

register = template.Library()

@register.filter
def get_form_field(form, field_name):
    """Get field from form by name"""
    return form.fields.get(field_name) and form[field_name] or None

@register.filter
def get_field(obj, attr):
    """Get attribute from object"""
    return getattr(obj, attr, None)

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, {})
    return {}

@register.filter
def get_display_value(field):
    """Get display value for form field"""
    if not field.value():
        return "-"
    
    # Dla pól datetime - sformatuj do dd.mm.yyyy hh:mm
    if hasattr(field.field, 'widget') and hasattr(field.field.widget, 'input_type') and field.field.widget.input_type == 'datetime-local':
        try:
            from datetime import datetime
            value = field.value()
            if isinstance(value, datetime):
                return value.strftime("%d.%m.%Y %H:%M")
            elif isinstance(value, str):
                # Spróbuj sparsować i przeformatować
                try:
                    dt = datetime.fromisoformat(value.replace('T', ' '))
                    return dt.strftime("%d.%m.%Y %H:%M")
                except:
                    return value
        except:
            pass
    
    # Dla pól z queryset (ForeignKey, ManyToMany)
    if hasattr(field.field, 'queryset'):
        try:
            value = field.value()
            # ManyToManyField - lista wartości
            if isinstance(value, (list, tuple)):
                objects = field.field.queryset.filter(pk__in=value)
                if hasattr(field.field, 'label_from_instance'):
                    return ", ".join([field.field.label_from_instance(obj) for obj in objects])
                else:
                    return ", ".join([str(obj) for obj in objects])
            # ForeignKey - pojedyncza wartość
            else:
                obj = field.field.queryset.get(pk=value)
                if hasattr(field.field, 'label_from_instance'):
                    return field.field.label_from_instance(obj)
                else:
                    return str(obj)
        except:
            return field.value()
    
    # Dla pól z choices
    if hasattr(field.field, 'choices') and field.field.choices:
        for value, label in field.field.choices:
            if str(value) == str(field.value()):
                return label
    
    return field.value()