# 🚀 Publikacja na GitHub i PyPI

## GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/djcrudx.git
git push -u origin main
```

## PyPI
```bash
# Test PyPI
uv run twine upload --repository testpypi dist/*

# Produkcyjne PyPI  
uv run twine upload dist/*
```

## Instalacja przez użytkowników

### Z PyPI (po publikacji):
```bash
pip install djcrudx
# lub
uv add djcrudx
```

### Z GitHub (bezpośrednio):
```bash
pip install git+https://github.com/yourusername/djcrudx.git
# lub
uv add git+https://github.com/yourusername/djcrudx.git
```

### Użycie:
```python
# settings.py
INSTALLED_APPS = [
    'djcrudx',
]

# views.py
from djcrudx import create_crud
from djcrudx.widgets import MultiSelectDropdownWidget

crud = create_crud(Model, ModelForm, ModelFilter)
```