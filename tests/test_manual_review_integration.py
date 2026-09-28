"""End-to-end integration test: simulates a real AWIS skill calling manual-review MCP.

Adapted from ARIS (MIT), see NOTICE.

This test:
1. Starts the MCP server as a subprocess (exactly how Claude Code would)
2. Sends a realistic code-review prompt (same format as an AWIS night-shift
   review round sends to the reviewer)
3. Simulates a user submitting a response via the HTTP endpoint
4. Verifies the MCP returns the correct format that skills expect
5. Tests review_reply (multi-round) with threadId continuity
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

import pytest

SERVER_PATH = Path(__file__).parent.parent / "mcp-servers" / "manual-review" / "server.py"

# A realistic review prompt (shortened version of what an AWIS overnight
# coding loop sends to the reviewer after a round of unattended changes)
REALISTIC_PROMPT = """You are reviewing an unattended overnight coding change. Please provide a detailed, structured review.

## Task: Add retry-with-backoff to the job queue worker

## Diff Summary:
The worker now wraps each job execution in a retry loop with exponential backoff
(base 1s, factor 2, max 5 attempts, jitter). Failed jobs are re-queued unless
they raise a non-retryable error...

## Key Changes:
- worker.py: new `run_with_retry()` helper, `NonRetryableError` exception
- queue.py: `requeue()` keeps the original attempt count in the job envelope
- tests: 6 new cases covering backoff timing and non-retryable short-circuit

## Test Results:
- pytest: 41 passed, 0 failed (baseline: 35 passed)
- New backoff tests use a fake clock; no real sleeps

## Review Instructions
Please act as a senior software reviewer. Provide:
1. **Overall Score** (1-10, where 6 = weak accept, 7 = accept)
2. **Summary** (2-3 sentences)
3. **Strengths** (bullet list, ranked)
4. **Weaknesses** (bullet list, ranked: CRITICAL > MAJOR > MINOR)
5. **For each CRITICAL/MAJOR weakness**: A specific, actionable fix
6. **Verdict**: Ready to merge? Yes / Almost / No

Focus on: correctness under concurrency, backoff edge cases, test adequacy.
"""

# A realistic review response (what a reviewer model would return)
REALISTIC_RESPONSE = """## Overall Score: 6/10

## Summary
The change adds a solid retry-with-backoff mechanism to the job queue worker with good test coverage of the timing logic. The core idea is sound but there are concurrency and state-tracking gaps that should be fixed before merge.

## Strengths
- Clean separation of retry policy (`run_with_retry`) from job execution
- Fake-clock tests avoid flaky timing-dependent assertions
- Non-retryable short-circuit prevents wasting attempts on permanent failures

## Weaknesses

### CRITICAL
1. **Attempt count is not persisted across worker restarts** — The attempt count lives only in the in-memory job envelope. If the worker crashes mid-backoff, the re-queued job restarts at attempt 0, so a poison job can loop forever across restarts.
   - **Fix**: Store `attempts` in the job record itself (e.g. a column or a Redis field) and increment it atomically on requeue.

### MAJOR
2. **No cap on total elapsed time** — 5 attempts at base 1s is fine, but combined with a slow job timeout a single job can hold a worker slot for many minutes, starving the queue.
   - **Fix**: Add a `max_elapsed_sec` budget checked before each retry.

3. **Jitter is applied before the cap** — With full jitter the effective delay can exceed the intended max interval.
   - **Fix**: Clamp after jitter, not before.

### MINOR
4. Naming inconsistency: `run_with_retry` vs `requeue` live in different modules but share retry-policy constants duplicated in both files.

## Verdict: Almost

