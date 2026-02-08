from django import forms
from django.forms.widgets import Widget
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings
from django.forms import inlineformset_factory


def get_ui_colors():
    """Pobierz kolory UI z ustawień Django"""
    return getattr(settings, 'DJCRUDX_UI_COLORS', {
        'primary': 'blue-500',
        'primary_hover': 'blue-600',
        'primary_text': 'blue-600',
        'primary_ring': 'blue-500',
        'primary_border': 'blue-500',
        'secondary': 'gray-500',
        'secondary_hover': 'gray-600'
    })


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


class MultiSelectDropdownWidget(Widget):
    """Custom widget dla multiselect dropdown z checkboxami"""

    def __init__(self, choices=(), attrs=None):
        super().__init__(attrs)
        self.choices = choices

    def format_value(self, value):
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            return [value]
        return [str(v) for v in value]

    def value_from_datadict(self, data, files, name):
        """Pobierz wartości z danych formularza"""
        return data.getlist(name)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        attrs["class"] = attrs.get("class", "") + " multiselect-dropdown"

        selected_values = self.format_value(value)
        ui_colors = get_ui_colors()

        # Pobierz choices z widget lub z bound field
        choices = getattr(self, "choices", [])
        if hasattr(self, "field") and hasattr(self.field, "queryset"):
            choices = [(obj.pk, str(obj)) for obj in self.field.queryset.all()]

        # Generuj opcje z checkboxami
        options_html = ""
        selected_labels = []

        for option_value, option_label in choices:
            if option_value == "":
                continue

            is_selected = str(option_value) in selected_values
            if is_selected:
                selected_labels.append(str(option_label))

            checked = "checked" if is_selected else ""
            options_html += f'''
                <label class="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer">
                    <input type="checkbox" name="{name}" value="{option_value}" {checked}>
                    <span class="text-xs">{option_label}</span>
                </label>
            '''

        # Tekst wyświetlany w dropdown
        display_text = (
            ", ".join(selected_labels) if selected_labels else "Wybierz opcje..."
        )
        if len(display_text) > 30:
            display_text = f"{len(selected_labels)} wybranych"

        # Dodaj id do kontenera
        field_id = attrs.get("id", f"id_{name}")

        # JavaScript dla aktualizacji tekstu
        multiselect_js = "const checkboxes = $el.querySelectorAll('input[type=checkbox]:checked'); const labels = Array.from(checkboxes).map(cb => cb.nextElementSibling.textContent); if (labels.length === 0) { selectedText = 'Wybierz opcje...'; } else if (labels.join(', ').length > 30) { selectedText = labels.length + ' wybranych'; } else { selectedText = labels.join(', '); }"

        html = f"""
            <div class="relative" id="{field_id}_container" x-data="{{ open: false, selectedText: '{display_text}' }}" @click.outside="open = false">
                <button type="button" class="w-full px-3 py-1 text-left bg-white border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-{ui_colors['primary_ring']} flex items-center justify-between gap-2" @click="open = !open">
                    <span class="truncate text-xs" x-text="selectedText">{display_text}</span>
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div x-show="open" x-transition class="absolute z-50 w-full min-w-40 mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-60 overflow-hidden dropdown-menu"
                     :class="$el.getBoundingClientRect().bottom + 250 > window.innerHeight ? 'bottom-full mb-1' : 'top-full mt-1'"
                     @change="{multiselect_js}">
                    <div class="p-2 border-b">
                        <input type="text" placeholder="Szukaj..." class="w-full px-2 py-1 text-xs border border-gray-300 rounded" onkeyup="filterOptions(this)">
                    </div>
                    <div class="max-h-48 overflow-y-auto">
                        {options_html}
                    </div>
                </div>
            </div>
        """

        return mark_safe(html)


