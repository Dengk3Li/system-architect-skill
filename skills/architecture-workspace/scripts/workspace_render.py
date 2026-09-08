"""Compile a validated catalog into an offline reader; all assets are first-party."""
from pathlib import Path
import html
import json

from workspace_model import validate_catalog

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def script_json(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def render_html(catalog):
    validate_catalog(catalog)
    template = (ASSETS / 'workspace.html').read_text(encoding='utf-8')
    return (template.replace('<!--WORKSPACE_STYLE-->', '<style>' + (ASSETS/'workspace.css').read_text(encoding='utf-8') + '</style>')
            .replace('<!--WORKSPACE_DATA-->', '<script type="application/json" id="catalog">' + script_json(catalog) + '</script>')
            .replace('<!--WORKSPACE_SCRIPT-->', '<script>' + (ASSETS/'workspace.js').read_text(encoding='utf-8').replace('</script', '<\\/script') + '</script>')
            .replace('<!--WORKSPACE_TITLE-->', html.escape(catalog['project']['title'])))
