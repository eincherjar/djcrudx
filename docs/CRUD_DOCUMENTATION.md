# 📚 DjCrudX - Dokumentacja API

## 🚀 Szybki start

```python
from djcrudx import create_crud
from djcrudx.widgets import MultiSelectDropdownWidget

# Tworzenie widoków CRUD
crud = create_crud(Model, ModelForm, ModelFilter)

list_view = crud['list'](table_config, page_title="Lista")
create_view = crud['create'](form_sections, page_title="Nowy")
```

## ✅ Wbudowane funkcje

### **Filtry** 
- Automatyczne przez `filter_class` (django-filter)
- Użycie: `?name__icontains=ABC&is_active=True`

### **Sortowanie**
- Automatyczne przez `?ordering=field_name`
- Konfiguracja: `"field": "nazwa_pola"` w `table_config`
- Użycie: `?ordering=name` (rosnąco), `?ordering=-name` (malejąco)

### **Paginacja**
- Automatyczna, domyślnie 25 na stronę
- Użycie: `?page=2&per_page=50`

### **Readonly Fields**
- Konfiguracja: `readonly_fields=["field1", "field2"]`
- Pola zablokowane w trybie edycji

## 🎨 Dostępne widgety

```python
from djcrudx.widgets import (
    MultiSelectDropdownWidget,      # Wielokrotny wybór
    SingleSelectDropdownWidget,     # Pojedynczy wybór
    ColoredSelectDropdownWidget,    # Wybór z kolorami
    DateTimePickerWidget,           # Data i czas
    DateRangePickerWidget,          # Zakres dat
    ActiveStatusDropdownWidget,     # Status aktywności
    TextInputWidget,                # Stylizowane pole tekstowe
)
```

## 📊 Konfiguracja tabeli

```python
TABLE_CONFIG = [
    {
        "label": "Nazwa",
        "field": "name",           # Sortowanie
        "value": lambda obj: obj.name,
        "url": lambda obj: ("app:update", {"pk": obj.pk}),
    },
    {
        "label": "Status", 
        "field": "is_active",
        "is_badge": True,          # Kolorowe badge'y
        "badge_data": lambda obj: [{
            "name": "Aktywny" if obj.is_active else "Nieaktywny",
            "background_color": "green-100" if obj.is_active else "red-100",
            "text_color": "green-800" if obj.is_active else "red-800"
        }],
    }
]
```

## 🔧 Sekcje formularza

```python
FORM_SECTIONS = [
    {
        "title": "Podstawowe informacje",
        "columns": 2,
        "fields": ["name", "email"]
    },
    {
        "title": "Szczegóły",
        "columns": 1,
        "fields": ["description"]
    }
]
```