class DateRangePickerWidget(Widget):
    """Widget z jednym polem do wyboru zakresu dat"""

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def format_value(self, value):
        if value is None:
            return [None, None]
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return value
        return [None, None]

    def value_from_datadict(self, data, files, name):
        return [data.get(name + "_0"), data.get(name + "_1")]

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        values = self.format_value(value)
        from_value = values[0] if values[0] else ""
        to_value = values[1] if values[1] else ""
        ui_colors = get_ui_colors()

        # Formatuj daty do dd.mm.rrrr
        def format_date(date_str):
            if date_str:
                try:
                    from datetime import datetime

                    # Sprawdź czy to już jest w formacie dd.mm.yyyy
                    if "." in date_str:
                        return date_str
                    date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
                    return date_obj.strftime("%d.%m.%Y")
                except:
                    return str(date_str)
            return date_str

        # Tekst wyświetlany w polu
        if from_value and to_value:
            display_text = f"{format_date(from_value)} - {format_date(to_value)}"
        elif from_value:
            display_text = f"Od {format_date(from_value)}"
        elif to_value:
            display_text = f"Do {format_date(to_value)}"
        else:
            display_text = "Wybierz zakres dat"

        # Dodaj id do kontenera
        field_id = attrs.get("id", f"id_{name}")

        html = f'''
            <div class="relative" id="{field_id}_container" x-data="{{ open: false, displayText: '{display_text}' }}" @click.outside="open = false">
                <button type="button" class="w-full px-3 py-1 text-left bg-white border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-{ui_colors["primary_ring"]} flex items-center justify-between gap-2" @click="open = !open">
                    <span class="truncate text-xs" x-text="displayText">{display_text}</span>
                    <span class="pointer-events-none">
                        <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                    </span>
                </button>
                <div x-show="open" x-transition class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg p-3 dropdown-menu">
                    <div class="flex flex-col space-y-2">
                        <div>
                            <label class="text-xs text-gray-600 mb-1">Od:</label>
                            <input type="date" name="{name}_0" value="{from_value}" class="w-full text-xs px-2 py-1 border border-gray-300 rounded">
                        </div>
                        <div>
                            <label class="text-xs text-gray-600 mb-1">Do:</label>
                            <input type="date" name="{name}_1" value="{to_value}" class="w-full text-xs px-2 py-1 border border-gray-300 rounded">
                        </div>
                        <div class="flex space-x-2 mt-2">
                            <button type="button" @click="
                                $el.closest('.dropdown-menu').querySelectorAll('input[type=date]').forEach(input => input.value = '');
                                displayText = 'Wybierz zakres dat';
                            " class="flex-1 px-2 py-1 text-xs bg-gray-200 rounded hover:bg-gray-300">Wyczyść</button>
                            <button type="button" @click="
                                const inputs = $el.closest('.dropdown-menu').querySelectorAll('input[type=date]');
                                const fromValue = inputs[0].value;
                                const toValue = inputs[1].value;

                                function formatDate(dateStr) {{
                                    if (dateStr) {{
                                        const [year, month, day] = dateStr.split('-');
                                        return day + '.' + month + '.' + year;
                                    }}
                                    return dateStr;
                                }}

                                if (fromValue && toValue) {{
                                    displayText = formatDate(fromValue) + ' - ' + formatDate(toValue);
                                }} else if (fromValue) {{
                                    displayText = 'Od ' + formatDate(fromValue);
                                }} else if (toValue) {{
                                    displayText = 'Do ' + formatDate(toValue);
                                }} else {{
                                    displayText = 'Wybierz zakres dat';
                                }}

                                open = false;
                            " class="flex-1 px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600">OK</button>
                        </div>
                    </div>
                </div>
            </div>
        '''

        return mark_safe(html)


