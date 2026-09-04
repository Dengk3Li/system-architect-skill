#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any


def load_model(path: Path) -> dict[str, Any]:
    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read architecture model: {exc}") from exc

    for key in ("title", "nodes", "relationships", "views"):
        if key not in model:
            raise ValueError(f"missing required field: {key}")
    if not isinstance(model["title"], str) or not model["title"].strip():
        raise ValueError("title must be a non-empty string")
    if not all(isinstance(model[key], list) for key in ("nodes", "relationships", "views")):
        raise ValueError("nodes, relationships, and views must be arrays")
    if not model["nodes"]:
        raise ValueError("architecture model requires at least one node")
    if not model["views"]:
        raise ValueError("architecture model requires at least one view")

    node_ids = _unique_ids(model["nodes"], "node")
    relationship_ids = _unique_ids(model["relationships"], "relationship")
    view_ids = _unique_ids(model["views"], "view")
    del view_ids

    for relationship in model["relationships"]:
        for endpoint in ("source", "target"):
            if relationship.get(endpoint) not in node_ids:
                raise ValueError(
                    f"relationship {relationship.get('id', '<unknown>')} references "
                    f"unknown node {relationship.get(endpoint)!r}"
                )

    for node in model["nodes"]:
        _validate_evidence(
            f"node {node['id']}",
            node.get("source_type"),
            node.get("evidence_status"),
        )
    for relationship in model["relationships"]:
        _validate_evidence(
            f"relationship {relationship['id']}",
            relationship.get("evidence_type"),
            relationship.get("evidence_status"),
        )

    for view in model["views"]:
        unknown_nodes = set(view.get("node_ids", [])) - node_ids
        unknown_relationships = set(view.get("relationship_ids", [])) - relationship_ids
        if unknown_nodes:
            raise ValueError(f"view {view['id']} references unknown node {sorted(unknown_nodes)[0]!r}")
        if unknown_relationships:
            raise ValueError(
                f"view {view['id']} references unknown relationship "
                f"{sorted(unknown_relationships)[0]!r}"
            )
    _validate_frontend_modules(model, node_ids)
    return model


def _validate_frontend_modules(model: dict[str, Any], node_ids: set[str]) -> None:
    modules = model.get("frontend_modules", [])
    if not isinstance(modules, list):
        raise ValueError("frontend_modules must be an array")
    module_ids = _unique_ids(modules, "frontend module")

    for module in modules:
        label = f"frontend module {module['id']}"
        if module.get("node_id") not in node_ids:
            raise ValueError(f"{label} references unknown architecture node {module.get('node_id')!r}")
        if not isinstance(module.get("template_ref"), str) or not module["template_ref"].strip():
            raise ValueError(f"{label} requires template_ref")
        requirement_ids = module.get("requirement_ids")
        if not isinstance(requirement_ids, list) or not requirement_ids or not all(
            isinstance(item, str) and item for item in requirement_ids
        ):
            raise ValueError(f"{label} requires requirement_ids")

        requirements = module.get("implementation_requirements")
        required_requirement_fields = {
            "pages",
            "components",
            "states",
            "interactions",
            "data_contracts",
            "quality",
        }
        if not isinstance(requirements, dict) or not required_requirement_fields.issubset(requirements):
            raise ValueError(f"{label} has incomplete implementation_requirements")
        required_states = {"loading", "empty", "error", "unavailable", "ready"}
        if not isinstance(requirements["states"], dict) or not required_states.issubset(
            requirements["states"]
        ):
            raise ValueError(f"{label} requires loading, empty, error, unavailable, and ready states")

        canvas = module.get("canvas")
        if not isinstance(canvas, dict):
            raise ValueError(f"{label} requires a canvas")
        if not all(isinstance(canvas.get(key), (int, float)) and canvas[key] > 0 for key in ("width", "height")):
            raise ValueError(f"{label} canvas requires positive width and height")
        elements = canvas.get("elements")
        connectors = canvas.get("connectors", [])
        if not isinstance(elements, list) or not elements:
            raise ValueError(f"{label} canvas requires elements")
        if not isinstance(connectors, list):
            raise ValueError(f"{label} connectors must be an array")
        element_ids = _unique_ids(elements, "frontend element")
        module_requirements = set(requirement_ids)
        for element in elements:
            for field in ("title", "kind"):
                if not isinstance(element.get(field), str) or not element[field].strip():
                    raise ValueError(f"frontend element {element['id']} requires {field}")
            if not all(
                isinstance(element.get(key), (int, float)) and element[key] >= 0
                for key in ("x", "y")
            ) or not all(
                isinstance(element.get(key), (int, float)) and element[key] > 0
                for key in ("width", "height")
            ):
                raise ValueError(f"frontend element {element['id']} requires valid geometry")
            unknown_requirements = set(element.get("requirement_ids", [])) - module_requirements
            if unknown_requirements:
                raise ValueError(
                    f"frontend element {element['id']} references unknown requirement "
                    f"{sorted(unknown_requirements)[0]!r}"
                )
        _unique_ids(connectors, "frontend connector")
        for connector in connectors:
            if connector.get("source") not in element_ids or connector.get("target") not in element_ids:
                raise ValueError(f"frontend connector {connector['id']} references unknown element")

        annotations = module.get("annotations", [])
        if not isinstance(annotations, list):
            raise ValueError(f"{label} annotations must be an array")
        _unique_ids(annotations, "frontend annotation")
        for annotation in annotations:
            if annotation.get("element_id") not in element_ids:
                raise ValueError(
                    f"frontend annotation {annotation['id']}: annotation references unknown element"
                )

    for view in model["views"]:
        if view.get("kind") == "frontend" and view.get("frontend_module_id") not in module_ids:
            raise ValueError(
                f"view {view['id']} references unknown frontend module "
                f"{view.get('frontend_module_id')!r}"
            )