The core mechanism is sound and well tested, but the lost attempt count (CRITICAL #1) can cause infinite poison-job loops in production. Fixable in a day.
"""


def send_jsonrpc(proc, method, params=None, req_id=1):
    msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params:
        msg["params"] = params
    payload = json.dumps(msg).encode("utf-8")
    header = f"Content-Length: {len(payload)}\r\n\r\n".encode("utf-8")
    proc.stdin.write(header + payload)
    proc.stdin.flush()


def read_response(proc, timeout=15):
    deadline = time.monotonic() + timeout
    header = b""
    while time.monotonic() < deadline:
        byte = proc.stdout.read(1)
        if not byte:
            break
        header += byte
        if header.endswith(b"\r\n\r\n"):
            break
    content_length = 0
    for line in header.decode("utf-8", errors="replace").split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
    if content_length == 0:
        return None
    body = proc.stdout.read(content_length)
    return json.loads(body.decode("utf-8"))


def simulate_user_submit(port, response_text, token="", delay=1.0):
    """Simulate a user pasting a response after a short delay."""
    time.sleep(delay)
    data = json.dumps({"response": response_text}).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/submit?token={token}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        print(f"  [submit error] {e}")
        return False


def find_server_port_and_token(pending_dir, timeout=8):
    """Read the port and token from the pending state file written by the server."""
    state_path = Path(pending_dir) / "pending_review.json"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if state_path.exists():
            try:
                data = json.loads(state_path.read_text(encoding="utf-8"))
                url = data.get("url", "")
                if url and ":" in url:
                    # URL format: http://127.0.0.1:PORT?token=TOKEN
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(url)
                    port = parsed.port
                    token = parse_qs(parsed.query).get("token", [""])[0]
                    # Verify it's actually responding
                    try:
                        urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/api/context?token={token}", timeout=1
                        )
                        return port, token
                    except:
                        pass
            except (json.JSONDecodeError, ValueError, OSError):
                pass
        time.sleep(0.3)
    return None, None


def test_manual_review_integration():
    tmpdir = tempfile.mkdtemp(prefix="awis_manual_review_test_")
    pending_dir = os.path.join(tmpdir, "pending_review")

    env = {
        **os.environ,
        "MANUAL_REVIEW_AUTO_OPEN": "false",
        "MANUAL_REVIEW_TIMEOUT_SEC": "30",
        "MANUAL_REVIEW_PENDING_DIR": pending_dir,
        "MANUAL_REVIEW_PORT": "28900",
    }

    proc = subprocess.Popen(
        [sys.executable, str(SERVER_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    try:
        # --- Step 1: MCP Initialize ---
        send_jsonrpc(proc, "initialize", {}, req_id=1)
        resp = read_response(proc)
        assert resp and resp["result"]["serverInfo"]["name"] == "manual-review"

        # Notify initialized
        send_jsonrpc(proc, "notifications/initialized", {}, req_id=2)
        read_response(proc)

        # --- Step 2: Simulate /research-review calling review tool ---

        # We need to find the port after the tool call starts the HTTP server.
        # The tool call will block until user submits, so we send it and then
        # find the port in a separate thread.

        # Send the tool call
        send_jsonrpc(proc, "tools/call", {
            "name": "review",
            "arguments": {
                "prompt": REALISTIC_PROMPT,
                "config": {"model_reasoning_effort": "xhigh"},
            },
        }, req_id=3)

        # Give the HTTP server a moment to start
        time.sleep(1.5)

        # Find the port by reading the pending state file
        port, token = find_server_port_and_token(pending_dir, timeout=8)
        assert port, "Could not find HTTP server port"

        # Verify /api/context returns the correct prompt
        ctx_resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/context?token={token}")
        ctx = json.loads(ctx_resp.read().decode("utf-8"))
        # Compare stripped to handle platform line-ending differences
        assert ctx["prompt"].strip() == REALISTIC_PROMPT.strip(), \
            f"Prompt mismatch! Lengths: sent={len(REALISTIC_PROMPT)}, got={len(ctx['prompt'])}"
        assert ctx["config"]["model_reasoning_effort"] == "xhigh"

        # --- Step 3: Simulate user submitting the review response ---
        submit_ok = simulate_user_submit(port, REALISTIC_RESPONSE, token=token, delay=0.5)
        assert submit_ok, "Submit failed!"

        # --- Step 4: Read the MCP tool result ---
        result = read_response(proc, timeout=10)
        assert result is not None, "No response from MCP server"
        assert "result" in result, f"Error response: {result}"

        content_text = result["result"]["content"][0]["text"]
        payload = json.loads(content_text)

        assert "threadId" in payload, f"Missing threadId: {payload}"
        assert "content" in payload, f"Missing content: {payload}"
        assert payload["content"].strip() == REALISTIC_RESPONSE.strip(), \
            f"Response mismatch! Lengths: sent={len(REALISTIC_RESPONSE)}, got={len(payload['content'])}"
        thread_id = payload["threadId"]

        # --- Step 5: Verify skill can parse the response ---
        response_text = payload["content"]

        # Parse score (same regex pattern skills use)
        import re
        score_match = re.search(r"Score[:\s]*(\d+)/10", response_text)
        assert score_match, "Could not parse score from response"
        score = int(score_match.group(1))
        assert score == 6, f"Wrong score: {score}"

        # Parse verdict
        verdict_match = re.search(r"Verdict[:\s]*(.*)", response_text)
        assert verdict_match, "Could not parse verdict"

        # --- Step 6: Test review_reply (multi-round) ---

        round2_prompt = """Round 2/4 of the overnight review loop.

Since last review, we have:
- Persisted the attempt count in the job record, incremented atomically on requeue
- Added a max_elapsed_sec budget checked before each retry
- Moved the clamp after jitter so the effective delay never exceeds the cap

Please re-score and re-assess. Has the change improved?
"""
        send_jsonrpc(proc, "tools/call", {
            "name": "review_reply",
            "arguments": {
                "threadId": thread_id,
                "prompt": round2_prompt,
                "config": {"model_reasoning_effort": "xhigh"},
            },
        }, req_id=4)

        time.sleep(1.5)
        port2, token2 = find_server_port_and_token(pending_dir, timeout=8)
        assert port2, "Could not find HTTP server for round 2"

        # Verify history is shown
        ctx2_resp = urllib.request.urlopen(f"http://127.0.0.1:{port2}/api/context?token={token2}")
        ctx2 = json.loads(ctx2_resp.read().decode("utf-8"))
        assert len(ctx2["history"]) >= 2, f"Expected history, got: {len(ctx2['history'])} items"
        assert ctx2["history"][0]["role"] == "user"
        assert ctx2["history"][0]["content"].strip() == REALISTIC_PROMPT.strip()

        # Submit round 2 response
        round2_response = "## Overall Score: 7/10\n\nThe change has improved significantly. All three major issues addressed."
        simulate_user_submit(port2, round2_response, token=token2, delay=0.5)

        result2 = read_response(proc, timeout=10)
        assert result2 is not None
        payload2 = json.loads(result2["result"]["content"][0]["text"])
        assert payload2["threadId"] == thread_id, "ThreadId should be preserved across rounds"
        assert "7/10" in payload2["content"]
    finally:
        proc.terminate()
        proc.wait(timeout=3)
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