class ColoredSelectDropdownWidget(Widget):
    """Custom widget dla select dropdown z kolorami (bg_color, txt_color)"""

    def __init__(self, choices=(), attrs=None):
        super().__init__(attrs)
        self.choices = choices

    def format_value(self, value):
        if value is None:
            return ""
        return str(value)

    def value_from_datadict(self, data, files, name):
        return data.get(name)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        attrs["class"] = attrs.get("class", "") + " singleselect-dropdown"

        selected_value = self.format_value(value)
        ui_colors = get_ui_colors()

        # Pobierz choices z widget lub z bound field
        choices = getattr(self, "choices", [])
        if hasattr(self, "field") and hasattr(self.field, "queryset"):
            choices = [
                (
                    obj.pk,
                    str(obj),
                    getattr(obj, "bg_color", "#ffffff"),
                    getattr(obj, "txt_color", "#000000"),
                )
                for obj in self.field.queryset.all()
            ]
        elif not choices:
            # Fallback - pobierz bezpośrednio z modelu Status
            try:
                from appointments.models import Status

                choices = [
                    (obj.pk, str(obj), obj.bg_color, obj.txt_color)
                    for obj in Status.objects.all()
                ]
            except:
                choices = []

        # Znajdź aktualnie wybrany status aby pobrać jego kolory
        selected_status = None
        if selected_value:
            try:
                from appointments.models import Status

                selected_status = Status.objects.get(pk=selected_value)
            except:
                pass

        # Generuj opcje z radio buttonami i kolorami
        options_html = ""
        selected_label = "Wybierz opcję..."
        selected_bg_class = "bg-white"
        selected_text_class = "text-gray-900"

        # Dodaj pustą opcję jeśli istnieje
        if (
            hasattr(self, "field")
            and hasattr(self.field, "empty_label")
            and self.field.empty_label
        ):
            empty_checked = "checked" if not selected_value else ""
            if not selected_value:
                selected_label = self.field.empty_label
            options_html += f'''
                <label class="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer">
                    <input type="radio" name="{name}" value="" {empty_checked}>
                    <span class="text-xs">{self.field.empty_label}</span>
                </label>
            '''

        for choice_item in choices:
            if len(choice_item) == 4:
                option_value, option_label, bg_color, txt_color = choice_item
            elif len(choice_item) == 2:
                option_value, option_label = choice_item
                bg_color, txt_color = "#ffffff", "#000000"
            else:
                continue

            if option_value == "":
                continue

            is_selected = str(option_value) == selected_value
            if is_selected:
                selected_label = str(option_label)
                selected_bg_class = f"bg-[{bg_color}]"
                selected_text_class = f"text-[{txt_color}]"

            checked = "checked" if is_selected else ""
            bg_class = f"bg-[{bg_color}]"
            text_class = f"text-[{txt_color}]"
            options_html += f'''
                <label class="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer">
                    <input type="radio" name="{name}" value="{option_value}" {checked}>
                    <span class="text-xs px-2 py-1 rounded {bg_class} {text_class}">{option_label}</span>
                </label>
            '''

        # Jeśli mamy wybrany status, użyj jego kolorów
        if selected_status:
            selected_bg_class = f"bg-[{selected_status.bg_color}]"
            selected_text_class = f"text-[{selected_status.txt_color}]"

        # Dodaj id do kontenera
        field_id = attrs.get("id", f"id_{name}")

        # JavaScript dla aktualizacji tekstu
        singleselect_js = "const radio = $el.querySelector('input[type=radio]:checked'); selectedText = radio ? radio.nextElementSibling.textContent : 'Wybierz opcję...'; open = false;"

        html = f"""
            <div class="relative" id="{field_id}_container" x-data="{{ open: false, selectedText: '{selected_label}' }}" @click.outside="open = false">
                <button type="button" class="w-full px-3 py-1 text-left border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-{ui_colors["primary_ring"]} flex items-center justify-between gap-2 {selected_bg_class} {selected_text_class}" @click="open = !open">
                    <span class="truncate text-xs" x-text="selectedText">{selected_label}</span>
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div x-show="open" x-transition class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-60 overflow-hidden dropdown-menu" @change="{singleselect_js}">
                    <div class="p-2 border-b">
                        <input type="text" placeholder="Szukaj..." class="w-full px-2 py-1 text-xs border border-gray-300 rounded" onkeyup="filterOptions(this)">
                    </div>
                    <div class="max-h-48 overflow-y-auto">
                        {options_html}
                    </div>
                </div>
            </div>
        """

        return mark_safe(html)


