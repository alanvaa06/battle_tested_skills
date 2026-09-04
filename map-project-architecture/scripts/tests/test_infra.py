"""infra: docker, compose, devcontainer, CI, deploy configs, tests, tools."""
from __future__ import annotations

from pathlib import Path

from infra import infra
from scanner import scan


def test_python_repo_infra(py_repo: Path) -> None:
    files, _ = scan(py_repo, max_files=1000)
    i = infra(files)
    assert i["dockerfiles"] == [{"file": "Dockerfile", "base_image": "python:3.12-slim"}]
    assert i["compose"] == []
    assert i["devcontainer"] is False
    assert i["workflows"] == [{
        "file": ".github/workflows/ci.yml", "name": "CI",
        "triggers": ["push", "pull_request"], "matrix": ['python-version: ["3.12", "3.13"]'],
    }]
    assert i["deploy"] == []
    assert i["tests"] == {"dirs": {"tests": 1}, "loose_files": 0}
    assert i["tools"] == ["ruff"]


def test_ts_repo_infra(ts_repo: Path) -> None:
    files, _ = scan(ts_repo, max_files=1000)
    i = infra(files)
    assert i["deploy"] == ["vercel.json"]
    assert i["tools"] == ["typescript", "vitest"]
    assert i["tests"] == {"dirs": {}, "loose_files": 0}


def test_compose_services_and_inline_triggers(tmp_path: Path) -> None:
    (tmp_path / "compose.yaml").write_text("services:\n  web:\n    image: x\n  db:\n    image: y\nvolumes:\n  data:\n", encoding="utf-8")
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "deploy.yml").write_text("name: Deploy\non: [push, workflow_dispatch]\njobs: {}\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    i = infra(files)
    assert i["compose"] == [{"file": "compose.yaml", "services": ["web", "db"]}]
    assert i["workflows"][0]["triggers"] == ["push", "workflow_dispatch"]


def test_compose_learns_its_indent_from_the_file(tmp_path: Path) -> None:
    (tmp_path / "compose.yml").write_text(
        "version: '3'\n"
        "services:   # the stack\n"
        "    web:\n"
        "        image: x\n"
        "    db:\n"
        "        image: y\n"
        "volumes:\n"
        "    data:\n",
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["compose"] == [{"file": "compose.yml", "services": ["web", "db"]}]


def test_matrix_reports_the_declaration_not_its_consumers(tmp_path: Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "name: CI\n"
        "on: [push]\n"
        "jobs:\n"
        "  t:\n"
        "    strategy:\n"
        "      matrix:\n"
        '        python-version: ["3.12", "3.13"]  # note\n'
        "    steps:\n"
        "      - uses: actions/setup-python@v5\n"
        "        with:\n"
        '          python-version: "${{ matrix.python-version }}"\n',
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["workflows"][0]["matrix"] == ['python-version: ["3.12", "3.13"]']


def test_test_dirs_are_found_at_any_depth(tmp_path: Path) -> None:
    d = tmp_path / "packages" / "api" / "tests"
    d.mkdir(parents=True)
    (d / "test_x.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["tests"] == {"dirs": {"tests": 1}, "loose_files": 0}


def test_a_multi_stage_dockerfile_reports_its_last_base_image(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text(
        "FROM node:22 AS build\n"
        "RUN npm ci\n"
        "FROM gcr.io/distroless/nodejs22\n"
        "COPY --from=build /app /app\n",
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["dockerfiles"] == [
        {"file": "Dockerfile", "base_image": "gcr.io/distroless/nodejs22"}
    ]


def test_a_dockerfile_resolves_a_stage_alias_used_as_the_final_from(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.12 AS builder\n"
        "RUN pip install .\n"
        "FROM builder AS final\n"
        "CMD [\"run\"]\n",
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["dockerfiles"] == [
        {"file": "Dockerfile", "base_image": "python:3.12"}
    ]


def test_a_dockerfile_final_from_that_is_not_an_alias_is_reported_as_is(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text(
        "FROM node:20 AS builder\n"
        "RUN npm ci\n"
        "FROM python:3.12-slim\n"
        "COPY --from=builder /app /app\n",
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["dockerfiles"] == [
        {"file": "Dockerfile", "base_image": "python:3.12-slim"}
    ]


def test_workflow_triggers_learn_their_indent(tmp_path: Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "name: CI\n"
        "on:\n"
        "    push:\n"
        "        branches: [main]\n"
        "    pull_request:\n"
        "jobs: {}\n",
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["workflows"][0]["triggers"] == ["push", "pull_request"]


def test_compose_ignores_a_comment_when_learning_its_indent(tmp_path: Path) -> None:
    (tmp_path / "compose.yml").write_text(
        "services:\n"
        "      # the web tier comes first\n"
        "  web:\n"
        "    image: x\n"
        "  db:\n"
        "    image: y\n",
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert infra(files)["compose"] == [{"file": "compose.yml", "services": ["web", "db"]}]


def test_infra_lists_are_sorted_by_file(tmp_path: Path) -> None:
    (tmp_path / "b").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / "b" / "Dockerfile").write_text("FROM alpine\n", encoding="utf-8")
    (tmp_path / "a" / "Dockerfile").write_text("FROM debian\n", encoding="utf-8")
    (tmp_path / "b" / "compose.yml").write_text("services:\n  w:\n", encoding="utf-8")
    (tmp_path / "a" / "compose.yml").write_text("services:\n  v:\n", encoding="utf-8")
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "z.yml").write_text("name: Z\non: [push]\n", encoding="utf-8")
    (wf / "a.yml").write_text("name: A\non: [push]\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=20)
    i = infra(files)
    assert [d["file"] for d in i["dockerfiles"]] == ["a/Dockerfile", "b/Dockerfile"]
    assert [c["file"] for c in i["compose"]] == ["a/compose.yml", "b/compose.yml"]
    assert [w["file"] for w in i["workflows"]] == [
        ".github/workflows/a.yml", ".github/workflows/z.yml",
    ]
