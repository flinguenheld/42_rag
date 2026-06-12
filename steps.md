Here’s a **clear, step-by-step breakdown** of what you need to do for your **"RAG against the machine"** project, organized by priority and dependencies.

---

---

## **📌 Project Overview**
**Goal**: Build a **Retrieval-Augmented Generation (RAG)** system that can answer questions about a codebase (the `vLLM` repository).
**Core Tasks**:
1. **Ingest** the `vLLM` repository and create a searchable knowledge base.
2. **Retrieve** relevant code snippets/documentation for questions.
3. **Generate** answers using the `Qwen/Qwen3-0.6B` model + retrieved context.
4. **Evaluate** retrieval quality using `recall@k` metrics.
5. **Provide a CLI** for all operations.

**Performance Requirements**:
- **Recall@5**: ≥80% on docs, ≥50% on code.
- **Indexing time**: ≤5 minutes.
- **Cold start latency**: ≤60 seconds.
- **Warm retrieval throughput**: ≤90 seconds for 1000 questions.

---

---

## **🚀 Step-by-Step Plan**

---

### **🔹 Phase 1: Setup & Preparation**
**Objective**: Set up the environment and understand the requirements.

1. **Read the Project Document**
   - Focus on **Chapter V (Mandatory Part)** and **Chapter VI (Evaluation)**.
   - Note the **data models** (Pydantic classes) in **V.7** and **output formats** in **V.9**.

2. **Set Up the Project Structure**
   - Create a Git repository with:
     ```
     your_project/
     ├── src/                # Your Python code
     ├── pyproject.toml      # Dependencies (use `uv`)
     ├── uv.lock             # Lock file for `uv`
     ├── README.md           # Documentation (see Chapter VII)
     ├── Makefile            # Automation (see III.2)
     └── .gitignore          # Exclude artifacts
     ```
   - Use **`uv`** as the package manager (mandatory).

3. **Install Dependencies**
   - Required libraries:
     - `transformers`, `torch`, `sentence-transformers` (for embeddings if using semantic search).
     - `rank-bm25` or `scikit-learn` (for TF-IDF/BM25).
     - `pydantic`, `fire`, `tqdm`, `uuid`.
     - `qwen3-0.6b` (or another compatible model).
   - Example `pyproject.toml`:
     ```toml
     [project]
     name = "rag_project"
     version = "0.1.0"
     dependencies = [
         "pydantic>=2.0",
         "fire>=0.5.0",
         "tqdm>=4.64.0",
         "rank-bm25>=0.2.2",
         "transformers>=4.30.0",
         "torch>=2.0.0",
         "scikit-learn>=1.2.0",
     ]
     ```

4. **Download the vLLM Repository**
   - The repository is provided as an attachment (`v1lm-0.10.1.zip`).
   - Extract it into `data/raw/vllm/`.

---

---

### **🔹 Phase 2: Implement Core Components**
**Objective**: Build the RAG pipeline step by step.

---

#### **1️⃣ Knowledge Base Ingestion System (V.2.1)**
**Goal**: Process the `vLLM` repository into searchable chunks.

- **Tasks**:
  - **Read all files** (Python code, Markdown docs) from `data/raw/vllm/`.
  - **Implement chunking**:
    - **Python code**: Split by functions/classes (max 2000 chars, configurable via CLI).
    - **Text/Markdown**: Split by paragraphs/sections.
    - Store chunks with metadata: `file_path`, `start_char_index`, `end_char_index`.
  - **Indexing**:
    - Use **TF-IDF** or **BM25** (mandatory) to create a searchable index.
    - Save the index (e.g., `data/processed/bm25_index/`).
    - Save chunks (e.g., `data/processed/chunks/`).

- **CLI Command**:
  ```bash
  uv run python -m src.main index --max_chunk_size 2000
  ```

- **Files to Create**:
  - `src/ingestion.py`: Chunking + indexing logic.
  - `src/models.py`: Pydantic models (e.g., `MinimalSource`, `UnansweredQuestion`).

---

#### **2️⃣ Retrieval System (V.2.2)**
**Goal**: Retrieve relevant chunks for a query.

