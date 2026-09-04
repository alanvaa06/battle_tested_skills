"""detectors: the pattern tables and the per-line matcher."""
from __future__ import annotations

import re

from detectors import ALL_DETECTORS, ENV_READ, URL_LITERAL, grep_recipes, match_line


def test_sqlalchemy_matches_python_import() -> None:
    names = [d.name for d in match_line("import sqlalchemy", "py")]
    assert names == ["sqlalchemy"]


def test_python_detector_does_not_fire_on_ts_stack() -> None:
    assert match_line("import sqlalchemy", "ts") == []


def test_supabase_js_matches_scoped_import() -> None:
    line = "import { createClient } from '@supabase/supabase-js';"
    assert [d.name for d in match_line(line, "ts")] == ["supabase-js"]


def test_fetch_url_matches_literal_url_only() -> None:
    assert [d.name for d in match_line('fetch("https://x.io")', "ts")] == ["fetch-url"]
    assert match_line("fetch(url)", "ts") == []


def test_env_read_patterns_capture_name() -> None:
    py = re.search(ENV_READ["py"], 'token = os.environ["API_KEY"]')
    assert py is not None and "API_KEY" in py.groups()
    ts = re.search(ENV_READ["ts"], "process.env.SUPABASE_URL ?? ''")
    assert ts is not None and "SUPABASE_URL" in ts.groups()


def test_url_literal_stops_at_quote_or_paren() -> None:
    assert URL_LITERAL.findall('x = "https://api.example.com/v1"') == ["https://api.example.com/v1"]
    assert URL_LITERAL.findall('f("https://a.com/x")') == ["https://a.com/x"]


def test_url_literal_stops_before_template_interpolation() -> None:
    assert URL_LITERAL.findall('`https://a/${id}/b`') == ["https://a/"]


def test_ts_import_ignores_commented_out_lines() -> None:
    assert match_line("// import axios from 'axios';", "ts") == []
    assert match_line(" * from 'axios'", "ts") == []


def test_ts_import_requires_a_package_terminator() -> None:
    assert match_line("import retry from 'axios-retry';", "ts") == []
    assert match_line("import x from 'stripe-mock';", "ts") == []
    assert match_line("import v from 'pgvector';", "ts") == []


def test_ts_import_still_matches_exact_and_subpath_specs() -> None:
    assert [d.name for d in match_line("import { Client } from 'pg';", "ts")] == ["pg"]
    assert [d.name for d in match_line("import a from 'axios';", "ts")] == ["axios"]
    assert [d.name for d in match_line('import a from "axios/lib/x";', "ts")] == ["axios"]


def test_grep_recipes_lists_every_detector() -> None:
    text = grep_recipes()
    for d in ALL_DETECTORS:
        assert d.name in text
