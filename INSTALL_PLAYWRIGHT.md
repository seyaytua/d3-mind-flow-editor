# Playwright Browser Installation Guide

## Required Step for Export Functionality

After installing Python dependencies, you need to install the Playwright browser engines for the export functionality to work properly.

## Installation Commands

```bash
# Install Chromium browser engine (required for PNG/PDF export)
python -m playwright install chromium

# Optional: Install all browsers (if you want full compatibility)
python -m playwright install
```

## For macOS Users

If you encounter permission issues, try:

```bash
# Install with user permissions
python -m playwright install --force chromium

# Or install all browsers
python -m playwright install --force
```

## Verification

Test if Playwright is working:

```bash
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    print('✅ Playwright Chromium installed successfully')
    browser.close()
"
```

## Note

The export functionality (PNG, PDF, SVG) requires Playwright's Chromium browser to render the D3.js visualizations. The application will work for HTML export and preview without Playwright, but high-quality image exports need this component.