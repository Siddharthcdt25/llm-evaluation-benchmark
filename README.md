# LLM Evaluation Benchmark

**A self-initiated, model-agnostic framework for systematically evaluating Large Language Models against a custom-designed benchmark.**

> ⚠️ **Status: FROZEN PROTOTYPE — Educational Research Experiment**
> This repository is not a standardized or scientifically validated benchmark. It is a self-driven engineering and research exercise built to understand *how LLM evaluation systems are designed, implemented, and validated* — not to rank or certify any model's general quality.

---

## Table of Contents

- [1. Why This Project Exists](#1-why-this-project-exists)
- [2. What This Project Is (and Is Not)](#2-what-this-project-is-and-is-not)
- [3. Core Methodological Principle](#3-core-methodological-principle)
- [4. Benchmark Design](#4-benchmark-design)
- [5. Evaluation Methods](#5-evaluation-methods)
- [6. Repository Structure](#6-repository-structure)
- [7. File-by-File Explanation](#7-file-by-file-explanation)
- [8. Development / Regression Tests](#8-development--regression-tests)
- [9. Execution Flow](#9-execution-flow)
- [10. Local Model Integration (Ollama)](#10-local-model-integration-ollama)
- [11. Key Findings From the Recorded Run](#11-key-findings-from-the-recorded-run)
- [12. Why the Experiment Was Frozen](#12-why-the-experiment-was-frozen)
- [13. Limitations](#13-limitations)
- [14. Lessons Learned](#14-lessons-learned)
- [15. Reproducibility](#15-reproducibility)
- [16. Future Research Directions](#16-future-research-directions)
- [17. Quick Reference](#17-quick-reference)
- [18. Final Takeaway](#18-final-takeaway)

---

## 1. Why This Project Exists

This project began from a practical, self-posed question:

> **How can an LLM be evaluated systematically through a predefined benchmark, rather than by manually reading its responses one at a time?**

Rather than adopting an existing public benchmark, I chose to **design my own** — end to end — as a hands-on way to learn:

- What a real LLM benchmark actually contains (structure, metadata, evaluation criteria)
- How to design questions, expected answers, and category-specific evaluation logic
- How different evaluators are matched to different response types
- How to connect a benchmark to a real model (local or API-based)
- How to automatically classify outcomes as `PASS`, `FAIL`, or `ERROR`
- How to compute and visualize aggregate and category-level metrics
- Where an evaluator itself can produce **false negatives** and distort an apparent model score
- Why **reproducibility**, **evaluator validity**, and **execution security** matter in evaluation pipelines

This is fundamentally a **practice / research-driven project born from my own idea**, not a tutorial followed or a benchmark copied from elsewhere.

---

## 2. What This Project Is (and Is Not)

### ✅ What it IS
- A **self-initiated AI/ML engineering and research practice project**
- A **model-agnostic evaluation framework** — the benchmark and evaluator are decoupled from any specific model
- A complete, working **evaluation pipeline**: benchmark definition → model client → evaluation engine → results → metrics → dashboard
- A **case study in evaluator validity** — i.e., understanding when an evaluation *system* itself can be wrong, even when the model is right

### ❌ What it is NOT
- **Not** a standardized, peer-reviewed, or publicly recognized benchmark
- **Not** a claim about any model's general quality, safety, or real-world reliability
- **Not** a comparison of one model against another
- **Not** simply "a Grok evaluation" — the repository was *originally named* `grok-4.7-evaluation-benchmark` during early ideation, but the benchmark and evaluation engine are entirely **model-agnostic**. The one full recorded run used **Llama 3.2 3B via Ollama**, not Grok.
- 

---

## 3. Core Methodological Principle

The architecture is built around one deliberate separation of concerns: the benchmark defines *what* is tested, the model produces *a* response, and the evaluator independently decides *whether* that response satisfies the predefined criteria. These three responsibilities are never allowed to blur into one another.
Benchmark data
|
v
Model client
|
v
Model response
|
v
Evaluation engine
|
+--> exact match
+--> numerical comparison
+--> rule-based checks
+--> schema validation
+--> code execution
|
v
PASS / FAIL / ERROR
|
v
results.json
|
+--> metrics.py
|
+--> app.py (Streamlit)

**Why this separation matters:** if the benchmark, the model, and the evaluator are not kept independent, it becomes impossible to tell whether a failure reflects the *model's* limitation or the *evaluator's* limitation — which turned out to be the single most important lesson of this project (see [Section 11](#11-key-findings-from-the-recorded-run)).

---

## 4. Benchmark Design

The benchmark consists of **60 original test cases**, evenly divided across **six capability categories** (10 tests each):

| Category | Tests | Primary Capability |
|---|---|---|
| Reasoning | 10 | Logical deduction and multi-step reasoning |
| Coding | 10 | Executable Python generation and functional correctness |
| Mathematics | 10 | Numerical reasoning and calculation |
| Knowledge | 10 | Stable factual knowledge |
| Instruction Following | 10 | Following exact output constraints |
| Hallucination Resistance | 10 | Recognizing unsupported or missing information |

### 4.1 Reasoning
Tests logical deduction, relational constraints, and multi-step inference. Notably, `REASONING_006` (a box-labeling problem involving apples and oranges) checks multiple inferred conditions and allows **partial scoring** rather than a binary pass/fail.

### 4.2 Coding
Ten discrete Python function tasks: `is_even`, `reverse_string`, `sum_positive`, `char_frequency`, `second_largest`, `binary_search`, `sort_by_length`, `factorial`, `count_vowels`, `remove_duplicates`.

### 4.3 Mathematics
Covers arithmetic, percentages, ratios, linear equations, probability, geometry, mean, speed/distance/time, sequences, and markup/discount calculations.

### 4.4 Knowledge
Ten stable factual questions spanning chemistry, geography, computer science, biology, physics, history, algorithms, astronomy, and machine learning.

### 4.5 Instruction Following
Enforces hard output constraints: exactly three languages, YES/NO-only responses, exactly five words, exactly two bullet points, exact JSON keys, alphabetization, word-count-only output, raw JSON, single-sentence responses with required phrases and no colon, and exactly three lines.

### 4.6 Hallucination Resistance
Deliberately withholds required facts or presents ambiguous/unsupported premises. The *correct* behavior is for the model to acknowledge insufficient information rather than fabricate an answer — e.g., missing grades, missing founding dates, ambiguous identities, unsupported causal claims, an unspecified winner, an unspecified medical-study outcome.

### 4.7 Test Schema

Each test case follows a consistent structure:

```json
{
  "id": "REASONING_001",
  "category": "reasoning",
  "difficulty": "easy",
  "question": "...",
  "expected_answer": "...",
  "evaluation_type": "rule_based",
  "evaluation_criteria": "...",
  "capability_tested": "..."
}
```

Coding tests additionally carry an `evaluation_config` object specifying the required function name and its test cases (for execution-based grading).

---

## 5. Evaluation Methods

Rather than forcing every test through a single evaluation strategy, each test is graded by the method best suited to its response type:

| Method | Purpose | Known Weakness |
|---|---|---|
| **Exact match** | Short, fixed-format answers and strict output strings | Overly strict — fails on harmless punctuation/formatting differences |
| **Numerical comparison** | Compares numeric values, optionally with tolerance | Requires robust extraction if the model explains its reasoning before the final number |
| **Rule-based** | Checks explicit structural conditions (required phrases, line counts, bullet structure) | Can be brittle if rules are too narrowly specified |
| **Schema validation** | Parses structured JSON and verifies required/allowed keys | Fails if the model wraps JSON in explanatory text |
| **Code execution** | Runs generated Python against predefined test cases and evaluates *behavior*, not source similarity | Not securely sandboxed (`exec()`-based) |
| **Human evaluation** | Intended for subjective qualities (clarity, relevance, completeness) | Not the primary mechanism used in this project — noted as a future direction |

---

## 6. Repository Structure

grok-4.7-evaluation-benchmark/
│
├── data/
│ └── benchmark.json # Source of truth: all 60 test definitions
│
├── model_client.py # Gemini API integration (explored, not used in final run)
├── mock_model.py # Deterministic mock model for harness testing
├── ollama_model_client.py # Local model integration (Llama 3.2 3B via Ollama)
│
├── evaluator.py # Low-level evaluation functions (reasoning, numerical, code)
├── evaluation_engine.py # Central router — dispatches by evaluation_type
├── code_executor.py # Executes generated Python, returns namespace or error
│
├── run_test.py # Main orchestration script
├── test_api.py
├── test_ollama.py
├── test_ollama_client.py # Ad hoc test/dev utilities
│
├── metrics.py # Computes aggregate + category-level metrics
├── app.py # Streamlit dashboard
├── results.json # Recorded output of the frozen experiment
│
├── .gitignore
└── .env # Local config/secrets (not committed)


> Note: the repo name reflects the project's *original ideation direction*. The benchmark and evaluation engine themselves are model-agnostic — they were ultimately run against Llama 3.2 3B, not Grok.

---

## 7. File-by-File Explanation

### `data/benchmark.json`
The single source of truth for all 60 test definitions — questions, expected answers, evaluation types, and criteria. Kept entirely separate from implementation logic so the benchmark can be audited or reused independently of the code.

### `model_client.py`
Gemini API integration using the Google GenAI client, environment-variable-based configuration, and retry handling for transient server errors. Explored as an alternate model route during development; **not** the client used in the final recorded run.

### `ollama_model_client.py`
The local model integration actually used for the full run. Invokes Ollama via Python `subprocess`, targeting `llama3.2:3b`. Captures stdout, handles non-zero return codes, and enforces a 120-second timeout.

### `mock_model.py`
A deterministic stand-in model used to validate the evaluation pipeline **independently of any live model**. Mock results validate the harness's correctness — not any model's capability.

### `evaluator.py`
Contains the lower-level evaluation logic — reasoning checks, numerical comparison, and code-execution grading — used during development and by the central engine.

### `evaluation_engine.py`
The central dispatcher. Routes each test to the correct evaluator based on its declared `evaluation_type`: `rule_based`, `exact_match`, `numerical`, `code_execution`, or `schema_validation`.

### `code_executor.py`
Executes model-generated Python and returns either a populated namespace or an execution error. **Important caveat:** this uses Python's `exec()` directly and is *not* a secure sandbox — a known limitation, not a production-safe design.

### `run_test.py`
The main orchestration script. Loads `benchmark.json`, sends every test to the selected model client, passes each response through the evaluation engine, records a result entry, prints a run summary, and persists everything to `results.json`.

### `metrics.py`
Reads `results.json` and computes total test count, pass/fail/error counts, overall score, and per-category breakdowns. Treated as a development utility, **not** a final standardized scoring system.

### `app.py`
A Streamlit dashboard that loads `results.json`, excludes any record whose category is `development` from the benchmark view, and presents summary metrics, category-level performance, a full result table, and a per-test explorer (question / expected answer / model response / evaluation outcome).

### `results.json`
The recorded output of the one full experiment — every model response paired with its evaluation outcome and metadata.

### `.env` / `.gitignore`
Local configuration and secrets (never committed). `.gitignore` excludes `.env`, `venv/`, `__pycache__/`, and `results/` — though the root `results.json` was intentionally retained as the permanent record of the experiment.

---

## 8. Development / Regression Tests

Separate from the 60 benchmark tests, four development tests exist purely to validate the **evaluation machinery itself**:

| ID | Purpose |
|---|---|
| `TEST_CODE_001` | Validates code-execution evaluation |
| `TEST_EXACT_001` | Validates exact-match evaluation (expected pass) |
| `TEST_EXACT_002` | Intentionally wrong mock response — validates that failure is correctly detected |
| `TEST_NUM_001` | Validates numerical evaluation |

These are excluded from all benchmark-level scoring and dashboard views.

---

## 9. Execution Flow

python run_test.py
|
v
Load data/benchmark.json
|
v
Iterate through all 60 benchmark tests
|
v
Send question to Ollama (Llama 3.2 3B)
|
v
Model generates a response
|
v
evaluation_engine.py evaluates the response
|
v
Result classified: PASS / FAIL / ERROR
|
v
Response + score + metadata stored
|
v
results.json saved
|
+--> python metrics.py (aggregate scoring)
|
+--> streamlit run app.py (interactive dashboard)


---

## 10. Local Model Integration (Ollama)

The recorded full experiment ran entirely **locally** — no paid hosted API — using Llama 3.2 3B through Ollama:
OLLAMA
|
v
ollama run llama3.2:3b "<question>"
|
v
stdout
|
v
ask_ollama()
|
v
run_test.py


The local client handles successful output capture, subprocess errors, encoding issues, and request timeouts. In the original Windows environment, the Ollama executable path was resolved via the `LOCALAPPDATA` directory.

---

## 11. Key Findings From the Recorded Run

The full run — 60 benchmark tests + 4 development tests, against Llama 3.2 3B via Ollama — produced approximately **25 PASS, 34 FAIL, 1 ERROR**.

> ⚠️ These numbers describe **this one prototype run**, not a validated model score. Several failures were caused — or influenced — by evaluator strictness rather than genuine model incorrectness.

### 11.1 The Central Discovery: Model Correctness ≠ Evaluator Correctness

**Mathematics example** — naive float parsing failed on explained answers:
Model response: "The discount is 25% of 80 = 20. Therefore the final price is $60."
Expected value: 60

Naive float(answer.strip()) → FAIL
Underlying mathematics → CORRECT


Similar parsing failures occurred with `'$60'`, `'0.33'` embedded in explanation text, and `'300 km'`.

**Exact-match example** — semantically correct answers penalized for formatting:
Expected: Mitochondria
Model: Mitochondria.
Exact string comparison → FAIL
Semantic content → Correct


The same pattern appeared throughout the **hallucination-resistance** tests: multiple correct "Not enough information"-style responses were marked `FAIL` purely because of punctuation mismatches against the expected string.

### 11.2 Instruction-Following: Mixed Genuine and Evaluator-Sensitive Failures

- Genuine failures observed: returning C# instead of requested C++; returning explanatory text/code instead of raw JSON; including prose before a requested output-only list; explaining an answer instead of returning only a word count.
- The exact-three-lines task passed cleanly.
- At least one semantically correct response was scored as a failure, reinforcing that evaluator behavior must be inspected before attributing every failure to the model.

### 11.3 Hallucination Resistance: One Recorded Error

`HALLUCINATION_009` produced an `ERROR` (no model response was available) rather than a `PASS`/`FAIL`. The category overall confirmed that hallucination resistance is better evaluated **semantically**, not via brittle exact-string matching.

---

## 12. Why the Experiment Was Frozen

During development, it became clear that repeatedly amending evaluator logic **after** observing model outputs turns the benchmark into a moving target — making it impossible to cleanly separate genuine model measurement from post-hoc evaluator tuning.
Benchmark definition
|
v
Freeze questions + criteria
|
v
Run model
|
v
Observe results
|
v
Analyze evaluator validity separately


For this reason, the project was **deliberately stopped** at the prototype stage rather than iteratively "improved" to raise its apparent score. The repository is preserved as a documented experiment — any future work is a **new, versioned experiment**, not a retroactive edit of this one.

---

## 13. Limitations

- Only 60 tests — not statistically representative of general LLM capability
- Original, self-designed questions — not a validated standardized benchmark
- Only a single recorded local model run was performed
- Evaluator has known weaknesses: numerical extraction and punctuation-sensitive exact matching
- Some evaluation rules are brittle and produce false negatives
- `code_executor.py` uses `exec()` — not a secure sandbox
- No rigorous inter-rater human evaluation was conducted
- No confidence intervals, significance testing, or repeated-seed analysis
- Different task types are aggregated into a single overall score despite measuring distinct capabilities
- `metrics.py` and `app.py` handle development-category records slightly differently
- Results can vary with model version, prompt formatting, local inference configuration, and evaluator implementation
- Does **not** establish general model quality, safety, or real-world reliability

---

## 14. Lessons Learned

- Benchmark design is as much a software-engineering problem as a data-design problem
- A benchmark question is only useful if its expected behavior can be evaluated *reliably*
- Different task types genuinely require different evaluators — one-size-fits-all grading doesn't work
- Exact matching is simple but often too brittle for real model output
- Numerical evaluation requires robust answer extraction, not naive parsing
- Code generation is best evaluated through execution against test cases, not text similarity
- Instruction-following includes output-*format* compliance, not just semantic correctness
- Hallucination resistance requires judging whether a response is evidence-supported, not just string-matching it
- **The evaluator can fail even when the model succeeds**
- A moving evaluator invalidates cross-run comparisons
- Mock-model tests validate the harness — not the model
- Local inference via Ollama is a practical, cost-free path for this kind of experimentation
- Executing model-generated code requires real security consideration
- A benchmark score should never be presented as scientifically meaningful without adequate coverage and evaluator validation

---

## 15. Reproducibility

Create/activate the Python environment
Install required Python packages
Install Ollama locally
Pull the configured local model:
ollama pull llama3.2:3b
Ensure Ollama is accessible to the Python client
Place the benchmark dataset at:
data/benchmark.json
Run:
python run_test.py
Inspect:
results.json
Run:
python metrics.py
Launch:
streamlit run app.py


> The original run was performed on Windows with a local Ollama installation. Python version, Ollama install path, and package versions can all affect exact reproducibility.

---

## 16. Future Research Directions

- Freeze benchmark questions and publish versioned benchmark releases
- Build a more robust, pre-validated evaluator specification *before* comparing models
- Implement tolerant numerical answer extraction
- Use semantic/normalized comparison where punctuation shouldn't matter
- Apply structured JSON/schema validators consistently for structured-output tests
- Run generated code in isolated containers/subprocesses with resource limits, timeouts, and network restrictions
- Separate benchmark scoring from harness-health metrics
- Add repeated runs to measure variance
- Expand test count per capability; add adversarial and edge-case tests
- Introduce human evaluation for subjective tasks
- Version model, prompt, evaluator, dataset, and environment together
- Only compare multiple models *after* evaluator validity is established
- Report per-category results rather than relying on a single aggregate score
- Track evaluator false positives/negatives using known control responses

### Recommended Experimental Discipline (for any future version)

> The original run was performed on Windows with a local Ollama installation. Python version, Ollama install path, and package versions can all affect exact reproducibility.

---

## 16. Future Research Directions

- Freeze benchmark questions and publish versioned benchmark releases
- Build a more robust, pre-validated evaluator specification *before* comparing models
- Implement tolerant numerical answer extraction
- Use semantic/normalized comparison where punctuation shouldn't matter
- Apply structured JSON/schema validators consistently for structured-output tests
- Run generated code in isolated containers/subprocesses with resource limits, timeouts, and network restrictions
- Separate benchmark scoring from harness-health metrics
- Add repeated runs to measure variance
- Expand test count per capability; add adversarial and edge-case tests
- Introduce human evaluation for subjective tasks
- Version model, prompt, evaluator, dataset, and environment together
- Only compare multiple models *after* evaluator validity is established
- Report per-category results rather than relying on a single aggregate score
- Track evaluator false positives/negatives using known control responses

### Recommended Experimental Discipline (for any future version)

PHASE A — DESIGN
Define benchmark
Define expected behavior
Define evaluator
Create control responses

PHASE B — VALIDATE EVALUATOR
Correct response -> should PASS
Clearly wrong response -> should FAIL
Formatting variation -> decide explicitly
Edge cases -> test explicitly

PHASE C — FREEZE
Freeze benchmark version
Freeze evaluator version
Record environment

PHASE D — MEASURE
Run model
Store raw responses
Store evaluator outputs

PHASE E — ANALYZE
Separate model errors from evaluator errors
Report category-level results
Report limitations

PHASE F — COMPARE
Only compare models after the measurement system is stable


---

## 17. Quick Reference

| Item | Current State |
|---|---|
| Project type | Self-initiated AI/ML research & practice |
| Primary problem | Systematic LLM evaluation |
| Benchmark size | 60 tests |
| Categories | 6, with 10 tests each |
| Recorded model | Llama 3.2 3B |
| Inference | Local, via Ollama |
| Dataset | `data/benchmark.json` |
| Runner | `run_test.py` |
| Evaluation router | `evaluation_engine.py` |
| Code evaluator | `code_executor.py` + `evaluator.py` |
| Results | `results.json` |
| Metrics | `metrics.py` |
| Dashboard | `app.py` (Streamlit) |
| Development tests | 4 |
| Final status | **Frozen prototype** |

---

## 18. Final Takeaway

This project is best understood as a **hands-on study of how to build an LLM evaluation system**, not as a scorecard for any particular model.

- The **benchmark** answers: *what capabilities do I want to test?*
- The **model client** answers: *how do I obtain the model's response?*
- The **evaluator** answers: *how do I decide whether that response satisfies the requirement?*
- The **result pipeline** answers: *how do I store and analyze the experiment?*

The central methodological lesson carried forward from this project is simple but easy to overlook:

> **A model evaluation is only as trustworthy as the benchmark and evaluator used to produce it.**

Any future extension of this work should treat that principle as its starting point.
