# map-project-architecture — design

Date: 2026-09-03
Status: approved in conversation, pending written review

## Purpose

One slash command, `/map-project-architecture`, that maps a repository and produces one
HTML page with the code architecture, storage, external connections, user flow and infra,
every claim backed by a file and line. The page is written to `docs/architecture/index.html`
in the repo and published as an Artifact.

The page produced on 2026-09-03 for `S_Portfolio-Construction` is the reference output:
layered import diagram, package table, contracts, type chain, entities, helpers, errors,
tests. This skill generalizes it and adds the lenses that page lacked.

## Non-goals

- n8n workflow JSON as code. Separate skill if ever.
- Runtime tracing, profiling, or executing the project.
- Editing the project. The skill writes only under `docs/architecture/`.
- Prose architecture from README. README is read for names and the user flow only.

## Stacks

Python and TypeScript/Node in v1. Detection tables live in one module,
`scripts/detectors.py`, and are the single source of truth for both the script and the
manual grep fallback described in SKILL.md.

## Layout

```
~/.claude/skills/map-project-architecture/
  SKILL.md                      procedure, evidence rules, fallback recipes
  scripts/inventory.py          repo -> inventory.json, stdlib only, Python >= 3.10
  scripts/detectors.py          pattern tables per stack (the only place patterns live)
  templates/architecture.html   fixed design tokens + lens markers
  docs/                         this design, later the plan
```

Frontmatter: `disable-model-invocation: true`. Mirrored by hand into the SKILLS folder
like `scaffold`.

## The seven blocks (six lenses plus the context diagram)

Fixed. Each lens is one section, one detection recipe, and one "not found" block.

| Lens | Section answers | Empty-state text |
|---|---|---|
| context | system context: repo center, storage left, external right, entrypoints top, infra bottom | never empty |
| code | packages, import layers, contracts, type chain, error taxonomy, tests | never empty: a repo with code has packages |
| contracts | ABCs, Protocols, TS interfaces and abstract classes; who implements each | "No abstract classes, Protocols or exported interfaces found" |
| storage | databases, ORMs, migrations, caches, file stores, object storage | "Searched: <list of detector names>. Nothing matched." |
| external | HTTP clients with literal URLs, SDKs, MCP servers, env vars that name a host or key | same pattern |
| flow | main entrypoint drawn as a flow; the rest listed | "No entrypoint found (no scripts, main, routes, bin)" |
| infra | Docker, compose, devcontainer, CI workflows with triggers and matrix, deploy configs, lint/type tools | same pattern |

Rule: a lens with no evidence renders its empty-state block naming what was searched. The
model never fills a lens from general knowledge or from the README.

## inventory.py

Input: repo root. Output: `inventory.json` to a path given by `--out`. Stdout is
ASCII-only (Windows cp1252 rule).

Skips: `.git`, `.venv`, `venv`, `node_modules`, `dist`, `build`, `__pycache__`,
`.next`, `.turbo`, `coverage`, anything in `.gitignore` when `git` is available.

Every item carries `evidence: [{"file": str, "line": int}]`.

Blocks:

- `meta`: name and version (pyproject, package.json), languages by file count, commit
  SHA, total files and lines, roots found (more than one `pyproject.toml` or
  `package.json` not nested under another = monorepo).
- `packages`: Python: directories with `__init__.py` under the first source root
  (`src/<ns>/...` or top-level). TS: directories under `src/`, `app/`, `lib/`,
  `packages/*`. Per package: files, lines.
- `import_graph`: Python via `ast`, internal imports only, aggregated package to
  package with counts. TS via regex over `import ... from '...'` and `require('...')`
  for relative specifiers; `tsconfig` `paths` is out of scope for v1 and recorded in
  `unresolved` when present.
- `contracts`: Python classes inheriting `ABC` or with `@abstractmethod`, and
  `Protocol` subclasses, with abstract method names and known implementers found by
  base-class name. TS `export interface` and `export abstract class` with members.