- **Tasks**:
  - Implement **semantic search** (TF-IDF/BM25) over the indexed chunks.
  - For a query, return **top-k** chunks with:
    - `file_path`
    - `first_character_index`
    - `last_character_index`
  - Support **batch processing** (for datasets).

- **CLI Commands**:
  ```bash
  # Single query
  uv run python -m src.main search "How to configure OpenAI server?" --k 10

  # Batch processing (dataset)
  uv run python -m src.main search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 \
    --save_directory data/output/search_results
  ```

- **Files to Create**:
  - `src/retrieval.py`: Retrieval logic (TF-IDF/BM25).
  - `src/cli.py`: CLI commands (using `fire`).

---

#### **3️⃣ Answer Generation System (V.2.3)**
**Goal**: Generate answers using `Qwen/Qwen3-0.6B` + retrieved context.

- **Tasks**:
  - Load the `Qwen/Qwen3-0.6B` model (or another compatible model).
  - For each query:
    1. Retrieve top-k chunks.
    2. Pass chunks as context to the LLM.
    3. Generate an answer in **natural language**.
    4. Output structured JSON (see **V.9**).
  - Ensure answers are:
    - **Self-contained** (readable without the question).
    - **Source-grounded** (cite sources).
    - **Faithful** (no hallucinations).
    - **Relevant** (directly answer the question).

- **CLI Commands**:
  ```bash
  # Single query
  uv run python -m src.main answer "How to configure OpenAI server?" --k 10

  # Batch processing (dataset)
  uv run python -m src.main answer_dataset \
    --student_search_results_path data/output/search_results/dataset_docs_public.json \
    --save_directory data/output/answers
  ```

- **Files to Create**:
  - `src/generation.py`: LLM interaction logic.
  - Update `src/cli.py` with `answer` and `answer_dataset` commands.

---

#### **4️⃣ Evaluation System (V.2.4)**
**Goal**: Measure retrieval quality using `recall@k`.

- **Tasks**:
  - Implement `recall@k` metric (see **VI.1.1**):
    - A source is "found" if ≥5% overlap with a correct source.
    - For each question: `recall = (number_found / total_correct_sources)`.
  - Compare retrieved sources against ground truth (from `dataset_*.json`).
  - Output metrics: `Recall@1`, `Recall@3`, `Recall@5`, `Recall@10`.

- **CLI Command**:
  ```bash
  uv run python -m src.main evaluate \
    --student_answer_path data/output/search_results/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json \
    --k 10
  ```

- **Files to Create**:
  - `src/evaluation.py`: Recall@k logic.

---

#### **5️⃣ Command-Line Interface (V.2.5)**
**Goal**: Provide a CLI for all operations (using `fire`).

- **Mandatory Commands**:
  | Command               | Description                                                                 |
  |-----------------------|-----------------------------------------------------------------------------|
  | `index`               | Index the repository.                                                      |
  | `search`              | Search for a single query.                                                 |
  | `search_dataset`      | Process multiple questions from a JSON dataset.                          |
  | `answer`              | Answer a single query with context.                                       |
  | `answer_dataset`      | Generate answers from search results.                                     |
  | `evaluate`            | Evaluate search results against ground truth.                            |

- **Example CLI Structure**:
  ```python
  # src/cli.py
  import fire
  from src.ingestion import index_repository
  from src.retrieval import search_query, search_dataset
  from src.generation import answer_query, answer_dataset
  from src.evaluation import evaluate_results

  class RAGCLI:
      def index(self, max_chunk_size: int = 2000):
          """Index the vLLM repository."""
          index_repository(max_chunk_size)

      def search(self, query: str, k: int = 10):
          """Search for a single query."""
          return search_query(query, k)

      def search_dataset(self, dataset_path: str, k: int = 10, save_directory: str = "data/output"):
          """Process a dataset of questions."""
          return search_dataset(dataset_path, k, save_directory)

      def answer(self, query: str, k: int = 10):
          """Answer a single query."""
          return answer_query(query, k)

      def answer_dataset(self, search_results_path: str, save_directory: str = "data/output"):
          """Answer a dataset of questions."""
          return answer_dataset(search_results_path, save_directory)

      def evaluate(self, student_answer_path: str, dataset_path: str, k: int = 10):
          """Evaluate search results."""
          return evaluate_results(student_answer_path, dataset_path, k)

  if __name__ == "__main__":
      fire.Fire(RAGCLI)
  ```

