#!/bin/bash

# Build script for DjCrudX package with uv

echo "🚀 Building DjCrudX package with uv..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Sync dependencies
echo "📦 Syncing dependencies..."
uv sync

# Build the package
echo "🔨 Building package..."
uv build

echo "✅ Build completed!"
echo "📁 Package files created in dist/"
ls -la dist/

echo ""
echo "To install locally: uv pip install dist/djcrudx-0.1.0-py3-none-any.whl"
echo "To upload to PyPI: uv run twine upload dist/*"