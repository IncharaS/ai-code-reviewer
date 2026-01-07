
# AI Code Reviewer - Multi Agent Python Reviewer with Memory and Auto Patch Suggestions

This project is a multi agent AI code reviewer for Python files built using the Google Agent Development Kit (ADK) and Gemini models. It runs several specialized review agents in parallel, uses an evaluator agent as an "LLM as judge" with a rubric, maintains a simple memory of past reviews, and can generate diffs for code fixes.

The system can be used in two ways:

1. **CLI mode**: `python main.py path/to/file.py`
2. **Cloud Run API**: Containerized FastAPI app deployed to Cloud Run
3. **Optional Streamlit UI**: Simple front end to upload a `.py` file and view the AI review

The project is focused on **Python** code review.


## 1. Problem

Static code analysis tools like `pycodestyle`, `pylint`, or `bandit` are very good at finding specific classes of issues, but they are:

- Run separately, one by one.
- Hard to unify into a single coherent summary.
- Not aware of context across multiple runs of the same file.
- Not able to reason about trade offs or "quality over time".

At the same time, LLMs are very good at **summarizing**, **evaluating**, and **deciding**, but they are not perfect at:

- Precisely matching linters' rules.
- Producing structured outputs that are easy to automate on.

This project tries to combine both:

- Use **classical tools** for precise detection.
- Use **agents + Gemini** to orchestrate, aggregate, score, and optionally patch.



## 2. High level solution

Given a Python file path, the system:

1. **Runs four review agents in parallel**:
   - Style review (pycodestyle)
   - Correctness review (pylint)
   - Security review (bandit)
   - Performance review (simple rule based stub for now)

2. **Combines their structured outputs** into a single JSON "review report".

3. **Calls an evaluator agent** that:
   - Uses Gemini to:
     - Score style, correctness, security, performance on a 1–10 scale.
     - Compute an `overall_score`.
     - Decide whether the file needs a retry (`should_retry`).
     - Generate `improvement_instructions`.
   - Reads **past reviews from disk** for that file to produce a "trend" summary:
     - Are issues repeating across runs?
     - Is quality improving or not?

4. **Optional retry loop with patch generation**:
   - If `should_retry` is `True`, the system can call a **patch generator agent**:
     - Takes the original code + issues.
     - Returns a unified diff patch (`diff` format) to fix the code.
   - The coordinator can then:
     - Apply the patch (conceptually).
     - Re run the four review agents.
     - Call the evaluator again, up to a limited number of retries.

5. Returns a final human readable summary that can be shown in CLI, Streamlit, or any UI.


## 3. Architecture

### 3.1 Agent graph

The architecture is built using ADK `Agent`, `SequentialAgent`, and `ParallelAgent`.

**Agents:**

- `style_review_agent`
  - Tool: `run_style_review(path: str) -> StyleReviewOutput`
  - Under the hood uses `pycodestyle` to detect PEP8 style issues.

- `correctness_review_agent`
  - Tool: `run_correctness_review(path: str) -> CorrectnessOutput`
  - Uses `pylint` to find issues like unused imports, missing docstrings, etc.

- `security_review_agent`
  - Tool: `run_security_review(path: str) -> SecurityOutput`
  - Uses `bandit` to flag common Python security issues.

- `performance_review_agent`
  - Tool: `run_performance_review(path: str) -> PerformanceOutput`
  - Simple rule based stub for now. The agent is already wired, and can be extended with custom checks.

- `evaluator_agent`
  - Tool: `run_evaluate(report: str, file: str) -> EvaluationOutput`
  - Uses Gemini to:
    - Read the combined review report (JSON as string).
    - Read a "trend preview" of past reviews from the memory store.
    - Produce:
      - `style_score: int`
      - `correctness_score: int`
      - `security_score: int`
      - `performance_score: int`
      - `overall_score: float`
      - `should_retry: bool`
      - `improvement_instructions: str`
      - `comments: str`
      - `trend: str` (LLM generated based on history)

- `patch_generator_agent`
  - Tool: `generate_patch(original_code: str, style_issues: list, correctness_issues: list, security_issues: list, performance_issues: list) -> PatchOutput`
  - Uses Gemini to:
    - Read the original file contents and all issues.
    - Generate a patch in `diff` format:
      ```diff
      --- original
      +++ updated
      @@
      ...
      ```

- `parallel_review_team` (ADK `ParallelAgent`)
  - Sub agents:
    - `style_review_agent`
    - `correctness_review_agent`
    - `security_review_agent`
    - `performance_review_agent`
  - All four are executed in parallel for better latency.

- `retry_manager_agent`
  - Main responsibilities:
    - Combine the four review outputs into one JSON.
    - Call `evaluator_agent`.
    - If `should_retry` is `True`, call `patch_generator_agent` and conceptually apply the patch.
    - Re run the review team and evaluator up to a maximum retry count (for example, 3).

- `coordinator_agent` (ADK `SequentialAgent`)
  - `SequentialAgent` that runs:
    1. `parallel_review_team`
    2. `retry_manager_agent`
  - This is the root agent used by the CLI and Cloud Run API.

### 3.2 Memory

Memory is implemented as a simple "memory bank" on disk, per file.