---

---

### **🔹 Phase 3: Testing & Validation**
**Objective**: Ensure your system meets the requirements.

1. **Test Indexing**
   - Run `index` and verify:
     - Index is saved in `data/processed/`.
     - Chunks are correctly split (max 2000 chars).

2. **Test Retrieval**
   - Run `search` with a sample query (e.g., `"How to configure OpenAI server?"`).
   - Verify:
     - Top-k results are relevant.
     - Output includes `file_path`, `start_char_index`, `end_char_index`.

3. **Test Answer Generation**
   - Run `answer` with a sample query.
   - Verify:
     - Answer is **self-contained**, **source-grounded**, and **relevant**.
     - Output JSON matches the required format.

4. **Test Evaluation**
   - Run `evaluate` with a dataset.
   - Verify:
     - Recall@k scores are ≥80% (docs) and ≥50% (code).
     - Output includes metrics for `k=1,3,5,10`.

5. **Test Performance**
   - **Indexing time**: ≤5 minutes.
   - **Cold start latency**: ≤60 seconds (first retrieval after startup).
   - **Warm retrieval throughput**: ≤90 seconds for 1000 questions.

---

---

### **🔹 Phase 4: Documentation & Submission**
**Objective**: Document your work and submit.

1. **Write the README.md** (Chapter VII)
   - **Mandatory Sections**:
     - Description (goal + overview).
     - Instructions (how to run).
     - Resources (documentation, AI usage).
     - System architecture (RAG pipeline components).
     - Chunking strategy.
     - Retrieval method (TF-IDF/BM25).
     - Performance analysis (recall@k scores).
     - Design decisions (key choices).
     - Challenges faced + solutions.
     - Example usage (CLI commands).

2. **Add a Makefile** (III.2)
   - Example:
     ```makefile
     install:
         uv sync

     run:
         uv run python -m src.main

     debug:
         uv run python -m pdb -m src.main

     clean:
         rm -rf __pycache__ .mypy_cache data/processed/

     lint:
         flake8 src/
         mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
     ```

3. **Final Checks**
   - Run `lint` to ensure code quality (flake8 + mypy).
   - Verify all CLI commands work.
   - Ensure no large files (e.g., model weights) are committed.

4. **Submit**
   - Push to your Git repository.
   - Ensure the repo contains:
     - `src/`
     - `pyproject.toml` + `uv.lock`
     - `README.md`
     - `Makefile`
     - `.gitignore`

---

---
---
## **📅 Suggested Timeline**
| Phase               | Time Estimate | Priority |
|---------------------|---------------|----------|
| Setup & Preparation | 1-2 days      | ⭐⭐⭐⭐⭐ |
| Ingestion System    | 2-3 days      | ⭐⭐⭐⭐⭐ |
| Retrieval System    | 2-3 days      | ⭐⭐⭐⭐⭐ |
| Answer Generation   | 2-3 days      | ⭐⭐⭐⭐⭐ |
| Evaluation System   | 1-2 days      | ⭐⭐⭐⭐  |
| CLI & Testing       | 1-2 days      | ⭐⭐⭐⭐  |
| Documentation       | 1 day         | ⭐⭐⭐    |

---
---
## **💡 Tips & Pitfalls**
- **Start Simple**: Begin with **TF-IDF** or **BM25** for retrieval. Optimize later.
- **Chunking**: For Python code, split by **functions/classes** (not just by characters).
- **LLM Context**: Limit the context window to avoid exceeding token limits.
- **Error Handling**: Use `try-except` blocks for file I/O, model loading, etc.
- **Progress Bars**: Use `tqdm` for long-running operations (e.g., indexing).
- **Testing**: Test with small subsets of the `vLLM` repo first.
- **AI Usage**: Use AI for **code snippets** or **debugging**, but **understand everything** you submit.

---
---
## **❓ Next Steps for You**
1. **Do you want me to**:
   - Generate a **starter template** for any of the files (e.g., `ingestion.py`, `cli.py`)?
   - Explain a specific part in more detail (e.g., chunking strategy, recall@k calculation)?
   - Help design the **Pydantic models** or **CLI structure**?
2. **Or do you want to start coding and ask questions as you go?**
