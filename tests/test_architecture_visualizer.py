from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "skills/architecture-visualizer/scripts/render_architecture.py"
FRONTEND_TEMPLATE = ROOT / "skills/architecture-visualizer/assets/frontend-module.template.json"


class ArchitectureVisualizerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        self.model = self.output_dir / "architecture-model.json"
        self.model.write_text(
            json.dumps(
                {
                    "title": "Checkout architecture",
                    "scope": "Purchase completion",
                    "audience": ["product", "engineering"],
                    "views": [
                        {
                            "id": "context",
                            "title": "System context",
                            "node_ids": ["customer", "checkout"],
                            "relationship_ids": ["starts-checkout"],
                        },
                        {
                            "id": "container",
                            "title": "Checkout containers",
                            "node_ids": ["checkout", "orders"],
                            "relationship_ids": ["creates-order"],
                        },
                    ],
                    "nodes": [
                        {
                            "id": "customer",
                            "name": "Customer",
                            "type": "person",
                            "responsibility": "Completes a purchase",
                            "business_driver": "Reduce checkout abandonment",
                            "source": "accepted product brief",
                            "source_type": "HUMAN_APPROVED_REQUIREMENT",
                            "evidence_status": "ACCEPTED",
                        },
                        {
                            "id": "checkout",
                            "name": "Checkout",
                            "type": "system",
                            "responsibility": "Coordinates purchase completion",
                            "business_driver": "Reduce checkout abandonment",
                            "source": "src/checkout",
                            "source_type": "SOURCE_CODE",
                            "evidence_status": "OBSERVED",
                        },
                        {
                            "id": "orders",
                            "name": "Orders",
                            "type": "container",
                            "responsibility": "Owns order state",
                            "business_driver": "Preserve order integrity",
                            "source": "src/orders",
                            "source_type": "SOURCE_CODE",
                            "evidence_status": "OBSERVED",
                        },
                    ],
                    "relationships": [
                        {
                            "id": "starts-checkout",
                            "source": "customer",
                            "target": "checkout",
                            "label": "starts purchase",
                            "evidence": "accepted user flow",
                            "evidence_type": "HUMAN_APPROVED_REQUIREMENT",
                            "evidence_status": "ACCEPTED",
                        },
                        {
                            "id": "creates-order",
                            "source": "checkout",
                            "target": "orders",
                            "label": "creates order through orders.v2",
                            "evidence": "orders.v2 contract",
                            "evidence_type": "CONTRACT",
                            "evidence_status": "VERIFIED",
                        },
                    ],
                    "feedback": [
                        {
                            "severity": "decision",
                            "message": "Confirm guest-checkout retention target",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_renderer(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(RENDERER),
                str(self.model),
                "--output-dir",
                str(self.output_dir),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def add_frontend_workspace(self) -> None:
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        payload["views"].append(
            {
                "id": "frontend-checkout",
                "title": "Checkout frontend module",
                "kind": "frontend",
                "frontend_module_id": "checkout-web",
                "node_ids": ["checkout"],
                "relationship_ids": [],
            }
        )
        payload["frontend_modules"] = [
            {
                "id": "checkout-web",
                "node_id": "checkout",
                "name": "Checkout web",
                "surface": "/checkout",
                "template_ref": "frontend-module-canvas-v1",
                "requirement_ids": ["REQ-CHECKOUT-01"],
                "implementation_requirements": {
                    "pages": ["Checkout page"],
                    "components": ["Order summary", "Payment form"],
                    "states": {
                        "loading": "Show retained order summary and progress",
                        "empty": "Return to cart",
                        "error": "Keep entered data and show recovery",
                        "unavailable": "Offer retry without duplicate submission",
                        "ready": "Enable one explicit submit action",
                    },
                    "interactions": [
                        {
                            "id": "submit-order",
                            "trigger": "Customer confirms payment",
                            "result": "Create one order or show a recoverable failure",
                            "requirement_ids": ["REQ-CHECKOUT-01"],
                        }
                    ],
                    "data_contracts": [
                        {
                            "id": "orders-v2",
                            "provider": "orders",
                            "version": "2.0",
                            "read_write": "write through orders API only",
                        }
                    ],
                    "quality": [
                        "Keyboard-operable submit flow",
                        "Responsive from 320px to desktop",
                    ],
                },
                "canvas": {
                    "width": 1200,
                    "height": 700,
                    "elements": [
                        {
                            "id": "checkout-page",
                            "kind": "page",
                            "title": "Checkout page",
                            "details": "Owns the purchase completion surface",
                            "requirement_ids": ["REQ-CHECKOUT-01"],
                            "x": 80,
                            "y": 80,
                            "width": 460,
                            "height": 480,
                        },
                        {
                            "id": "payment-form",
                            "kind": "component",
                            "title": "Payment form",
                            "details": "Collects and validates payment input",
                            "requirement_ids": ["REQ-CHECKOUT-01"],
                            "x": 130,
                            "y": 250,
                            "width": 340,
                            "height": 180,
                        },
                    ],
                    "connectors": [],
                },
                "annotations": [
                    {
                        "id": "annotation-copy",
                        "element_id": "payment-form",
                        "status": "open",
                        "text": "Confirm recovery copy with product",
                    }
                ],
            }
        ]
        self.model.write_text(json.dumps(payload), encoding="utf-8")

    def test_renderer_creates_repeatable_human_views(self) -> None:
        first = self.run_renderer()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        html = (self.output_dir / "architecture.html").read_text(encoding="utf-8")
        svg = (self.output_dir / "architecture.svg").read_text(encoding="utf-8")
        self.assertIn("System context", html)
        self.assertIn("Checkout containers", html)
        self.assertIn("Confirm guest-checkout retention target", html)
        self.assertIn("accepted product brief", html)
        self.assertIn("creates order through orders.v2", svg)

        initial_html = html
        initial_svg = svg
        second = self.run_renderer()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(
            (self.output_dir / "architecture.html").read_text(encoding="utf-8"),
            initial_html,
        )
        self.assertEqual(
            (self.output_dir / "architecture.svg").read_text(encoding="utf-8"),
            initial_svg,
        )

    def test_svg_centers_relationship_labels_on_the_edge(self) -> None:
        result = self.run_renderer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        root = ET.parse(self.output_dir / "architecture.svg").getroot()
        labels = [element for element in root.iter() if element.attrib.get("class") == "label"]
        self.assertGreater(len(labels), 0)
        self.assertTrue(all(label.attrib.get("text-anchor") == "middle" for label in labels))

    def test_renderer_rejects_relationships_to_unknown_nodes(self) -> None:
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        payload["relationships"][0]["target"] = "missing"
        self.model.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_renderer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown node", result.stderr)

    def test_renderer_rejects_a_model_without_views(self) -> None:
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        payload["views"] = []
        self.model.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_renderer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("at least one view", result.stderr)

    def test_renderer_rejects_ai_proposal_as_verified_architecture_evidence(self) -> None:
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        payload["nodes"][1]["source_type"] = "AI_PROPOSAL"
        payload["nodes"][1]["evidence_status"] = "VERIFIED"
        self.model.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_renderer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("AI_PROPOSAL cannot establish VERIFIED", result.stderr)

    def test_renderer_requires_explicit_evidence_provenance(self) -> None:
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        del payload["nodes"][1]["source_type"]
        self.model.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_renderer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires evidence type and status", result.stderr)

    def test_renderer_localizes_the_interactive_shell_from_the_model(self) -> None:
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        payload["language"] = "zh-CN"
        self.model.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_renderer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (self.output_dir / "architecture.html").read_text(encoding="utf-8")
        self.assertIn("架构反馈", html)
        self.assertIn("选择元素", html)

    def test_frontend_workspace_renders_from_the_architecture_model(self) -> None:
        self.add_frontend_workspace()
        result = self.run_renderer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        html = (self.output_dir / "architecture.html").read_text(encoding="utf-8")
        svg = (self.output_dir / "architecture.svg").read_text(encoding="utf-8")
        self.assertIn("Checkout frontend module", html)
        self.assertIn("Payment form", html)
        self.assertIn("REQ-CHECKOUT-01", html)
        self.assertIn("Confirm recovery copy with product", html)
        self.assertIn("Payment form", svg)

    def test_frontend_view_rejects_an_unknown_frontend_module(self) -> None:
        self.add_frontend_workspace()
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        payload["views"][-1]["frontend_module_id"] = "missing"
        self.model.write_text(json.dumps(payload), encoding="utf-8")

        result = self.run_renderer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown frontend module", result.stderr)

    def test_frontend_workspace_rejects_duplicate_element_ids(self) -> None:
        self.add_frontend_workspace()
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        duplicate = dict(payload["frontend_modules"][0]["canvas"]["elements"][0])
        payload["frontend_modules"][0]["canvas"]["elements"].append(duplicate)
        self.model.write_text(json.dumps(payload), encoding="utf-8")

        result = self.run_renderer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate frontend element id", result.stderr)

    def test_frontend_workspace_rejects_annotation_for_unknown_element(self) -> None:
        self.add_frontend_workspace()
        payload = json.loads(self.model.read_text(encoding="utf-8"))
        payload["frontend_modules"][0]["annotations"][0]["element_id"] = "missing"
        self.model.write_text(json.dumps(payload), encoding="utf-8")

        result = self.run_renderer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("annotation references unknown element", result.stderr)

    def test_frontend_workspace_exposes_local_edit_and_export_controls(self) -> None:
        self.add_frontend_workspace()
        result = self.run_renderer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        html = (self.output_dir / "architecture.html").read_text(encoding="utf-8")
        self.assertIn('id="export-model"', html)
        self.assertIn('id="reset-layout"', html)
        self.assertIn('id="element-editor"', html)
        self.assertIn('id="frontend-module-overview"', html)
        self.assertIn('id="annotation-text"', html)
        self.assertIn('id="add-annotation"', html)
        self.assertNotIn('<script src="http', html)

    def test_frontend_template_renders_without_project_specific_code(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(RENDERER),
                str(FRONTEND_TEMPLATE),
                "--output-dir",
                str(self.output_dir),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.output_dir / "architecture.html").exists())
        self.assertIn(
            "Frontend capability module",
            (self.output_dir / "architecture.svg").read_text(encoding="utf-8"),
        )

    def test_static_svg_expands_to_fit_the_frontend_canvas(self) -> None:
        self.add_frontend_workspace()
        result = self.run_renderer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        payload = json.loads(self.model.read_text(encoding="utf-8"))
        canvas_width = payload["frontend_modules"][0]["canvas"]["width"]
        root = ET.parse(self.output_dir / "architecture.svg").getroot()
        viewbox_width = float(root.attrib["viewBox"].split()[2])
        self.assertGreaterEqual(viewbox_width, canvas_width + 110)

    def test_static_frontend_view_compacts_multiple_requirement_ids(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(RENDERER),
                str(FRONTEND_TEMPLATE),
                "--output-dir",
                str(self.output_dir),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        svg = (self.output_dir / "architecture.svg").read_text(encoding="utf-8")
        self.assertIn("state-controller · REQ-CAPABILITY-01 +1", svg)


if __name__ == "__main__":
    unittest.main()
