# Certify Backend

This is the backend for the Certify project, built with FastAPI and MongoDB.

## Prerequisites

-   Python 3.10+
-   pip
-   MongoDB (local or remote)

## Setup

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
2. Create a `.env` file with your MongoDB URI:
    ```env
    MONGODB_URI=mongodb://localhost:27017
    PORT=8000
    ```
3. Start the development server:
    ```sh
    uvicorn src.main:app --reload --port 8000
    ```
4. The API will be available at `http://localhost:8000` by default.

## Deploying to Vercel

-   See `vercel.json` for configuration. The entry point is `main.py`.

## For Developers

### Setup for Development

1. Install development dependencies:

```sh
pip install -r requirements-dev.txt
```

2. Install Lefthook and set up Git hooks:

```sh
lefthook install
```

### Git Hooks with Lefthook

We use Lefthook for consistent linting, type checking, and testing before commits:

-   **Pre-commit** runs:

    -   `ruff` for linting
    -   `mypy` for type checks
    -   `pytest` to run tests

-   **Commit-msg** ensures conventional commit messages:

    ```
    feat:, fix:, docs:, style:, refactor:, test:, chore:
    ```

    Supports formats like:

    ```
    feat(some-feature):
    feat(some/other-feature):
    ```

To manually run hooks:

```sh
# Run pre-commit hooks
lefthook run pre-commit

# Run commit-msg hook against a commit message
lefthook run commit-msg "feat: example message"
```

### Writing Tests

-   All utilities and business logic functions should have corresponding tests in the `tests/` folder.
-   Example: for `generate_credential_id`, we have:

```python
from utils.common_utils import generate_credential_id

def test_generate_credential_id():
    cred_id = generate_credential_id()
    assert isinstance(cred_id, str)
    assert len(cred_id) > 0
    assert cred_id[0].islower()
```

-   Run tests with:

```sh
pytest -v
```

-   Ensure new functions have proper test cases before merging.

### Coding Guidelines

-   Use 4 spaces for Python indentation.
-   Keep line length ≤ 88 characters (matches `ruff` configuration).
-   Follow `.editorconfig` for consistent formatting across editors.
-   Re-run hooks before committing to avoid failures.
