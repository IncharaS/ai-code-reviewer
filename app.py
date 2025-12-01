# app.py
import os
import tempfile
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from google.adk.runners import InMemoryRunner

# Import your root agent
from agents.review_coordinator_agent import coordinator_agent

app = FastAPI(
    title="AI Code Reviewer",
    description="Multi-agent AI code review service (style, correctness, security, performance, evaluator, patcher).",
    version="1.0.0",
)

# One runner instance for the whole process
runner = InMemoryRunner(agent=coordinator_agent, app_name="ai-code-reviewer")


async def run_review_on_path(path: str) -> str:
    """
    Uses the exact same pattern you already use in main.py:
    runner.run_debug(prompt) -> final natural-language summary.
    """
    prompt = f"Please review the Python file at: {path}"
    # run_debug is async in the newer ADK versions
    resp = await runner.run_debug(prompt)
    # In your logs, resp is often just the final string (but sometimes a list of Events).
    # Normalize to string for the API response.
    if isinstance(resp, str):
        return resp

    # If it's a list of Events, extract any text parts
    try:
        from google.genai.types import Content, Part  # type: ignore

        texts = []
        for evt in resp:
            if getattr(evt, "content", None) and getattr(evt.content, "parts", None):
                for part in evt.content.parts:
                    if getattr(part, "text", None):
                        texts.append(part.text)
        return "\n".join(texts) if texts else "No textual response from agent."
    except Exception:
        return str(resp)


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


@app.post("/review")
async def review_file(file: UploadFile = File(...)):
    """
    POST /review
    Content-Type: multipart/form-data
    Body: file=<uploaded python file>

    Returns the final coordinator_agent summary (markdown / text).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name.")

    try:
        raw_bytes = await file.read()
        try:
            code_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File is not valid UTF-8 text.")

        # Save to a temporary file, because all your review tools expect a file path.
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1] or ".py") as tmp:
            tmp.write(code_text.encode("utf-8"))
            tmp_path = tmp.name

        review_text = await run_review_on_path(tmp_path)

        return JSONResponse(
            {
                "file_name": file.filename,
                "tmp_path": tmp_path,
                "review": review_text,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
