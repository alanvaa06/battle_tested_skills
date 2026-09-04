---
name: python-standards
description: Robust Python coding standards — enums, dataclasses, Protocols, dependency injection, composition, type annotations, pytest/hypothesis/mutation testing. Use whenever writing, refactoring, or reviewing ANY Python code — modules, scripts, agents, CLI tools, tests, or Python embedded in a larger task — even if the user doesn't mention standards, typing, or best practices.
---

# Robust Python: Defining Your Own Types

Operating rules for all Python code. Where a rule can be checked mechanically, its section ends with a **Verification** — how to prove it held.

## Enums
- Use `enum.Enum` and `enum.auto()`. No magic numbers or raw strings for categories.
- Style: `class MyEnum(Enum):` with UPPERCASE member names.

## Data classes
- Use `@dataclass`. Prefer `frozen=True` for immutability.
- Type-hint all fields. Use `field(default_factory=...)` for mutable defaults (never mutable default literals).

## Classes
- Enforce invariants: the class keeps its data in a valid state.
- **Verification**: Test that violates an invariant fails (class prevents it or raises).

## Protocols and interfaces
- Use `typing.Protocol` for structural subtyping. Avoid deep inheritance.
- Use `@runtime_checkable` only when you need `isinstance` checks.
- A class can satisfy a Protocol without inheriting from it (duck typing with safety).

## Dependency injection
- Pass dependencies (objects/services) into functions or constructors; do not instantiate them inside the consumer.
- Use type hints to declare the interface of the injected dependency.

## Composition
- Prefer "Has-A" over "Is-A". Build complex behavior by combining small, focused objects.
- Avoid god objects; delegate responsibilities to composed parts.

## Static analysis
- Use a linter and formatter (e.g. `ruff` for both; `pylint`/`flake8` + `black` are fine if the project already uses them). Automate; don't rely on manual style review.
- **Verification**: Run the linter on complex code and refactor until it passes.

## Testing (pytest)
- Use pytest. Write unit tests. Arrange-Act-Assert. Use fixtures for setup.
- Test behavior and properties, not only single data points.
- **Verification**: Run `pytest`; all tests pass and failures have clear messages.

## Property-based testing (hypothesis)
- Use Hypothesis. Define strategies (e.g. `st.integers()`, `st.lists()`) for generated data.
- Aim to find edge cases (e.g. division by zero, empty lists) that examples miss.
- **Verification**: Run a hypothesis test that exposes a bug (e.g. wrong handling of zero or empty input).

## Mutation testing
- Use mutmut or similar. Reason about mutant survival.
- Focus: testing the tests — the suite should detect logic changes.
- **Verification**: Introduce a small bug (mutate code); the test suite must fail.

## Type annotations (PEP 484)
- **Mandatory**: type hints on function arguments and return values.
  - `def greet(name: str) -> str:`
- Annotate variables only when inference is ambiguous. Annotations = machine-verified docs.
- **Verification**: Run `mypy`; fix any type mismatch errors.

## Constraining types
- Use `T | None` and `A | B` (PEP 604, Python 3.10+); `Optional`/`Union` only on older interpreters. Use `Literal` where needed. Use `Any` sparingly.
- Explicitly handle `None`: unwrap or check before use. Avoid `Any`; it weakens type checking.
- **Verification**: Every `| None` value is checked or unwrapped before use.

## Collections
- Annotate inner types: `list[int]`, `dict[str, int]`. Never raw `list`/`dict` in annotations.
- Prefer abstract types for parameters: `Iterable` or `Sequence` for read-only inputs.

## Type checker config
- Configure `mypy.ini` or `pyproject.toml` (e.g. `--disallow-untyped-defs`, `--no-implicit-optional`).
- **Verification**: Changing a strictness flag should change mypy output as expected.
