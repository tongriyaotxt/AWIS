#!/usr/bin/env python3
"""
llm-chat converter output must carry NO Codex pins.

Adapted from ARIS (MIT), see NOTICE.

Uses the real proof-checker / experiment-audit / research-review sources as
fixtures (the skills with the densest reviewer payloads): after
convert_content(), no OpenAI model pin, no model_reasoning_effort knob, and no
mcp__codex__ tool name may survive — a leftover pin would be sent verbatim to a
generic OpenAI-compatible backend that rejects or misroutes it.

Run: python3 tests/test_llm_chat_converter.py   (also pytest-compatible)

NOTE (AWIS): this test depends on tools/convert_skills_to_llm_chat.py and the
upstream skill fixtures, which do not exist in AWIS. It self-skips unless both
are present.
"""
import os
import re
import sys

import pytest

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
_CONVERTER = os.path.join(REPO, "tools", "convert_skills_to_llm_chat.py")

FIXTURES = [
    "skills/proof-checker/SKILL.md",
    "skills/experiment-audit/SKILL.md",
    "skills/research-review/SKILL.md",
    "skills/result-to-claim/SKILL.md",
    "skills/kill-argument/SKILL.md",
    "skills/interview-cheatsheet/SKILL.md",
    "skills/patent-review/SKILL.md",
    "skills/render-html/SKILL.md",
    "skills/auto-review-loop/SKILL.md",
]

_FIXTURES_PRESENT = all(os.path.isfile(os.path.join(REPO, f)) for f in FIXTURES)
_CONVERTER_PRESENT = os.path.isfile(_CONVERTER)

pytestmark = pytest.mark.skipif(
    not (_CONVERTER_PRESENT and _FIXTURES_PRESENT),
    reason="AWIS has no skills converter or upstream skill fixtures (self-skip)",
)

if _CONVERTER_PRESENT:
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from convert_skills_to_llm_chat import convert_content  # noqa: E402
else:
    convert_content = None

FORBIDDEN = re.compile(r"mcp__codex__|model_reasoning_effort|model_#|model:\s*[\"'`]?gpt-|model:\s*REVIEWER_MODEL")


def offending_lines(path):
    src = open(os.path.join(REPO, path), encoding="utf-8").read()
    out = convert_content(src)
    bad = []
    for i, line in enumerate(out.split("\n"), 1):
        if "mcp__manual_review" in line:   # separate MCP, not a Codex pin
            continue
        if FORBIDDEN.search(line):
            bad.append(f"{path} (converted) line {i}: {line.strip()[:100]}")
    return bad


def test_converted_output_has_no_codex_pins():
    problems = []
    for f in FIXTURES:
        problems += offending_lines(f)
    assert not problems, "\n".join(problems)


if __name__ == "__main__":
    ps = []
    for f in FIXTURES:
        ps += offending_lines(f)
    if ps:
        print("\n".join(ps))
        sys.exit(1)
    print(f"ok: {len(FIXTURES)} fixtures convert clean")