def _validate_evidence(label: str, evidence_type: Any, status: Any) -> None:
    evidence_types = {
        "HUMAN_APPROVED_REQUIREMENT",
        "SOURCE_CODE",
        "TEST_RESULT",
        "RUNTIME_OBSERVATION",
        "CONTRACT",
        "EXTERNAL_PRIMARY_SOURCE",
        "AI_PROPOSAL",
    }
    evidence_statuses = {"PROPOSED", "OBSERVED", "VERIFIED", "ACCEPTED"}
    if evidence_type not in evidence_types or status not in evidence_statuses:
        raise ValueError(f"{label}: requires evidence type and status")
    if evidence_type == "AI_PROPOSAL" and status in {"VERIFIED", "ACCEPTED"}:
        raise ValueError(f"{label}: AI_PROPOSAL cannot establish {status} architecture evidence")


def _unique_ids(items: list[dict[str, Any]], kind: str) -> set[str]:
    ids: set[str] = set()
    for item in items:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"{kind} requires a non-empty id")
        if item_id in ids:
            raise ValueError(f"duplicate {kind} id: {item_id}")
        ids.add(item_id)
    return ids


def _positions(node_ids: list[str]) -> dict[str, tuple[int, int]]:
    columns = min(3, max(1, len(node_ids)))
    return {
        node_id: (90 + (index % columns) * 350, 110 + (index // columns) * 190)
        for index, node_id in enumerate(node_ids)
    }


def _requirement_summary(requirement_ids: list[str]) -> str:
    if not requirement_ids:
        return "UNMAPPED"
    suffix = f" +{len(requirement_ids) - 1}" if len(requirement_ids) > 1 else ""
    return f"{requirement_ids[0]}{suffix}"


def render_svg(model: dict[str, Any]) -> str:
    node_by_id = {node["id"]: node for node in model["nodes"]}
    relationship_by_id = {edge["id"]: edge for edge in model["relationships"]}
    frontend_by_id = {module["id"]: module for module in model.get("frontend_modules", [])}
    section_heights = [
        (
            110 + frontend_by_id[view["frontend_module_id"]]["canvas"]["height"]
            if view.get("kind") == "frontend"
            else 150
            + max(1, (len(view.get("node_ids", [])) + 2) // 3) * 190
            + len(view.get("relationship_ids", [])) * 24
        )
        for view in model["views"]
    ]
    height = 90 + sum(section_heights)
    width = max(
        [1200]
        + [110 + module["canvas"]["width"] for module in model.get("frontend_modules", [])]
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs><marker id=\"arrow\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" fill=\"#637083\"/></marker></defs>",
        "<style>.node{fill:#f7f9fc;stroke:#3659a2;stroke-width:2}.name{font:600 17px system-ui;fill:#132238}.meta{font:13px system-ui;fill:#516174}.edge{stroke:#637083;stroke-width:2;marker-end:url(#arrow)}.label{font:600 11px system-ui;fill:#334155}.legend{font:13px system-ui;fill:#334155}</style>",
        f'<text x="55" y="45" font-family="system-ui" font-size="26" font-weight="700">{html.escape(model["title"])}</text>',
    ]
    offset = 70
    for view, section_height in zip(model["views"], section_heights):
        if view.get("kind") == "frontend":
            module = frontend_by_id[view["frontend_module_id"]]
            canvas = module["canvas"]
            elements = {element["id"]: element for element in canvas["elements"]}
            parts.append(
                f'<text x="55" y="{offset + 24}" font-family="system-ui" font-size="17" '
                f'font-weight="650">{html.escape(view.get("title", view["id"]))}</text>'
            )
            parts.append(
                f'<text class="meta" x="55" y="{offset + 50}">'
                f'{html.escape(module.get("surface", ""))} · '
                f'{html.escape(module.get("template_ref", ""))}</text>'
            )
            for connector in canvas.get("connectors", []):
                source = elements[connector["source"]]
                target = elements[connector["target"]]
                x1 = 55 + source["x"] + source["width"]
                y1 = offset + 75 + source["y"] + source["height"] / 2
                x2 = 55 + target["x"]
                y2 = offset + 75 + target["y"] + target["height"] / 2
                parts.append(f'<line class="edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
                parts.append(
                    f'<text class="label" text-anchor="middle" x="{(x1 + x2) / 2}" '
                    f'y="{(y1 + y2) / 2 - 8}">{html.escape(connector.get("label", ""))}</text>'
                )
            for element in canvas["elements"]:
                x = 55 + element["x"]
                y = offset + 75 + element["y"]
                parts.extend(
                    [
                        f'<rect class="node" x="{x}" y="{y}" width="{element["width"]}" '
                        f'height="{element["height"]}" rx="12"/>',
                        f'<text class="name" x="{x + 14}" y="{y + 27}">'
                        f'{html.escape(element["title"])}</text>',
                        f'<text class="meta" x="{x + 14}" y="{y + 49}">'
                        f'{html.escape(element["kind"])} · '
                        f'{html.escape(_requirement_summary(element.get("requirement_ids", [])))}</text>',
                    ]
                )
            offset += section_height
            continue
        node_ids = view.get("node_ids", [])
        positions = {
            node_id: (x, y + offset)
            for node_id, (x, y) in _positions(node_ids).items()
        }
        parts.append(
            f'<text x="55" y="{offset + 24}" font-family="system-ui" font-size="17" '
            f'font-weight="650">{html.escape(view.get("title", view["id"]))}</text>'
        )
        for edge_number, relationship_id in enumerate(view.get("relationship_ids", []), start=1):
            edge = relationship_by_id[relationship_id]
            if edge["source"] not in positions or edge["target"] not in positions:
                continue
            x1, y1 = positions[edge["source"]]
            x2, y2 = positions[edge["target"]]
            parts.append(f'<line class="edge" x1="{x1 + 130}" y1="{y1 + 42}" x2="{x2}" y2="{y2 + 42}"/>')
            parts.append(
                f'<text class="label" text-anchor="middle" x="{(x1 + x2 + 130) // 2}" '
                f'y="{(y1 + y2) // 2 + 30}">R{edge_number}</text>'
            )
        for node_id in node_ids:
            node = node_by_id[node_id]
            x, y = positions[node_id]
            parts.extend(
                [
                    f'<rect class="node" x="{x}" y="{y}" width="260" height="84" rx="14"/>',
                    f'<text class="name" x="{x + 18}" y="{y + 31}">{html.escape(node.get("name", node_id))}</text>',
                    f'<text class="meta" x="{x + 18}" y="{y + 56}">{html.escape(node.get("type", "element"))}</text>',
                    f'<title>{html.escape(node.get("responsibility", ""))}</title>',
                ]
            )
        legend_y = offset + 130 + max(1, (len(node_ids) + 2) // 3) * 190
        for edge_number, relationship_id in enumerate(view.get("relationship_ids", []), start=1):
            edge = relationship_by_id[relationship_id]
            parts.append(
                f'<text class="legend" x="55" y="{legend_y + edge_number * 24}">'
                f'R{edge_number}  {html.escape(edge.get("label", ""))}</text>'
            )
        offset += section_height
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_summary(model: dict[str, Any]) -> str:
    is_zh = str(model.get("language", "")).lower().startswith("zh")
    scope_label = "范围" if is_zh else "Scope"
    views_label = "视图" if is_zh else "Views"
    feedback_label = "架构反馈" if is_zh else "Architecture feedback"
    empty_feedback = "暂无反馈。" if is_zh else "No feedback recorded."
    lines = [
        f"# {model['title']}",
        "",
        f"{scope_label}: {model.get('scope', 'UNKNOWN')}",
        "",
        f"## {views_label}",
        "",
    ]
    lines.extend(f"- {view.get('title', view['id'])}" for view in model["views"])
    lines.extend(["", f"## {feedback_label}", ""])
    feedback = model.get("feedback", [])
    if feedback:
        lines.extend(
            f"- [{item.get('severity', 'note').upper()}] {item.get('message', '')}"
            for item in feedback
        )
    else:
        lines.append(f"- {empty_feedback}")
    return "\n".join(lines) + "\n"


def render_html(model: dict[str, Any]) -> str:
    payload = json.dumps(model, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    title = html.escape(model["title"])
    is_zh = str(model.get("language", "")).lower().startswith("zh")
    language = "zh-CN" if is_zh else "en"
    ui = {
        "search": "查找架构元素" if is_zh else "Find an element",
        "diagram_label": "交互式架构视图" if is_zh else "Interactive architecture view",
        "feedback": "架构反馈" if is_zh else "Architecture feedback",
        "selected": "选择元素" if is_zh else "Selected element",
        "instruction": (
            "选择一个元素，查看其职责、业务驱动和来源。"
            if is_zh
            else "Select an element to inspect its responsibility, business driver, and source."
        ),
        "export": "导出已编辑模型" if is_zh else "Export edited model",
        "reset": "重置布局" if is_zh else "Reset layout",
        "edit": "编辑前端元素" if is_zh else "Edit frontend element",
        "element_title": "元素名称" if is_zh else "Element title",
        "details": "实现要求" if is_zh else "Implementation requirement",
        "requirements": "需求 ID（逗号分隔）" if is_zh else "Requirement IDs (comma-separated)",
        "geometry": "布局：x / y / 宽 / 高" if is_zh else "Layout: x / y / width / height",
        "apply": "应用到画布" if is_zh else "Apply to canvas",
        "annotation": "批注" if is_zh else "Annotation",
        "annotation_placeholder": "写下需要确认或调整的内容" if is_zh else "Record a decision or requested adjustment",
        "add_annotation": "添加批注" if is_zh else "Add annotation",
        "local_note": (
            "修改只保存在当前页面；导出 JSON 后再进入版本评审。"
            if is_zh
            else "Edits stay in this page until you export the JSON for review."
        ),
        "invalid_requirement": (
            "元素只能引用前端模块已经登记的需求 ID。"
            if is_zh
            else "An element can reference only requirement IDs registered by its frontend module."
        ),
    }
    detail_fields = [
        ("名称" if is_zh else "Name", "name"),
        ("类型" if is_zh else "Type", "type"),
        ("职责" if is_zh else "Responsibility", "responsibility"),
        ("业务驱动" if is_zh else "Business driver", "business_driver"),
        ("来源" if is_zh else "Source", "source"),
    ]
    detail_payload = json.dumps(detail_fields, ensure_ascii=False)
    frontend_sections = [
        ("页面" if is_zh else "Pages", "pages"),
        ("组件" if is_zh else "Components", "components"),
        ("状态" if is_zh else "States", "states"),
        ("交互" if is_zh else "Interactions", "interactions"),
        ("数据合同" if is_zh else "Data contracts", "data_contracts"),
        ("质量要求" if is_zh else "Quality requirements", "quality"),
    ]
    frontend_sections_payload = json.dumps(frontend_sections, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--ink:#142033;--muted:#64748b;--line:#cbd5e1;--panel:#f8fafc;--accent:#315da8}}
*{{box-sizing:border-box}} body{{margin:0;font:15px/1.5 system-ui,sans-serif;color:var(--ink);background:#eef2f7}}
header{{padding:24px 30px;background:white;border-bottom:1px solid var(--line)}} h1{{margin:0 0 4px;font-size:26px}}
.layout{{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:18px;padding:18px;min-height:calc(100vh - 100px)}}
.canvas,.side{{background:white;border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 24px #1e293b12}}
.toolbar{{display:flex;flex-wrap:wrap;gap:10px;padding:14px;border-bottom:1px solid var(--line)}} select,input,textarea,button{{font:inherit}} select,input,textarea{{padding:9px 11px;border:1px solid var(--line);border-radius:9px;background:white}} button{{padding:9px 12px;border:1px solid #94a3b8;border-radius:9px;background:white;cursor:pointer}} button.primary{{background:var(--accent);color:white;border-color:var(--accent)}}
#diagram{{width:100%;height:650px}} .edge{{stroke:#7b8798;stroke-width:2;marker-end:url(#arrow)}} .edge-label{{font-size:12px;fill:#475569}}
.node rect{{fill:#f8fafc;stroke:var(--accent);stroke-width:2}} .node text{{pointer-events:none}} .node{{cursor:pointer}}
.frontend-element rect.body{{fill:#f8fafc;stroke:#315da8;stroke-width:2}} .frontend-element[data-kind="page"] rect.body{{fill:#eef6ff;stroke:#1d4ed8}} .frontend-element.selected rect.body{{stroke:#ea580c;stroke-width:3}} .frontend-element{{cursor:move}} .resize-handle{{fill:#fff;stroke:#ea580c;stroke-width:2;cursor:nwse-resize}}
.edge-label{{text-anchor:middle;paint-order:stroke;stroke:white;stroke-width:6px;stroke-linejoin:round}}
.side{{padding:18px}} .card{{padding:12px 0;border-bottom:1px solid #e2e8f0}} .label{{font-size:12px;text-transform:uppercase;color:var(--muted)}}
.feedback{{margin-top:20px;padding:13px;border-radius:12px;background:#fff7ed;border:1px solid #fed7aa}}
.editor{{display:grid;gap:10px}} .editor label{{display:grid;gap:5px;font-size:12px;color:var(--muted)}} .editor input,.editor textarea{{width:100%}} .geometry{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}} .note{{color:var(--muted);font-size:12px}} .annotation-item{{padding:9px;margin-top:8px;border:1px solid #fed7aa;border-radius:9px;background:#fff7ed}}
@media(max-width:850px){{.layout{{grid-template-columns:1fr}} .side{{order:-1}}}}
</style>
</head>
<body>
<header><h1>{title}</h1><div>{html.escape(model.get("scope", "Scope not recorded"))}</div></header>
<main class="layout">
<section class="canvas">
<div class="toolbar"><select id="view"></select><input id="search" type="search" placeholder="{ui["search"]}"><button id="reset-layout">{ui["reset"]}</button><button id="export-model" class="primary">{ui["export"]}</button></div>
<svg id="diagram" viewBox="0 0 1200 700" role="img" aria-label="{ui["diagram_label"]}">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7b8798"/></marker></defs>
<g id="edges"></g><g id="nodes"></g></svg>
</section>
<aside class="side"><h2>{ui["feedback"]}</h2><div id="feedback"></div><h2>{ui["selected"]}</h2><div id="details">{ui["instruction"]}</div><div id="frontend-module-overview" hidden></div><form id="element-editor" class="editor" hidden><h3>{ui["edit"]}</h3><label>{ui["element_title"]}<input id="element-title"></label><label>{ui["details"]}<textarea id="element-details" rows="4"></textarea></label><label>{ui["requirements"]}<input id="element-requirements"></label><div class="label">{ui["geometry"]}</div><div class="geometry"><input id="element-x" type="number"><input id="element-y" type="number"><input id="element-width" type="number" min="40"><input id="element-height" type="number" min="30"></div><button class="primary" type="submit">{ui["apply"]}</button><div class="note">{ui["local_note"]}</div><label>{ui["annotation"]}<textarea id="annotation-text" rows="3" placeholder="{ui["annotation_placeholder"]}"></textarea></label><button id="add-annotation" type="button">{ui["add_annotation"]}</button><div id="annotation-list"></div></form></aside>
</main>
<script>
let model={payload};
const initialModel=JSON.parse(JSON.stringify(model));
const svgNS="http://www.w3.org/2000/svg";
const viewSelect=document.getElementById("view");
const search=document.getElementById("search");
let nodeById={{}};
let edgeById={{}};
const detailFields={detail_payload};
const frontendSections={frontend_sections_payload};
const diagram=document.getElementById("diagram");
const editor=document.getElementById("element-editor");
let selectedFrontend=null;
let gesture=null;
function refreshIndexes(){{nodeById=Object.fromEntries(model.nodes.map(n=>[n.id,n]));edgeById=Object.fromEntries(model.relationships.map(e=>[e.id,e]))}}
function el(name,attrs,text){{const n=document.createElementNS(svgNS,name);for(const [k,v] of Object.entries(attrs||{{}}))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n}}
function positions(ids){{const cols=Math.min(3,Math.max(1,ids.length));return Object.fromEntries(ids.map((id,i)=>[id,[85+(i%cols)*365,95+Math.floor(i/cols)*190]]))}}
function requirementSummary(ids){{if(!ids?.length)return "UNMAPPED";return ids[0]+(ids.length>1?` +${{ids.length-1}}`:"")}}
function showDetails(node){{selectedFrontend=null;editor.hidden=true;document.getElementById("frontend-module-overview").hidden=true;const box=document.getElementById("details");box.hidden=false;box.replaceChildren();for(const [label,key] of detailFields){{const card=document.createElement("div");card.className="card";const l=document.createElement("div");l.className="label";l.textContent=label;const v=document.createElement("div");v.textContent=node[key]||"UNKNOWN";card.append(l,v);box.append(card)}}}}
function frontendModule(id){{return (model.frontend_modules||[]).find(item=>item.id===id)}}
function activeView(){{return model.views.find(v=>v.id===viewSelect.value)||model.views[0]}}
function activeFrontend(){{const view=activeView();return view.kind==="frontend"?frontendModule(view.frontend_module_id):null}}
function selectedElement(){{if(!selectedFrontend)return null;const module=frontendModule(selectedFrontend.moduleId);return module?.canvas.elements.find(item=>item.id===selectedFrontend.elementId)||null}}
function renderAnnotations(module,element){{const list=document.getElementById("annotation-list");list.replaceChildren();for(const note of module.annotations||[]){{if(note.element_id!==element.id)continue;const item=document.createElement("div");item.className="annotation-item";item.textContent=`${{note.status||"open"}}: ${{note.text}}`;list.append(item)}}}}
function requirementText(value){{if(typeof value==="string")return value;if(Array.isArray(value))return value.map(requirementText).join(" · ");if(value&&typeof value==="object")return Object.entries(value).map(([key,item])=>`${{key}}: ${{requirementText(item)}}`).join(" · ");return String(value??"UNKNOWN")}}
function showFrontendOverview(module){{const overview=document.getElementById("frontend-module-overview");document.getElementById("details").hidden=true;editor.hidden=true;overview.hidden=false;overview.replaceChildren();const heading=document.createElement("h3");heading.textContent=module.name;overview.append(heading);const meta=document.createElement("div");meta.className="note";meta.textContent=`${{module.surface}} · ${{module.template_ref}} · ${{module.requirement_ids.join(", ")}}`;overview.append(meta);for(const [label,key] of frontendSections){{const card=document.createElement("div");card.className="card";const title=document.createElement("div");title.className="label";title.textContent=label;const value=document.createElement("div");value.textContent=requirementText(module.implementation_requirements[key]);card.append(title,value);overview.append(card)}}}}
function showFrontendEditor(module,element){{selectedFrontend={{moduleId:module.id,elementId:element.id}};document.getElementById("details").hidden=true;document.getElementById("frontend-module-overview").hidden=true;editor.hidden=false;document.getElementById("element-title").value=element.title;document.getElementById("element-details").value=element.details||"";document.getElementById("element-requirements").value=(element.requirement_ids||[]).join(", ");for(const key of ["x","y","width","height"])document.getElementById(`element-${{key}}`).value=element[key];renderAnnotations(module,element)}}
function renderStandard(view){{diagram.setAttribute("viewBox","0 0 1200 700");const q=search.value.trim().toLowerCase();const ids=view.node_ids.filter(id=>!q||JSON.stringify(nodeById[id]).toLowerCase().includes(q));const visible=new Set(ids);const pos=positions(ids);const edges=document.getElementById("edges");const nodes=document.getElementById("nodes");edges.replaceChildren();nodes.replaceChildren();for(const id of view.relationship_ids){{const edge=edgeById[id];if(!visible.has(edge.source)||!visible.has(edge.target))continue;const [x1,y1]=pos[edge.source],[x2,y2]=pos[edge.target];edges.append(el("line",{{class:"edge",x1:x1+260,y1:y1+45,x2:x2,y2:y2+45}}));edges.append(el("text",{{class:"edge-label",x:(x1+x2+260)/2,y:(y1+y2)/2+30}},edge.label))}}for(const id of ids){{const node=nodeById[id],[x,y]=pos[id];const g=el("g",{{class:"node",tabindex:"0"}});g.append(el("rect",{{x,y,width:260,height:90,rx:14}}),el("text",{{x:x+16,y:y+30,"font-size":17,"font-weight":650}},node.name),el("text",{{x:x+16,y:y+55,"font-size":13,fill:"#64748b"}},node.type||"element"),el("text",{{x:x+16,y:y+76,"font-size":12,fill:"#475569"}},node.business_driver||""));g.addEventListener("click",()=>showDetails(node));g.addEventListener("keydown",e=>{{if(e.key==="Enter")showDetails(node)}});nodes.append(g)}}}}
function renderFrontend(view){{const module=frontendModule(view.frontend_module_id);if(!selectedFrontend||selectedFrontend.moduleId!==module.id)showFrontendOverview(module);const canvas=module.canvas;diagram.setAttribute("viewBox",`0 0 ${{canvas.width}} ${{canvas.height}}`);const q=search.value.trim().toLowerCase();const visibleElements=canvas.elements.filter(item=>!q||JSON.stringify(item).toLowerCase().includes(q));const visible=new Set(visibleElements.map(item=>item.id));const byId=Object.fromEntries(canvas.elements.map(item=>[item.id,item]));const edges=document.getElementById("edges");const nodes=document.getElementById("nodes");edges.replaceChildren();nodes.replaceChildren();for(const connector of canvas.connectors||[]){{if(!visible.has(connector.source)||!visible.has(connector.target))continue;const source=byId[connector.source],target=byId[connector.target];const x1=source.x+source.width,y1=source.y+source.height/2,x2=target.x,y2=target.y+target.height/2;edges.append(el("line",{{class:"edge",x1,y1,x2,y2}}));edges.append(el("text",{{class:"edge-label",x:(x1+x2)/2,y:(y1+y2)/2-8}},connector.label||""))}}for(const item of visibleElements){{const selected=selectedFrontend?.moduleId===module.id&&selectedFrontend?.elementId===item.id;const g=el("g",{{class:`frontend-element${{selected?" selected":""}}`,"data-id":item.id,"data-kind":item.kind,tabindex:"0"}});g.append(el("rect",{{class:"body",x:item.x,y:item.y,width:item.width,height:item.height,rx:12}}),el("text",{{x:item.x+14,y:item.y+28,"font-size":17,"font-weight":650,"pointer-events":"none"}},item.title),el("text",{{x:item.x+14,y:item.y+50,"font-size":12,fill:"#64748b","pointer-events":"none"}},`${{item.kind}} · ${{requirementSummary(item.requirement_ids)}}`));if(selected)g.append(el("rect",{{class:"resize-handle",x:item.x+item.width-7,y:item.y+item.height-7,width:14,height:14,rx:3}}));g.addEventListener("click",()=>showFrontendEditor(module,item));g.addEventListener("keydown",event=>{{if(event.key==="Enter")showFrontendEditor(module,item)}});nodes.append(g)}}}}
function render(){{const view=activeView();if(view.kind==="frontend")renderFrontend(view);else renderStandard(view)}}
function svgPoint(event){{const point=diagram.createSVGPoint();point.x=event.clientX;point.y=event.clientY;return point.matrixTransform(diagram.getScreenCTM().inverse())}}
diagram.addEventListener("pointerdown",event=>{{const target=event.target.closest?.(".frontend-element");if(!target)return;const module=activeFrontend();if(!module)return;const item=module.canvas.elements.find(element=>element.id===target.dataset.id);if(!item)return;showFrontendEditor(module,item);const point=svgPoint(event);gesture={{pointerId:event.pointerId,moduleId:module.id,elementId:item.id,mode:event.target.classList.contains("resize-handle")?"resize":"move",startX:point.x,startY:point.y,original:{{x:item.x,y:item.y,width:item.width,height:item.height}}}};diagram.setPointerCapture(event.pointerId);event.preventDefault()}});
diagram.addEventListener("pointermove",event=>{{if(!gesture||gesture.pointerId!==event.pointerId)return;const module=frontendModule(gesture.moduleId);const item=module.canvas.elements.find(element=>element.id===gesture.elementId);const point=svgPoint(event),dx=point.x-gesture.startX,dy=point.y-gesture.startY;if(gesture.mode==="move"){{item.x=Math.max(0,gesture.original.x+dx);item.y=Math.max(0,gesture.original.y+dy)}}else{{item.width=Math.max(40,gesture.original.width+dx);item.height=Math.max(30,gesture.original.height+dy)}}renderFrontend(activeView())}});
diagram.addEventListener("pointerup",event=>{{if(!gesture||gesture.pointerId!==event.pointerId)return;const module=frontendModule(gesture.moduleId);const item=module.canvas.elements.find(element=>element.id===gesture.elementId);gesture=null;showFrontendEditor(module,item)}});
editor.addEventListener("submit",event=>{{event.preventDefault();const module=activeFrontend(),item=selectedElement();if(!module||!item)return;const ids=document.getElementById("element-requirements").value.split(",").map(value=>value.trim()).filter(Boolean);if(ids.some(id=>!module.requirement_ids.includes(id))){{alert({json.dumps(ui['invalid_requirement'], ensure_ascii=False)});return}}item.title=document.getElementById("element-title").value.trim()||item.title;item.details=document.getElementById("element-details").value.trim();item.requirement_ids=ids;for(const key of ["x","y","width","height"])item[key]=Math.max(key==="width"?40:key==="height"?30:0,Number(document.getElementById(`element-${{key}}`).value)||0);renderFrontend(activeView());showFrontendEditor(module,item)}});
document.getElementById("add-annotation").addEventListener("click",()=>{{const module=activeFrontend(),item=selectedElement(),input=document.getElementById("annotation-text");const value=input.value.trim();if(!module||!item||!value)return;module.annotations=module.annotations||[];module.annotations.push({{id:`annotation-${{Date.now()}}`,element_id:item.id,status:"open",text:value}});input.value="";renderAnnotations(module,item)}});
document.getElementById("export-model").addEventListener("click",()=>{{const blob=new Blob([JSON.stringify(model,null,2)+"\\n"],{{type:"application/json"}});const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download="architecture-model.edited.json";link.click();URL.revokeObjectURL(link.href)}});
document.getElementById("reset-layout").addEventListener("click",()=>{{model=JSON.parse(JSON.stringify(initialModel));selectedFrontend=null;editor.hidden=true;document.getElementById("frontend-module-overview").hidden=true;document.getElementById("details").hidden=false;refreshIndexes();render()}});
for(const view of model.views){{const option=document.createElement("option");option.value=view.id;option.textContent=view.title||view.id;viewSelect.append(option)}}
const feedback=document.getElementById("feedback");for(const item of model.feedback||[]){{const card=document.createElement("div");card.className="feedback";card.textContent=(item.severity?item.severity.toUpperCase()+": ":"")+item.message;feedback.append(card)}}
viewSelect.addEventListener("change",()=>{{selectedFrontend=null;editor.hidden=true;document.getElementById("frontend-module-overview").hidden=true;document.getElementById("details").hidden=false;render()}});search.addEventListener("input",render);refreshIndexes();render();
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a stable architecture model as SVG, HTML, and Markdown.")
    parser.add_argument("model", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        model = load_model(args.model)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "architecture.svg").write_text(render_svg(model), encoding="utf-8")
        (args.output_dir / "architecture.html").write_text(render_html(model), encoding="utf-8")
        (args.output_dir / "architecture-summary.md").write_text(render_summary(model), encoding="utf-8")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Rendered architecture views in {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
