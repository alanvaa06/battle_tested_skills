---
name: map-project-architecture
description: Map a Python or TypeScript repository into one evidence-backed HTML architecture page — import layers, contracts, storage, external connections, user flow and infra — written to docs/architecture/index.html and published as an Artifact. Every claim carries a file and line from scripts/inventory.py; a lens with no evidence says so instead of guessing. Use when the user says "map the architecture", "arquitectura del proyecto", "map-project-architecture", or wants an onboarding page for a codebase.
disable-model-invocation: true
---

# map-project-architecture

One invocation, one page. The page is built from `inventory.json`, never from
memory or the README. The README is read for names and for the user flow only.

## 0. Ground rules

- **Evidence or nothing.** Every row, card and diagram box comes from an item in
  `inventory.json` and shows its `file:line`. A lens with no items renders the
  empty-state block naming what was searched.
- **Never fill from general knowledge.** If the JSON does not say the project uses
  Postgres, the page does not say it either.
- **Fixed design.** Use `templates/architecture.html` as is. Replace only the
  `{{TOKENS}}` and the content between `<!-- LENS:x -->` markers.
- **Language** of the page: the language of the invoking message.
- **Translate every literal.** `fuente`, `No encontrado`, `Buscamos`, `implementas:`,
  the arrow labels, the layer captions and the footer are the Spanish defaults;
  when the page language is not Spanish translate all of them together.
  `templates/architecture.html`'s `aria-label="Contenido"` is the one non-token
  string you may also replace.
- **Write only** under `docs/architecture/` in the target repo.

## 1. Inventory

```bash
python "<skill-dir>/scripts/inventory.py" <repo-root> --out "<scratchpad>/inventory.json" --diff "<repo-root>/docs/architecture/inventory.json"
```

`<skill-dir>` is this file's directory. Run the inventory once per invocation,
before section 7 writes the new `inventory.json`; a second run afterwards would
diff against itself. Read the printed summary:

- `[!] N roots found` -> ask once which root to map, then rerun with that root, and point `--diff` at that root's `docs/architecture/inventory.json`.
- `[!] capped` -> say so in the footer.
- `[!] unresolved=N` -> list them in the footer, grouped by `unresolved[].kind`
  (py_parse_failure, py_other_top_package, ts_alias_import, json_parse_failure),
  with the file. What the script could not place must not be presented as absent.
- `[diff] ...` -> keep those lines; they go in the footer as "what changed".
- Script cannot run (no Python, crash) -> follow section 6 and mark the page
  "confianza reducida / reduced confidence" in the eyebrow.

Then Read `inventory.json` in full.

## 2. Names and flow (README pass)

Read `README.md` and the top level of `docs/` only to learn: what the project
calls its stages, who the user is, and the first runnable example. Do not take
architecture claims from them.

## 3. Main entrypoint

Take `entrypoints[0]` (already ranked: project.scripts / bin, README command,
routes, `__main__`, CLI framework, npm scripts, main guards). If the top two
share the same rank and differ in kind, ask once which one the page should draw.

## 4. Fill the seven blocks

Each block opens with `<h2>` (the same text as its `NAV_*` label) and one
`<p class="sub">` stating what the lens shows, then the content.

Each block goes between its markers. Every table whose items carry `evidence` has a `fuente` column with
`file:line` from `evidence[0]`. `evidence` is capped (20 per detector or env var, 3 per URL) while `count` is the
true total; when `count` > `len(evidence)`, render the count and label the list
"primeras N".

Empty state (Spanish shown; translate to the page language):

```html
<div class="note empty"><div class="t">No encontrado</div><p>Buscamos: <detector names or patterns>. Nada coincidio en <N> archivos de codigo.</p></div>
```