class SingleSelectDropdownWidget(Widget):
    """Custom widget dla single select dropdown z radio buttonami i automatycznym wykrywaniem kolorów"""

    def __init__(self, choices=(), attrs=None):
        super().__init__(attrs)
        self.choices = choices

    def format_value(self, value):
        if value is None:
            return ""
        return str(value)

    def value_from_datadict(self, data, files, name):
        return data.get(name)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        attrs["class"] = attrs.get("class", "") + " singleselect-dropdown"

        selected_value = self.format_value(value)
        ui_colors = get_ui_colors()

        # Pobierz choices z widget lub z bound field
        choices = getattr(self, "choices", [])
        if hasattr(self, "field") and hasattr(self.field, "queryset"):
            choices = [(obj.pk, str(obj)) for obj in self.field.queryset.all()]

        # Generuj opcje z radio buttonami
        options_html = ""
        selected_label = "Wybierz opcję..."

        # Dodaj pustą opcję jeśli istnieje
        if (
            hasattr(self, "field")
            and hasattr(self.field, "empty_label")
            and self.field.empty_label
        ):
            empty_checked = "checked" if not selected_value else ""
            if not selected_value:
                selected_label = self.field.empty_label
            options_html += f'''
                <label class="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer">
                    <input type="radio" name="{name}" value="" {empty_checked}>
                    <span class="text-xs">{self.field.empty_label}</span>
                </label>
            '''

        for option_value, option_label in choices:
            if option_value == "":
                continue

            is_selected = str(option_value) == selected_value
            if is_selected:
                selected_label = str(option_label)

            checked = "checked" if is_selected else ""
            options_html += f'''
                <label class="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer">
                    <input type="radio" name="{name}" value="{option_value}" {checked}>
                    <span class="text-xs">{option_label}</span>
                </label>
            '''

        # Dodaj id do kontenera
        field_id = attrs.get("id", f"id_{name}")

        # JavaScript dla aktualizacji tekstu
        singleselect_js = "const radio = $el.querySelector('input[type=radio]:checked'); selectedText = radio ? radio.nextElementSibling.textContent : 'Wybierz opcję...'; open = false;"

        html = f"""
            <div class="relative" id="{field_id}_container" x-data="{{ open: false, selectedText: '{selected_label}' }}" @click.outside="open = false">
                <button type="button" class="w-full px-3 py-1 text-left bg-white border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-{ui_colors["primary_ring"]} flex items-center justify-between gap-2" @click="open = !open">
                    <span class="truncate text-xs" x-text="selectedText">{selected_label}</span>
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div x-show="open" x-transition class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-60 overflow-hidden dropdown-menu"
                     :class="$el.getBoundingClientRect().bottom + 250 > window.innerHeight ? 'bottom-full mb-1' : 'top-full mt-1'"
                     @change="{singleselect_js}">
                    <div class="p-2 border-b">
                        <input type="text" placeholder="Szukaj..." class="w-full px-2 py-1 text-xs border border-gray-300 rounded" onkeyup="filterOptions(this)">
                    </div>
                    <div class="max-h-48 overflow-y-auto">
                        {options_html}
                    </div>
                </div>
            </div>
        """

        return mark_safe(html)


class DateTimePickerWidget(Widget):
    """Widget dla datetime picker z formatem dd.mm.yyyy hh:mm"""

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def format_value(self, value):
        if value is None:
            return ""
        if hasattr(value, "strftime"):
            return value.strftime("%d.%m.%Y %H:%M")
        return str(value)

    def value_from_datadict(self, data, files, name):
        return data.get(name)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        formatted_value = self.format_value(value)
        field_id = attrs.get("id", f"id_{name}")
        ui_colors = get_ui_colors()

        html = f'''
            <div class="relative" id="{field_id}_container">
                <input type="text" name="{name}" value="{formatted_value}"
                        class="w-full px-3 py-1 text-xs bg-white border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-{ui_colors["primary_ring"]}"
                        placeholder="dd.mm.rrrr hh:mm" readonly onclick="openDateTimePicker(this)">
                <div class="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                </div>
                <input type="datetime-local" style="position: absolute; left: -9999px; opacity: 0;" onchange="updateDateTimeDisplay(this)">
            </div>
        '''

        return mark_safe(html)


