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
    return model


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


def render_svg(model: dict[str, Any]) -> str:
    node_by_id = {node["id"]: node for node in model["nodes"]}
    relationship_by_id = {edge["id"]: edge for edge in model["relationships"]}
    section_heights = [
        150
        + max(1, (len(view.get("node_ids", [])) + 2) // 3) * 190
        + len(view.get("relationship_ids", [])) * 24
        for view in model["views"]
    ]
    height = 90 + sum(section_heights)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">',
        "<defs><marker id=\"arrow\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" fill=\"#637083\"/></marker></defs>",
        "<style>.node{fill:#f7f9fc;stroke:#3659a2;stroke-width:2}.name{font:600 17px system-ui;fill:#132238}.meta{font:13px system-ui;fill:#516174}.edge{stroke:#637083;stroke-width:2;marker-end:url(#arrow)}.label{font:600 11px system-ui;fill:#334155}.legend{font:13px system-ui;fill:#334155}</style>",
        f'<text x="55" y="45" font-family="system-ui" font-size="26" font-weight="700">{html.escape(model["title"])}</text>',
    ]
    offset = 70
    for view, section_height in zip(model["views"], section_heights):
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
    }
    detail_fields = [
        ("名称" if is_zh else "Name", "name"),
        ("类型" if is_zh else "Type", "type"),
        ("职责" if is_zh else "Responsibility", "responsibility"),
        ("业务驱动" if is_zh else "Business driver", "business_driver"),
        ("来源" if is_zh else "Source", "source"),
    ]
    detail_payload = json.dumps(detail_fields, ensure_ascii=False)
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
.toolbar{{display:flex;gap:10px;padding:14px;border-bottom:1px solid var(--line)}} select,input{{padding:9px 11px;border:1px solid var(--line);border-radius:9px;background:white}}
#diagram{{width:100%;height:650px}} .edge{{stroke:#7b8798;stroke-width:2;marker-end:url(#arrow)}} .edge-label{{font-size:12px;fill:#475569}}
.node rect{{fill:#f8fafc;stroke:var(--accent);stroke-width:2}} .node text{{pointer-events:none}} .node{{cursor:pointer}}
.edge-label{{text-anchor:middle;paint-order:stroke;stroke:white;stroke-width:6px;stroke-linejoin:round}}
.side{{padding:18px}} .card{{padding:12px 0;border-bottom:1px solid #e2e8f0}} .label{{font-size:12px;text-transform:uppercase;color:var(--muted)}}
.feedback{{margin-top:20px;padding:13px;border-radius:12px;background:#fff7ed;border:1px solid #fed7aa}}
@media(max-width:850px){{.layout{{grid-template-columns:1fr}} .side{{order:-1}}}}
</style>
</head>
<body>
<header><h1>{title}</h1><div>{html.escape(model.get("scope", "Scope not recorded"))}</div></header>
<main class="layout">
<section class="canvas">
<div class="toolbar"><select id="view"></select><input id="search" type="search" placeholder="{ui["search"]}"></div>
<svg id="diagram" viewBox="0 0 1200 700" role="img" aria-label="{ui["diagram_label"]}">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7b8798"/></marker></defs>
<g id="edges"></g><g id="nodes"></g></svg>
</section>
<aside class="side"><h2>{ui["feedback"]}</h2><div id="feedback"></div><h2>{ui["selected"]}</h2><div id="details">{ui["instruction"]}</div></aside>
</main>
<script>
const model={payload};
const svgNS="http://www.w3.org/2000/svg";
const viewSelect=document.getElementById("view");
const search=document.getElementById("search");
const nodeById=Object.fromEntries(model.nodes.map(n=>[n.id,n]));
const edgeById=Object.fromEntries(model.relationships.map(e=>[e.id,e]));
const detailFields={detail_payload};
function el(name,attrs,text){{const n=document.createElementNS(svgNS,name);for(const [k,v] of Object.entries(attrs||{{}}))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n}}
function positions(ids){{const cols=Math.min(3,Math.max(1,ids.length));return Object.fromEntries(ids.map((id,i)=>[id,[85+(i%cols)*365,95+Math.floor(i/cols)*190]]))}}
function showDetails(node){{const box=document.getElementById("details");box.replaceChildren();for(const [label,key] of detailFields){{const card=document.createElement("div");card.className="card";const l=document.createElement("div");l.className="label";l.textContent=label;const v=document.createElement("div");v.textContent=node[key]||"UNKNOWN";card.append(l,v);box.append(card)}}}}
function render(){{const view=model.views.find(v=>v.id===viewSelect.value)||model.views[0];const q=search.value.trim().toLowerCase();const ids=view.node_ids.filter(id=>!q||JSON.stringify(nodeById[id]).toLowerCase().includes(q));const visible=new Set(ids);const pos=positions(ids);const edges=document.getElementById("edges");const nodes=document.getElementById("nodes");edges.replaceChildren();nodes.replaceChildren();for(const id of view.relationship_ids){{const edge=edgeById[id];if(!visible.has(edge.source)||!visible.has(edge.target))continue;const [x1,y1]=pos[edge.source],[x2,y2]=pos[edge.target];edges.append(el("line",{{class:"edge",x1:x1+260,y1:y1+45,x2:x2,y2:y2+45}}));edges.append(el("text",{{class:"edge-label",x:(x1+x2+260)/2,y:(y1+y2)/2+30}},edge.label))}}for(const id of ids){{const node=nodeById[id],[x,y]=pos[id];const g=el("g",{{class:"node",tabindex:"0"}});g.append(el("rect",{{x,y,width:260,height:90,rx:14}}),el("text",{{x:x+16,y:y+30,"font-size":17,"font-weight":650}},node.name),el("text",{{x:x+16,y:y+55,"font-size":13,fill:"#64748b"}},node.type||"element"),el("text",{{x:x+16,y:y+76,"font-size":12,fill:"#475569"}},node.business_driver||""));g.addEventListener("click",()=>showDetails(node));g.addEventListener("keydown",e=>{{if(e.key==="Enter")showDetails(node)}});nodes.append(g)}}}}
for(const view of model.views){{const option=document.createElement("option");option.value=view.id;option.textContent=view.title||view.id;viewSelect.append(option)}}
const feedback=document.getElementById("feedback");for(const item of model.feedback||[]){{const card=document.createElement("div");card.className="feedback";card.textContent=(item.severity?item.severity.toUpperCase()+": ":"")+item.message;feedback.append(card)}}
viewSelect.addEventListener("change",render);search.addEventListener("input",render);render();
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