| Block | Source in JSON | What to draw or list |
|---|---|---|
| context | meta, storage, external, entrypoints, infra, mcp | SVG: repo box center with name and unit count; storage boxes left (one per detector kind); external boxes right (http clients, SDKs, MCP servers); entrypoints top; infra bottom (containers, CI, deploy). Every box shows its count. Arrows labeled "lee/escribe", "llama", "entra por", "corre en". Empty side -> a dashed box "nada detectado". |
| code | code.python / code.ts: units, import_graph, layers | SVG layers: one band per `layers.layers[i]`, bottom = layer 0, label each band only `Capa <i>` / `Layer <i>`, never a role name; units in the same band drawn side by side; NO per-edge lines (39 edges is unreadable): one arrow per band gap labeled "importan de", and inside each unit box a third line listing the units it imports from, taken from the edges (wrap to two lines if long); the per-edge detail lives in the units table; units that share a band and are not in a `cycles` entry have no import between them, name the ones that matter in the caption ("X, Y y Z no se importan entre si"); `cycles` drawn with a red pill and named. Then the units table: name, kind, files, lines, imports from (from edges), fuente = `<package_dir>/<name>/` (units carry no evidence entry; state the directory, not a line, and say so once above the table). If both stacks exist, two diagrams. (`code.ts` or `code.python` is `null` when a stack is absent) |
| contracts | code.*.contracts | One card per contract: name, kind, "implementas: <abstract_methods>", implementers with unit, fuente. |
| storage | storage, migrations | Table: detector, kind, stack, count, fuente. Migrations dirs as pills. |
| external | external, urls, env, mcp | Table of clients and SDKs; table of URL literals (host only in the name column, full URL in a code cell); env var names with first fuente (never values); MCP servers per config file, fuente = the config file path (no line). |
| flow | entrypoints, code layers, README example | SVG left-to-right: entrypoint -> the units it reaches (resolve the entrypoint to a unit: take `target` if it names a module, the part before `:`, else the unit whose name is the first path segment under `code.<stack>.package_dir` in `evidence[0].file`; if neither resolves, draw the entrypoint as a box that touches no unit and say so in the figcaption) -> outputs (storage kinds, file writes). Below, table of the other entrypoints: kind, name, target, fuente. |
| infra | infra | Cards: containers (base image), compose services, devcontainer, CI workflows (name, triggers, matrix), deploy configs, tests by dir, tools. |

Hero tokens: `PROJECT_NAME`, `VERSION`, `COMMIT` from meta; `TITLE` a one-line
statement of what the repo is, in the page language, built
only from `meta.name`, the README's first descriptive sentence (section 2) and
the top-layer unit names, no characterization the JSON or README does not
support; `LEDE` two sentences from
the README pass; `STAT_UNITS` = total units across stacks, `STAT_LINES` =
`meta.code_lines`,
`STAT_EXTERNAL` = `len(external)` + the total number of servers across all
`mcp[].servers`. `STAT_UNITS_LABEL`, `STAT_LINES_LABEL`, `STAT_EXTERNAL_LABEL`
name those three numbers ("unidades", "lineas de codigo", "conexiones externas"),
`NAV_LABEL` heads the nav ("Contenido"), and `NAV_CONTEXT` .. `NAV_INFRA` name the
seven sections, all in the page language.

`FOOTER`: "Generado desde inventory.json · commit <sha> · <date> · <files> archivos, <code_lines> lineas · lentes vacias: <list or 'ninguna'> · <diff lines or 'primera corrida'>" plus "capped" if set.

## 5. Diagrams

Inline SVG, `viewBox` sized to content, `currentColor` strokes, one
`<marker>` arrowhead, boxes filled with the lens token (`var(--code)`,
`var(--storage)`, `var(--external)`, `var(--flow)`, `var(--infra)`), 12-13px
labels, `<figure>` + `<figcaption>` stating the claim, `role="img"` +
`aria-label`. Grid: 20px gutters, boxes on shared baselines.

## 6. Fallback when the script cannot run

Run these by hand and build a reduced `inventory.json` with the same shape:

- units: `find src -name __init__.py` (Python) or `ls src` (TS);
- imports: `rg -n "^(from|import) <package>" <package_dir>` per unit;
- contracts: `rg -n "abstractmethod|\(ABC\)|Protocol\)|export interface|abstract class"`;
- storage / external: the recipes table below;
- entrypoints: `rg -n "project.scripts|\"bin\"|__main__|if __name__"`;
- infra: `ls Dockerfile* compose* .devcontainer .github/workflows`.

Recipes below. They are generated, not hand-written: to refresh them run the
command in the HTML comment and replace the table. If `rg` is unavailable, the
equivalent is `grep -rnE '<pattern>' --include='*.py'`.

<!-- run: python -c "import sys; sys.path.insert(0,'scripts'); from detectors import grep_recipes; print(grep_recipes())" and paste below -->

