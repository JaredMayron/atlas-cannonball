# Python Quality Standards

## Linting & Formatting
- All Python code modifications must be linted and formatted using `ruff` before the task is considered complete.
- Use the @lint workflow to automate these checks.
- Target both GCP/src and GCP/tests.

## Testing Architecture
- **Pattern**: Follow the **Arrange, Act, Assert (AAA)** pattern for all tests.
  - **Arrange**: Set up the environment, mocks, and data.
  - **Act**: Execute the specific function or method being tested.
  - **Assert**: Verify the outcome.
- **Style**: Prefer plain `pytest` functions over `unittest.TestCase` classes.
- **Exceptions**: Use `with pytest.raises()` for negative test cases.
