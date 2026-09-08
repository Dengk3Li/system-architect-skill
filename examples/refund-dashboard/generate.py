"""Reproduce the fictional refund example with the bundled renderer."""
from pathlib import Path
import importlib.util

example = Path(__file__).resolve().parent
renderer = example.parents[1] / "skills/architecture-visualizer/scripts/render_architecture.py"
spec = importlib.util.spec_from_file_location("architecture_renderer", renderer)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
model = module.load_model(example / "architecture-model.json")
(example / "architecture.html").write_text(module.render_html(model), encoding="utf-8")
(example / "architecture.svg").write_text(module.render_svg(model), encoding="utf-8")
(example / "architecture-summary.md").write_text(module.render_summary(model), encoding="utf-8")
preview = dict(model, views=[model["views"][0]])
(example / "preview.svg").write_text(module.render_svg(preview), encoding="utf-8")
print("Generated refund-dashboard example.")
