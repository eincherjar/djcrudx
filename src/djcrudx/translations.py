from django.conf import settings
from django.utils.translation import get_language, gettext as _

# Wbudowane tłumaczenia - fallback gdy brak standardowych tłumaczeń Django
BUILTIN_TRANSLATIONS = {
    'pl': {
        'Create': 'Utwórz',
        'Edit': 'Edytuj', 
        'Delete': 'Usuń',
        'Save': 'Zapisz',
        'Cancel': 'Anuluj',
        'Previous': 'Poprzednia',
        'Next': 'Następna',
        'Show:': 'Pokaż:',
        'results': 'wyników',
        'entries': 'wpisów',
        'Showing': 'Wyświetlanie',
        'to': 'do',
        'of': 'z',
        'Search': 'Szukaj',
        'Actions': 'Akcje',
        'Details': 'Szczegóły',
        'Are you sure?': 'Czy jesteś pewien?',
        'This action cannot be undone.': 'Ta akcja nie może być cofnięta.',
        'Yes, delete': 'Tak, usuń',
        'No results found': 'Nie znaleziono wyników',
        'Filter': 'Filtruj',
        'Clear filters': 'Wyczyść filtry',
    }
}

# Dodaj własne tłumaczenia w settings.py
# DJCRUDX_TRANSLATIONS = {
#     'pl': {
#         'Create': 'Dodaj nowy',
#         'Edit': 'Modyfikuj',
#     }
# }

def get_custom_translations():
    """Pobierz własne tłumaczenia użytkownika z settings"""
    try:
        return getattr(settings, 'DJCRUDX_TRANSLATIONS', {})
    except:
        return {}

def smart_translate(text):
    """Inteligentne tłumaczenie - najpierw Django i18n, potem custom, potem fallback"""
    try:
        # Najpierw spróbuj standardowego Django i18n
        translated = _(text)
        if translated != text:  # Jeśli znaleziono tłumaczenie
            return translated
    except:
        pass
    
    try:
        current_lang = get_language() or getattr(settings, 'LANGUAGE_CODE', 'en')
    except:
        current_lang = 'en'  # Fallback gdy Django nie jest skonfigurowane
    
    # Sprawdź własne tłumaczenia użytkownika
    try:
        custom_translations = get_custom_translations()
        if current_lang in custom_translations and text in custom_translations[current_lang]:
            return custom_translations[current_lang][text]
    except:
        pass
    
    # Fallback do wbudowanych tłumaczeń
    if current_lang in BUILTIN_TRANSLATIONS:
        return BUILTIN_TRANSLATIONS[current_lang].get(text, text)
    
    return text