class ActiveStatusDropdownWidget(Widget):
    """Widget dla pola aktywności z czerwonym tłem dla 'Nie'"""

    def __init__(self, choices=(), attrs=None):
        super().__init__(attrs)
        self.choices = choices

    def format_value(self, value):
        if value is None:
            return ""
        return str(value)

    def value_from_datadict(self, data, files, name):
        return data.get(name)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        selected_value = self.format_value(value)
        choices = getattr(self, "choices", [(True, "Tak"), (False, "Nie")])
        ui_colors = get_ui_colors()

        options_html = ""
        selected_label = "Wybierz..."
        selected_bg_class = "bg-white"
        selected_text_class = "text-gray-900"

        for option_value, option_label in choices:
            is_selected = str(option_value) == selected_value
            if is_selected:
                selected_label = str(option_label)
                if str(option_value) == "False":
                    selected_bg_class = "bg-red-600"
                    selected_text_class = "text-white font-bold"
                else:
                    selected_bg_class = "bg-white"
                    selected_text_class = "text-gray-900"

            checked = "checked" if is_selected else ""

            if str(option_value) == "False":
                option_html = f'<span class="text-xs px-2 py-1 rounded bg-red-600 text-white font-bold">{option_label}</span>'
            else:
                option_html = f'<span class="text-xs">{option_label}</span>'

            options_html += f'''
                <label class="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer">
                    <input type="radio" name="{name}" value="{option_value}" {checked}>
                    {option_html}
                </label>
            '''

        field_id = attrs.get("id", f"id_{name}")

        singleselect_js = "const radio = $el.querySelector('input[type=radio]:checked'); if (radio) { const span = radio.nextElementSibling; selectedText = span.textContent; if (radio.value === 'False') { selectedBg = 'bg-red-600'; selectedTextClass = 'text-white font-bold'; } else { selectedBg = 'bg-white'; selectedTextClass = 'text-gray-900'; } } else { selectedText = 'Wybierz...'; selectedBg = 'bg-white'; selectedTextClass = 'text-gray-900'; } open = false;"

        html = f"""
            <div class="relative" id="{field_id}_container" x-data="{{ open: false, selectedText: '{selected_label}', selectedBg: '{selected_bg_class}', selectedTextClass: '{selected_text_class}' }}" @click.outside="open = false">
                <button type="button" :class="'w-full px-3 py-1 text-left border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-{ui_colors["primary_ring"]} flex items-center justify-between gap-2 ' + selectedBg + ' ' + selectedTextClass" @click="open = !open">
                    <span class="truncate text-xs" x-text="selectedText">{selected_label}</span>
                    <svg class="w-4 h-4" :class="selectedTextClass.includes('white') ? 'text-white' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div x-show="open" x-transition class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-60 overflow-hidden dropdown-menu" @change="{singleselect_js}">
                    <div class="max-h-48 overflow-y-auto">
                        {options_html}
                    </div>
                </div>
            </div>
        """

        return mark_safe(html)


class TextInputWidget(forms.TextInput):
    """Custom widget dla text input z jednolitym stylem"""

    def __init__(self, attrs=None):
        ui_colors = get_ui_colors()
        default_attrs = {
            "class": f"w-full px-3 py-1 text-xs bg-white border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-{ui_colors['primary_ring']}"
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TextareaWidget(forms.Textarea):
    """Custom widget dla textarea z pełną szerokością i jednolitym stylem"""

    def __init__(self, attrs=None):
        ui_colors = get_ui_colors()
        default_attrs = {
            "class": f"w-full px-3 py-2 text-xs bg-white border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-{ui_colors['primary_ring']}",
            "rows": 4
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)