- Module: `memory/memory_manager.py`
- Core functions:
  - `load_past_reviews(file: str) -> list[dict]`
  - `save_review(file: str, evaluation: EvaluationOutput) -> None`
- Storage strategy:
  - For each file path, the project stores an append-only log of past evaluations, for example in JSON.
  - `evaluator_agent` uses `load_past_reviews` to build the `trend` field in its output, so it can say things like:
    - "Trailing whitespace issues are recurring."
    - "Security issues are going down across runs."

This is intentionally simple, but demonstrates the **"Memory Bank"** concept from the course: an external store that agents consult to reason about history.

---

## 4. Technical design details

### 4.1 Tools and outputs

Each review tool returns a **Pydantic model**. Example:

```python
class StyleIssue(BaseModel):
    line: int
    column: int
    code: str
    message: str

class StyleReviewOutput(BaseModel):
    file: str
    issue_count: int
    issues: List[StyleIssue]
````

This makes the outputs:

* Strongly typed.
* Easy for the evaluator to consume.
* Easy to serialize into JSON for logging or a UI.

Similar models exist for correctness, security, and performance.

### 4.2 Evaluator agent as LLM judge

The evaluator uses Gemini with a detailed instruction:

* Read `report` (combined JSON text).
* Read `file` name and `trend` preview.
* Score each dimension 1 to 10.
* Compute `overall_score` as the average of the four scores.
* Decide `should_retry` with a threshold (for example, `overall_score < 7`).
* Generate `improvement_instructions` that are specific and actionable.

The actual returned object is something like:

```python
class EvaluationOutput(BaseModel):
    style_score: int
    correctness_score: int
    security_score: int
    performance_score: int
    overall_score: float
    should_retry: bool
    improvement_instructions: str
    comments: str
    trend: str
```

The use of `run_evaluate` as a tool ensures that:

* The LLM's natural language reasoning happens in the prompt.
* The final result is structured and easy to use programmatically.

### 4.3 Retry and patch loop

The retry loop is managed by the retry manager agent. The high level logic is:

1. Receive review outputs from `parallel_review_team`.
2. Build a JSON report.
3. Call `evaluator_agent` with:

   * `report` (JSON string)
   * `file` path
4. If `should_retry` is `False`:

   * End.
5. Else:

   * Call `patch_generator_agent` with:

     * `original_code`
     * `style_issues`, `correctness_issues`, `security_issues`, `performance_issues`
   * Apply the patch (conceptually; currently the system can display the patch and it is structured so it can be applied automatically).
   * Re run `parallel_review_team` on the patched code.
   * Call `evaluator_agent` again.
   * Continue up to a maximum retry count.

This pattern demonstrates:

* Multi agent collaboration.
* LLM as a supervisor/critic.
* LLM as a patch generator over structured diagnostics.


## 5. Running locally

### 5.1 Prerequisites

* Python 3.12 (or 3.10+)
* A valid Gemini API key in the environment as `GOOGLE_API_KEY`
* `pip` installed

### 5.2 Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:

* `google-adk`
* `google-genai`
* `pycodestyle`
* `pylint`
* `bandit`
* `pydantic`
* `fastapi` and `uvicorn` if using Cloud Run / API
* `streamlit` if using the UI

### 5.3 CLI usage

From the project root:

```bash
export GOOGLE_API_KEY=your_key_here    # or set in Windows env
python main.py path/to/file.py
```

You will see:

* The agent session id.
* Intermediate logs from sub agents.
* The final summary from the coordinator agent.

## 6. Cloud Run deployment

The project includes a simple HTTP API wrapper around `coordinator_agent` using FastAPI (`app.py`) and a `Dockerfile` suitable for Cloud Run.

### 6.1 Build and push image

```bash
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/ai-code-reviewer
```

### 6.2 Deploy to Cloud Run

```bash
gcloud run deploy ai-code-reviewer \
  --image gcr.io/$(gcloud config get-value project)/ai-code-reviewer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_GEMINI_KEY
```

Cloud Run will output a URL like:

```text
https://ai-code-reviewer-xxxxxxxxx-uc.a.run.app
```

### 6.3 API usage

The API exposes:

* `GET /healthz` - basic health check
* `POST /review` - review a Python file

Example:

```bash
curl -X POST "https://ai-code-reviewer-xxxxxxxxx-uc.a.run.app/review" \
  -F "file=@main.py"
```

Response:

```json
{
  "file_name": "main.py",
  "tmp_path": "/tmp/tmpabcd1234.py",
  "review": "Full coordinator agent summary here..."
}
```

## 7. Repository structure

```text
ai-code-reviewer/
  agents/
    style_review_agent.py
    correctness_review_agent.py
    security_review_agent.py
    performance_review_agent.py
    evaluator_agent.py
    patch_generator_agent.py
    coordinator_agent.py      # or review_coordinator_agent.py
  services/
    style_review.py
    correctness_review.py
    security_review.py
    performance_review.py
  memory/
    memory_manager.py
  main.py                     # CLI entry
  app.py                      # FastAPI Cloud Run entry (if used)
  streamlit_app.py            # Optional UI
  tests/
    test_patch_generator.py
    test_coordinator.py
  requirements.txt
  Dockerfile
  README.md