- `storage`, `external`: matches from the detector tables, one record per distinct
  (detector, file) pair, plus URL literals found next to HTTP client calls and env var
  names read via `os.environ`, `os.getenv`, `process.env`.
- `entrypoints`: ranked list with kind and evidence. Kinds: `project.scripts`, `bin`,
  `__main__`, `main_guard`, `cli_framework` (click, typer, argparse), `http_route`
  (FastAPI, Flask, Express, Next app/pages), `examples_dir`, `notebooks`.
- `infra`: files found with parsed summaries: workflow name, triggers, matrix;
  compose services; Dockerfile base image; devcontainer present; test directories with
  file counts; lint and type tools named in pyproject or package.json.
- `unresolved`: detected but ambiguous items, so the page can say what it could not
  place.

Runtime target: under 30 seconds on a 5k-file repo.

## SKILL.md procedure

1. Run `python scripts/inventory.py <root> --out <scratchpad>/inventory.json`. If Python
   is missing or the script fails, follow the grep recipes in SKILL.md (generated from
   the same detector table) and mark the page "reduced confidence".
2. If `meta.roots` has more than one entry, ask once which root to map.
3. Read README and `docs/` top level for names and for the user flow. Not for
   architecture claims.
4. Pick the main entrypoint by rank: `project.scripts` or `bin` first, then the first
   runnable example in the README, then `main_guard`. Tie: ask once.
5. Fill each lens from the JSON. Empty lens: empty-state block.
6. Draw three SVG diagrams:
   - layers: topological order of the package import graph, one band per layer,
     arrows read "imports from", packages that share a layer and have no edge between
     them are drawn side by side with no connector;
   - system context: the repo in the center, storage left, external right, users and
     entrypoints top, infra bottom, every box carrying its evidence count;
   - user flow: the main entrypoint through the stages the code shows.
7. Load the `artifact-design` skill, fill `templates/architecture.html`, write
   `docs/architecture/index.html` and `docs/architecture/inventory.json`, publish the
   Artifact.
8. Footer: commit SHA, date, counts, list of lenses that came back empty and what was
   searched.
9. Re-run: when `docs/architecture/inventory.json` already exists, print a diff summary
   (packages added or removed, external connections added or removed, entrypoints
   changed) before overwriting.

Language of the page: the language of the invoking message.

## Template

Fixed design, no per-run design decisions: IBM Plex Serif / Sans / Mono, cool paper
ground, one tint per lens, sticky left nav, light and dark tokens. Hero shows three
numbers: packages, lines, external connections. Every table has a `fuente` column with
`path:line`. Lens markers are HTML comments (`<!-- LENS:storage -->` ...
`<!-- /LENS:storage -->`) that the model replaces.

## Error handling

- Monorepo: ask which root; do not merge roots.
- Huge repo: cap at 20k files, report the cap in the footer.
- TS `tsconfig` paths: recorded as unresolved, not guessed.
- Detector false positives (a string that looks like a URL in a test fixture): the
  evidence column makes them visible; the page does not filter them.

## Acceptance

Run on three repos: `S_Portfolio-Construction` (Python library), one Next + Supabase
repo, one mixed. Pass when:

- no section contains a claim without a `path:line` source;
- every empty lens shows its empty-state block naming the detectors searched;
- inventory finishes under 30 seconds;
- the Python page matches the 2026-09-03 reference page on the code lens: same
  layers, same "no edge between stages" finding, same contract list.

2026-09-04: scripts reviewed in four rounds (walk cycles, detector anchors, real
package selection, TS members, quoted TOML keys, BOM, evidence lines); 103 tests.

2026-09-04: acceptance on S_Portfolio-Construction passed with the final scripts
(commit afa6951): 16 units, selection/sizing/timing in one layer with no edge between
them and no cycles, six contracts, 14 SizingInterface implementers, top entrypoint the
quoted [project.scripts] key, 0 unresolved, 0.57 s. 109 tests. Next + Supabase and
mixed repos still pending.
