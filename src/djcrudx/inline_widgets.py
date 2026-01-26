from django import forms
from django.forms import inlineformset_factory
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.widgets import Widget


class InlineFormsetWidget(Widget):
    """Universal widget for inline formsets - add/edit/delete related objects"""
    
    def __init__(self, model, related_model, fields, extra=3, can_delete=True, form_class=None, attrs=None):
        super().__init__(attrs)
        self.model = model
        self.related_model = related_model
        self.fields = fields
        self.extra = extra
        self.can_delete = can_delete
        self.form_class = form_class
        self.formset_class = None
        
    def get_formset_class(self):
        """Create formset class if not exists"""
        if not self.formset_class:
            self.formset_class = inlineformset_factory(
                self.model,
                self.related_model,
                form=self.form_class,
                fields=self.fields,
                extra=self.extra,
                can_delete=self.can_delete,
                can_delete_extra=True
            )
        return self.formset_class
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render inline formset"""
        if attrs is None:
            attrs = {}
            
        # Get formset instance
        formset_class = self.get_formset_class()
        
        # Create empty formset for rendering structure
        formset = formset_class()
        
        html = f'''
        <div class="inline-formset" data-formset-prefix="{formset.prefix}">
            <div class="formset-forms" id="formset-{name}">
                <!-- Forms will be rendered here by template -->
            </div>
            
            <div class="formset-controls mt-4">
                <button type="button" 
                        class="add-form-btn px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                        onclick="addInlineForm('{name}', '{formset.prefix}')">
                    Dodaj {self.related_model._meta.verbose_name}
                </button>
            </div>
            
            <!-- Hidden empty form template -->
            <div id="empty-form-{name}" style="display: none;">
                <!-- Empty form template will be here -->
            </div>
        </div>
        
        <script>
        function addInlineForm(fieldName, prefix) {{
            const totalForms = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
            const formNum = parseInt(totalForms.value);
            const emptyForm = document.getElementById('empty-form-' + fieldName);
            const formContainer = document.getElementById('formset-' + fieldName);
            
            // Clone empty form and replace __prefix__ with form number
            const newForm = emptyForm.innerHTML.replace(/__prefix__/g, formNum);
            
            // Add new form to container
            const formDiv = document.createElement('div');
            formDiv.className = 'inline-form border p-4 mb-4 bg-white rounded';
            formDiv.innerHTML = newForm;
            formContainer.appendChild(formDiv);
            
            // Update total forms count
            totalForms.value = formNum + 1;
            
            // Add delete functionality
            const deleteBtn = formDiv.querySelector('.delete-form-btn');
            if (deleteBtn) {{
                deleteBtn.onclick = function() {{
                    formDiv.remove();
                }};
            }}
        }}
        
        function deleteInlineForm(element) {{
            const formDiv = element.closest('.inline-form');
            const deleteCheckbox = formDiv.querySelector('input[name$="-DELETE"]');
            if (deleteCheckbox) {{
                deleteCheckbox.checked = true;
                formDiv.style.display = 'none';
            }} else {{
                formDiv.remove();
            }}
        }}
        </script>
        '''
        
        return mark_safe(html)


class InlineFormsetField(forms.Field):
    """Field for handling inline formsets"""
    
    def __init__(self, model, related_model, fields, extra=3, can_delete=True, form_class=None, **kwargs):
        self.widget = InlineFormsetWidget(
            model=model,
            related_model=related_model, 
            fields=fields,
            extra=extra,
            can_delete=can_delete,
            form_class=form_class
        )
        super().__init__(**kwargs)
        
    def clean(self, value):
        # Validation will be handled by the formset itself
        return value