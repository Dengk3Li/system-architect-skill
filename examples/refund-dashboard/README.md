# Refund dashboard example

This fictional scenario shows the existing renderer's output. It is not a customer case, a production architecture, or an implementation claim. Every relationship remains a proposed design.

## Scenario

A support specialist reviews a refund request, submits it to the Refunds API, and keeps unsent work available when the request fails. The API owns eligibility and refund records; the browser owns transient form state.

- `R1`: review and submit one refund request.
- `R2`: preserve progress and expose a clear recovery action after failure.

## Open and try

Download `architecture.html` and open the saved file in a browser. GitHub's normal HTML file page displays source; it does not run the viewer.

1. Switch between **From support request to refund** and **Refund workspace and recovery**.
2. Select **Request review** in the frontend view and edit its title or position.
3. Add an annotation, then use **Export edited model** to retain the changes as JSON.

Edits remain proposals. Export before closing the page and validate the model before adopting it.

## Reproduce

From the repository root, using Python 3.10 or newer:

```bash
python3 examples/refund-dashboard/generate.py
```

The command reads only the checked-in fictional model and regenerates HTML, SVG, a summary, and the context-only README preview. No API key or model call is needed to reproduce these files.

中文：这是虚构退款工作台示例。下载 HTML 后可离线切换视图、修改前端组件、添加批注并导出 JSON。示例用于体验现有功能，所有关系均为提议，未核验真实生产系统。