| lens | detector | kind | stack | grep |
|---|---|---|---|---|
| storage | sqlalchemy | sql | py | `rg -n '^(from|import) sqlalchemy' -g '*.py'` |
| storage | psycopg | sql | py | `rg -n '^(from|import) psycopg' -g '*.py'` |
| storage | asyncpg | sql | py | `rg -n '^(from|import) asyncpg' -g '*.py'` |
| storage | sqlite3 | sql | py | `rg -n '^(from|import) sqlite3' -g '*.py'` |
| storage | duckdb | sql | py | `rg -n '^(from|import) duckdb' -g '*.py'` |
| storage | pymongo | nosql | py | `rg -n '^(from|import) (pymongo|motor)' -g '*.py'` |
| storage | redis-py | cache | py | `rg -n '^(from|import) redis' -g '*.py'` |
| storage | supabase-py | baas | py | `rg -n '^(from|import) supabase' -g '*.py'` |
| storage | boto3 | object_store | py | `rg -n '^(from|import) boto3' -g '*.py'` |
| storage | parquet-csv-write | file_store | py | `rg -n 'to_parquet|write_table|to_csv|write_csv|to_excel' -g '*.py'` |
| storage | prisma | sql | ts | `rg -n '@prisma/client'` |
| storage | drizzle | sql | ts | `rg -n 'drizzle-orm'` |
| storage | pg | sql | ts | `rg -n "from ['\"]pg['\"]"` |
| storage | supabase-js | baas | ts | `rg -n '@supabase/'` |
| storage | mongoose | nosql | ts | `rg -n 'mongoose'` |
| storage | ioredis | cache | ts | `rg -n "ioredis|from ['\"]redis['\"]"` |
| external | requests | http_client | py | `rg -n '^(from|import) requests' -g '*.py'` |
| external | httpx | http_client | py | `rg -n '^(from|import) httpx' -g '*.py'` |
| external | aiohttp | http_client | py | `rg -n '^(from|import) aiohttp' -g '*.py'` |
| external | urllib-request | http_client | py | `rg -n 'urllib.request' -g '*.py'` |
| external | openai-py | sdk | py | `rg -n '^(from|import) openai' -g '*.py'` |
| external | anthropic-py | sdk | py | `rg -n '^(from|import) anthropic' -g '*.py'` |
| external | stripe-py | sdk | py | `rg -n '^(from|import) stripe' -g '*.py'` |
| external | slack-py | sdk | py | `rg -n '^(from|import) slack_sdk' -g '*.py'` |
| external | google-api-py | sdk | py | `rg -n 'googleapiclient|google.cloud|google.oauth2' -g '*.py'` |
| external | twilio-py | sdk | py | `rg -n '^(from|import) twilio' -g '*.py'` |
| external | axios | http_client | ts | `rg -n "from ['\"]axios"` |
| external | ky | http_client | ts | `rg -n "from ['\"]ky['\"]"` |
| external | node-fetch | http_client | ts | `rg -n 'node-fetch'` |
| external | fetch-url | http_client | ts | `rg -n "fetch\(\s*['\"\`]https?://"` |
| external | openai-js | sdk | ts | `rg -n "from ['\"]openai"` |
| external | anthropic-js | sdk | ts | `rg -n '@anthropic-ai/'` |
| external | stripe-js | sdk | ts | `rg -n "from ['\"]stripe"` |
| external | slack-js | sdk | ts | `rg -n '@slack/'` |
| external | googleapis-js | sdk | ts | `rg -n 'googleapis'` |
| external | resend-js | sdk | ts | `rg -n "from ['\"]resend"` |

## 7. Publish

1. Load the `artifact-design` skill (required before writing any artifact).
2. Write `<repo-root>/docs/architecture/index.html` and copy `inventory.json`
   next to it.
3. Publish. On a re-run, read `<repo-root>/docs/architecture/artifact.url` and
   pass its single line as `url` so the same Artifact updates; if the file is
   missing, use the Artifact tool's `action: "list"` and match on
   `PROJECT_NAME` before creating a new one. After a first publish, write the
   returned URL to `docs/architecture/artifact.url` (one line). Favicon on
   first publish: a single emoji chosen for the project. Title = `PROJECT_NAME`.
4. Report: the Artifact URL, the file path, the empty lenses, and the diff lines.
