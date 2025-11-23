from typing import AsyncGenerator, Generator, Optional
import requests
import json
import httpx
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

API_BASE_URL = "http://localhost:8000/api/v1"

async def async_stream_research(query: str, max_iteration: int, depth: str, model_provider: str, model_name: str, api_key: str | None = None) -> AsyncGenerator:
    url = f"{API_BASE_URL}/research/stream"

    payload = {
        "query": query,
        "max_iteration": max_iteration,
        "depth": depth,
        "model_provider": model_provider,
        "model_name": model_name
    }

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                prefix = "data "

                async for line in response.aiter_lines():
                    if line.startswith(prefix):
                        yield json.loads(line[len(prefix): ])

        except Exception as e:
            yield {"type": "error", "error": str(e)}

def stream_research(query: str, max_iteration: int, depth: str, model_provider: str, model_name: str, api_key: str | None = None) -> Generator:
    """Stream research results from the API"""
    url = f"{API_BASE_URL}/research/stream"
    
    payload = {
        "query": query,
        "max_iteration": max_iteration,
        "depth": depth,
        "model_provider": model_provider,
        "model_name": model_name
    }
    
    try:
        with requests.post(url, json=payload, stream=True, timeout=300) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = json.loads(line[6:])
                        yield data
    except requests.exceptions.RequestException as e:
        yield {"type": "error", "error": str(e)}
            

def format_planner_output(obj: dict) -> str:
    queries = obj.get("queries", [])
    rationale = obj.get("rationals", "")

    text = "## 📝 Research Plan\n"
    if queries:
        text += "**Queries:**\n"
        for q in queries:
            tools = ", ".join(q.get("tools", []))
            text += f"- **{q.get('query', '')}** (tools: {tools})\n"

    if rationale:
        text += "\n**Rationale:**\n"
        text += f"{rationale}\n"

    return text


def format_report_output(obj: dict) -> str:
    report = obj.get("report", "")
    citations = obj.get("citations", [])
    metadata = obj.get("metadata", {})

    text = report + "\n\n---\n\n"

    # Citations
    if citations:
        text += "## 🔗 Citations\n"
        for c in citations:
            text += (
                f"- **[{c.get('id')}]** {c.get('claim')}\n"
                f"  _Source:_ {c.get('source_type')}\n"
                f"  _URL:_ {c.get('source_url')}\n\n"
            )

    # Metadata
    if metadata:
        text += "## 📊 Metadata\n"
        text += f"- Word Count: {metadata.get('word_count')}\n"
        text += f"- Number of Sources: {metadata.get('num_sources')}\n"

        if "source_breakdown" in metadata:
            text += "- Source Breakdown:\n"
            for sb in metadata["source_breakdown"]:
                text += f"  - {sb.get('source_type')}: {sb.get('count')}\n"

    return text


def format_quality_output(obj: dict) -> str:
    passed = obj.get("passed")
    scores = obj.get("scores", {})
    issues = obj.get("citation_issues", [])
    gaps = obj.get("coverage_gaps", [])
    action = obj.get("action")
    next_steps = obj.get("next_steps", {})

    text = "## 📏 Quality Check\n"
    text += f"- **Passed:** {'✅ Yes' if passed else '❌ No'}\n\n"

    if scores:
        text += "### Scores\n"
        for k, v in scores.items():
            text += f"- **{k}:** {v}\n"

    if issues:
        text += "\n### Citation Issues\n"
        for i in issues:
            text += f"- {i}\n"

    if gaps:
        text += "\n### Coverage Gaps\n"
        for g in gaps:
            text += f"- {g}\n"

    if action:
        text += f"\n### Action: **{action}**\n"

    if next_steps:
        text += "\n### Next Steps\n"
        text += "```json\n" + json.dumps(next_steps, indent=2) + "\n```"

    return text


def _split_concatenated_json(raw: str) -> list[dict]:
    """
    Split a string like '{}{}{}' into [dict, dict, dict].
    Uses brace depth tracking; ignores braces inside strings.
    """
    objs = []
    buf = ""
    depth = 0
    in_string = False
    escape = False

    for ch in raw:
        buf += ch

        if ch == '"' and not escape:
            in_string = not in_string

        if not in_string:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and buf.strip():
                    try:
                        objs.append(json.loads(buf))
                    except Exception:
                        # Ignore parse errors and keep going
                        pass
                    buf = ""

        escape = (ch == '\\' and not escape)

    return objs


def format_stream_output(raw: str) -> str:
    """
    Entry point for Streamlit:
    Takes the full raw token stream and returns pretty markdown.
    """
    objs = _split_concatenated_json(raw)

    # If we couldn't parse anything, just return raw
    if not objs:
        return raw

    parts = []
    for obj in objs:
        if "queries" in obj and "rationals" in obj:
            parts.append(format_planner_output(obj))
        elif "report" in obj:
            parts.append(format_report_output(obj))
        elif "passed" in obj and "scores" in obj:
            parts.append(format_quality_output(obj))

    if not parts:
        return raw

    return "\n\n".join(parts)

def format_final_report(raw: str) -> str:
    """
    From a concatenated JSON stream like:
      {planner1}{report1}{qc1}{planner2}{report2}{qc2}
    return ONLY the last report (+ its quality check if present),
    nicely formatted as markdown.
    """
    objs = _split_concatenated_json(raw)

    if not objs:
        return raw  # fallback: nothing parsed, return raw

    last_report = None
    last_quality = None

    for obj in objs:
        if isinstance(obj, dict):
            if "report" in obj:
                last_report = obj
            elif "passed" in obj and "scores" in obj:
                last_quality = obj

    # If we never saw a report, just return raw
    if not last_report:
        return raw

    parts = [format_report_output(last_report)]

    # Attach the last quality block if available (optional)
    if last_quality:
        parts.append(format_quality_output(last_quality))

    return "\n\n".join(parts)


def markdown_to_pdf_bytes(md_text: str, title: Optional[str] = None) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    # Optional title at the top
    if title:
        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 18))

    lines = md_text.split("\n")
    for raw_line in lines:
        line = raw_line.rstrip()

        # Blank line = vertical space
        if not line.strip():
            story.append(Spacer(1, 10))
            continue

        # Very naive heading detection: lines starting with '#'
        if line.startswith("#"):
            # Count number of #'s to determine level
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()

            if level == 1:
                style = styles["Heading1"]
            elif level == 2:
                style = styles["Heading2"]
            else:
                style = styles["Heading3"]
        else:
            text = line
            style = styles["BodyText"]

        # Strip some basic markdown emphasis markers so they don't show as raw symbols
        text = text.replace("**", "").replace("__", "")

        story.append(Paragraph(text, style))
        story.append(Spacer(1, 6))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

