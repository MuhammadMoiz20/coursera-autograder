#!/usr/bin/env python3

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

from util import print_stderr, send_feedback

DEFAULT_RESULTS_FILENAME = "cypress-results.json"
MAX_DETAIL_ENTRIES = 20

PASS_STATES = {"passed", "pass", "success"}
FAIL_STATES = {"failed", "fail", "broken", "errored", "error"}
PENDING_STATES = {"pending", "skipped", "skip", "canceled", "cancelled"}

ENCRYPTED_SUFFIXES = (".enc", ".encrypted")
SECRET_ENV_VAR = "CYPRESS_RESULTS_SECRET"
SECRET_FILE_ENV_VAR = "CYPRESS_RESULTS_SECRET_FILE"
ENCRYPTED_FLAG_ENV_VAR = "CYPRESS_RESULTS_ENCRYPTED"
ENCRYPTION_ALGO_ENV_VAR = "CYPRESS_ENCRYPTION_ALGORITHM"
ENCRYPTION_ITER_ENV_VAR = "CYPRESS_ENCRYPTION_ITERATIONS"
DEFAULT_ENCRYPTION_ALGORITHM = "aes-256-cbc"
DEFAULT_ENCRYPTION_ITERATIONS = 100_000
OPENSSL_BINARY_ENV_VAR = "OPENSSL_BIN"
DEFAULT_SECRET_VALUE = "your-long-passphrase"

_CACHED_SECRET: Optional[str] = None
_SECRET_INITIALISED = False


class CypressResultsError(Exception):
    """Raised when the supplied Cypress results cannot be processed."""


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return None


def _expand_candidate_filenames(base_name: str) -> List[str]:
    names: List[str] = []

    def add(name: str) -> None:
        if name not in names:
            names.append(name)

    add(base_name)
    lower_name = base_name.lower()

    if not lower_name.endswith(".enc"):
        add(f"{base_name}.enc")

    if lower_name.endswith(".json") and not lower_name.endswith(".json.enc"):
        add(f"{base_name[:-5]}.json.enc")

    add(DEFAULT_RESULTS_FILENAME)
    add(f"{DEFAULT_RESULTS_FILENAME}.enc")
    add("cypress-results.enc")

    return names


def _secret_configured() -> bool:
    if _SECRET_INITIALISED:
        return bool(_CACHED_SECRET)
    if os.environ.get(SECRET_ENV_VAR) or os.environ.get(SECRET_FILE_ENV_VAR):
        return True
    # Check if a partId might be available to use as secret
    if len(sys.argv) > 1 and sys.argv[1]:
        return True
    return bool(DEFAULT_SECRET_VALUE)


def get_results_secret(part_id: Optional[str] = None, required: bool = False) -> Optional[str]:
    global _CACHED_SECRET, _SECRET_INITIALISED
    if _SECRET_INITIALISED:
        if required and not _CACHED_SECRET:
            raise CypressResultsError(
                "Encrypted Cypress results detected but no decryption secret was provided."
            )
        return _CACHED_SECRET

    _SECRET_INITIALISED = True
    secret_file = os.environ.get(SECRET_FILE_ENV_VAR)
    secret_value: Optional[str] = None

    if secret_file:
        path = Path(secret_file).expanduser()
        if not path.is_file():
            raise CypressResultsError(
                f"Cypress secret file '{path}' does not exist or is not readable."
            )
        try:
            secret_value = path.read_text(encoding="utf-8").strip()
        except OSError as err:
            raise CypressResultsError(
                f"Unable to read Cypress secret file '{path}': {err}"
            ) from err
    else:
        # Try env var first
        secret_value = os.environ.get(SECRET_ENV_VAR, "").strip()
        
        # If not found in env, use part_id if available
        if not secret_value and part_id:
             print_stderr(f"Using partId as decryption secret.")
             secret_value = part_id

    if not secret_value:
        # Fallback to default if nothing else works (for local testing mainly)
        secret_value = DEFAULT_SECRET_VALUE

    _CACHED_SECRET = secret_value or None

    if required and not _CACHED_SECRET:
        raise CypressResultsError(
            "Encrypted Cypress results detected but no decryption secret was provided. "
            "The grader expects the encryption key to match the 'partId' of this assignment."
        )

    return _CACHED_SECRET


def should_treat_as_encrypted(path: Path) -> bool:
    flag = _parse_bool(os.environ.get(ENCRYPTED_FLAG_ENV_VAR))
    if flag is not None:
        return flag
    suffix = path.suffix.lower()
    if suffix in ENCRYPTED_SUFFIXES:
        return True
    name = path.name.lower()
    return any(name.endswith(enc_suffix) for enc_suffix in ENCRYPTED_SUFFIXES)


def decrypt_results_file(path: Path, part_id: Optional[str] = None, *, quiet: bool = False) -> bytes:
    secret = get_results_secret(part_id=part_id, required=True)
    openssl_bin = os.environ.get(OPENSSL_BINARY_ENV_VAR, "openssl")
    openssl_path = shutil.which(openssl_bin)
    if not openssl_path:
        raise CypressResultsError(
            f"OpenSSL binary '{openssl_bin}' not found. Install OpenSSL or set "
            f"{OPENSSL_BINARY_ENV_VAR} to the correct executable."
        )

    algorithm = os.environ.get(ENCRYPTION_ALGO_ENV_VAR, DEFAULT_ENCRYPTION_ALGORITHM)
    algorithm_flag = (
        algorithm if algorithm.startswith("-") else f"-{algorithm}"
    )
    iterations = os.environ.get(
        ENCRYPTION_ITER_ENV_VAR, str(DEFAULT_ENCRYPTION_ITERATIONS)
    )

    secret_env = f"CYPRESS_SECRET_{os.getpid()}"
    env = os.environ.copy()
    env[secret_env] = secret  # type: ignore[arg-type]

    command = [
        openssl_path,
        "enc",
        algorithm_flag,
        "-pbkdf2",
        "-iter",
        iterations,
        "-d",
        "-in",
        str(path),
        "-pass",
        f"env:{secret_env}",
    ]

    if not quiet:
        print_stderr(
            "Decrypting encrypted Cypress results with OpenSSL command: "
            f"{' '.join(command[:-2])} <redacted>"
        )

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            env=env,
        )
    except subprocess.CalledProcessError as err:
        message = (
            "Please note that the Cypress results you submitted do not correspond to the correct test suite. "
            "Be sure to run and submit the Cypress tests included in the official lab starter pack."
        )
        raise CypressResultsError(message) from err

    return result.stdout


def read_results_bytes(path: Path, part_id: Optional[str] = None) -> bytes:
    if should_treat_as_encrypted(path):
        return decrypt_results_file(path, part_id=part_id)
    try:
        return path.read_bytes()
    except OSError as err:
        raise CypressResultsError(
            f"Unable to read results file '{path}': {err}"
        ) from err


def _maybe_decrypt_after_failure(
    path: Path, attempted_decrypt: bool, part_id: Optional[str] = None, *, reason: str
) -> Optional[bytes]:
    """Try decrypting when plaintext parsing fails but the file lacks .enc suffixes."""
    if attempted_decrypt:
        return None
    if should_treat_as_encrypted(path):
        return None
    print_stderr(
        "Plaintext parsing failed; retrying as encrypted Cypress results. "
        f"Reason: {reason}"
    )
    return decrypt_results_file(path, part_id=part_id)


def load_config() -> Dict:
    """Load the grader configuration file."""
    # Try current directory first (Docker standard), then script directory (local dev)
    candidates = [
        Path("config.json"),
        Path(__file__).parent / "config.json",
        Path(__file__).parent.parent / "config.json",
    ]

    for path in candidates:
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception as err:
                print_stderr(f"Warning: Failed to load config from {path}: {err}")
    
    print_stderr("Warning: config.json not found.")
    return {}


def main(part_id: Optional[str]) -> None:
    print_stderr(f"Starting Cypress JSON grader with partId: '{part_id}'")

    try:
        config = load_config()
        spec_pattern = config.get("cypressSpecPattern")
        
        # Support partId-specific patterns if provided as a dictionary
        if isinstance(spec_pattern, dict) and part_id:
            spec_pattern = spec_pattern.get(part_id)
        
        if spec_pattern:
            print_stderr(f"Filtering tests using pattern: {spec_pattern}")
        elif part_id and isinstance(config.get("cypressSpecPattern"), dict):
             print_stderr(f"No spec pattern configured for partId '{part_id}'. Checks may be too broad.")

        results_path = locate_results_file(part_id)
        print_stderr(f"Using Cypress results file: {results_path}")

        results_data = load_results(results_path, part_id)
        summary = summarize_results(results_data, spec_pattern=spec_pattern)

        total = summary["total_tests"]
        passed = summary["passed_tests"]
        failed = summary["failed_tests"]
        pending = summary["pending_tests"]
        details = summary["test_details"]

        if total == 0:
            raise CypressResultsError(
                "No tests were found in the provided Cypress results JSON file."
            )

        score_denominator = max(1, passed + failed)
        score = passed / score_denominator

        feedback_lines = build_feedback_lines(passed, failed, pending, score, details)
        send_feedback(score, "\n".join(feedback_lines))

    except CypressResultsError as err:
        print_stderr(f"Grading failed: {err}")
        send_feedback(0.0, str(err))
    except Exception as err:  # pragma: no cover - defensive
        print_stderr(f"Unexpected error: {err}")
        send_feedback(0.0, f"Unexpected error while reading Cypress results: {err}")


def locate_results_file(part_id: Optional[str] = None) -> Path:
    """Locate the Cypress results JSON file."""
    explicit_path = os.environ.get("CYPRESS_RESULTS_PATH")
    if explicit_path:
        path = Path(explicit_path).expanduser()
        if not path.is_file():
            raise CypressResultsError(
                f"Cypress results JSON not found at '{path}'. "
                "Update CYPRESS_RESULTS_PATH to point to a valid file."
            )
        return path.resolve()

    filename = os.environ.get("CYPRESS_RESULTS_FILENAME", DEFAULT_RESULTS_FILENAME)
    candidate_names = _expand_candidate_filenames(filename)
    submission_root = Path(
        os.environ.get("SHARED_SUBMISSION_PATH", "/shared/submission")
    )
    search_roots = _candidate_roots(submission_root)

    for root in search_roots:
        for name in candidate_names:
            candidate = root / name
            if candidate.is_file():
                return candidate.resolve()

    for root in search_roots:
        for json_path in sorted(root.glob("*.json")):
            try:
                with json_path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
                if is_probably_cypress_results(data):
                    print_stderr(
                        f"Detected Cypress results file by inspection: {json_path}"
                    )
                    return json_path.resolve()
            except Exception:
                continue

        # If we have a configured secret OR a part_id, look for .enc files
        if _secret_configured() or part_id:
            for enc_path in sorted(root.glob("*.enc")):
                try:
                    decrypted = decrypt_results_file(enc_path, part_id=part_id, quiet=True)
                    data = json.loads(decrypted.decode("utf-8"))
                except Exception:
                    continue
                if is_probably_cypress_results(data):
                    print_stderr(
                        f"Detected encrypted Cypress results file by inspection: {enc_path}"
                    )
                    return enc_path.resolve()

    raise CypressResultsError(
        f"Could not find a Cypress results file named '{filename}'. "
        "Either include the file in your submission or set CYPRESS_RESULTS_PATH."
    )


def load_results(path: Path, part_id: Optional[str] = None) -> Dict:
    """Load and validate the Cypress results JSON document."""
    attempted_decrypt = False
    raw_bytes = read_results_bytes(path, part_id=part_id)

    while True:
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as err:
            maybe_decrypted = _maybe_decrypt_after_failure(
                path, attempted_decrypt, part_id=part_id, reason=str(err)
            )
            if maybe_decrypted is not None:
                raw_bytes = maybe_decrypted
                attempted_decrypt = True
                continue
            raise CypressResultsError(
                f"Results file '{path}' is not valid UTF-8 encoded text: {err}"
            ) from err

        try:
            data = json.loads(text)
        except json.JSONDecodeError as err:
            maybe_decrypted = _maybe_decrypt_after_failure(
                path, attempted_decrypt, part_id=part_id, reason=str(err)
            )
            if maybe_decrypted is not None:
                raw_bytes = maybe_decrypted
                attempted_decrypt = True
                continue
            raise CypressResultsError(
                f"Results file '{path}' is not valid JSON: {err}"
            ) from err

        break

    if not isinstance(data, dict):
        raise CypressResultsError(
            "Cypress results JSON must contain an object at the top level."
        )

    if not is_probably_cypress_results(data):
        raise CypressResultsError(
            "Provided JSON file does not look like Cypress test results."
        )

    return data


def summarize_results(data: Dict, spec_pattern: Optional[str] = None) -> Dict[str, object]:
    """Summarize pass/fail counts and collect per-test details."""
    details: List[Dict[str, object]] = []
    passed = failed = pending = 0

    for test in iter_all_tests(data, spec_pattern=spec_pattern):
        title = format_test_title(test)
        state, error_message = extract_state_and_error(test)

        if state in PASS_STATES:
            passed += 1
            passed_flag = True
        elif state in FAIL_STATES:
            failed += 1
            passed_flag = False
        elif state in PENDING_STATES:
            pending += 1
            passed_flag = False
        else:
            # Treat unknown states as failures to avoid inflating scores.
            failed += 1
            passed_flag = False
            if not error_message:
                error_message = f"Test reported unknown state '{state}'."

        details.append(
            {
                "title": title,
                "passed": passed_flag,
                "state": state,
                "error": error_message,
            }
        )

    total = passed + failed + pending

    if total == 0:
        stats = aggregate_stats(data)
        passed = stats["passes"]
        failed = stats["failures"]
        pending = stats["pending"]
        total = passed + failed + pending

    return {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "pending_tests": pending,
        "test_details": details,
    }


def build_feedback_lines(
    passed: int,
    failed: int,
    pending: int,
    score: float,
    details: List[Dict[str, object]],
) -> List[str]:
    """Format the feedback message sent back to Coursera."""
    lines: List[str] = []
    executed = passed + failed

    if failed == 0 and executed > 0:
        lines.append("All executed Cypress tests passed.")
    else:
        lines.append(f"You passed {passed} of {max(1, executed)} executed Cypress tests.")

    if pending:
        lines.append(
            f"{pending} tests are pending or skipped; they do not affect the score."
        )

    lines.append("")
    lines.append("Test summary:")
    lines.append(f"Passed: {passed}")
    lines.append(f"Failed: {failed}")
    lines.append(f"Pending: {pending}")
    lines.append(f"Score: {score:.2%}")

    if details:
        lines.append("")
        lines.append("Detailed results:")
        for entry in details[:MAX_DETAIL_ENTRIES]:
            state = entry["state"]
            prefix = "✅"
            if state in FAIL_STATES:
                prefix = "❌"
            elif state in PENDING_STATES:
                prefix = "⚠️"
            lines.append(f"{prefix} {entry['title']} ({state})")
            if entry.get("error") and state in FAIL_STATES:
                lines.append(f"   Error: {entry['error']}")

        if len(details) > MAX_DETAIL_ENTRIES:
            lines.append(
                f"...and {len(details) - MAX_DETAIL_ENTRIES} more test results."
            )

    return lines


def iter_all_tests(data: Dict, spec_pattern: Optional[str] = None) -> Iterator[Dict]:
    """Yield every test dictionary found in the Cypress results JSON."""
    runs = data.get("runs")
    if isinstance(runs, list):
        for run in runs:
            if spec_pattern:
                spec = run.get("spec", {})
                # relative path is preferred, but name is fallback
                spec_name = spec.get("relative") or spec.get("name") or ""
                # If the spec name doesn't match the pattern, skip all tests in this run
                if not re.search(spec_pattern, spec_name, re.IGNORECASE):
                    continue

            tests = run.get("tests")
            if isinstance(tests, list):
                for test in tests:
                    if isinstance(test, dict):
                        yield test
            suites = run.get("suites")
            if suites:
                yield from iter_suite_tests(suites)

    tests = data.get("tests")
    if isinstance(tests, list):
        for test in tests:
            if isinstance(test, dict):
                yield test

    results = data.get("results")
    if isinstance(results, list):
        for result in results:
            suites = result.get("suites")
            if suites:
                yield from iter_suite_tests(suites)


def iter_suite_tests(node) -> Iterator[Dict]:
    """Recursively walk suite structures to extract tests."""
    if isinstance(node, dict):
        tests = node.get("tests")
        if isinstance(tests, list):
            for test in tests:
                if isinstance(test, dict):
                    yield test
        suites = node.get("suites")
        if suites:
            yield from iter_suite_tests(suites)
    elif isinstance(node, list):
        for item in node:
            yield from iter_suite_tests(item)


def format_test_title(test: Dict) -> str:
    """Return a human-readable title for a test entry."""
    title = test.get("title") or test.get("name") or test.get("id") or "Untitled test"
    if isinstance(title, list):
        title = " › ".join(str(part) for part in title if part is not None)
    return str(title)


def extract_state_and_error(test: Dict) -> (str, Optional[str]):
    """Determine the test state and best available error message."""
    state = test.get("state") or test.get("status")
    if isinstance(state, str):
        state = state.lower()

    if not state:
        if test.get("pass") or test.get("passed") is True:
            state = "passed"
        elif test.get("fail") or test.get("failed") is True:
            state = "failed"
        elif test.get("pending"):
            state = "pending"
        else:
            state = "unknown"

    error_message = (
        test.get("displayError")
        or test.get("err")
        or test.get("error")
        or test.get("message")
    )

    attempts = test.get("attempts")
    if isinstance(attempts, list) and attempts:
        for attempt in reversed(attempts):
            if not isinstance(attempt, dict):
                continue
            attempt_state = attempt.get("state")
            if isinstance(attempt_state, str):
                state = attempt_state.lower()
            attempt_error = attempt.get("error") or attempt.get("message")
            if attempt_error:
                error_message = attempt_error
            if attempt_state:
                break

    err_block = test.get("err")
    if state == "unknown" and isinstance(err_block, dict):
        if err_block:
            state = "failed"
            if not error_message:
                error_message = err_block
        else:
            state = "passed"

    return state, _normalise_error_message(error_message)


def _normalise_error_message(raw_error) -> Optional[str]:
    if raw_error is None:
        return None
    if isinstance(raw_error, str):
        return raw_error.strip()
    if isinstance(raw_error, dict):
        if not raw_error:
            return None
        for key in ("message", "displayMessage", "stack", "stacktrace", "name"):
            value = raw_error.get(key)
            if value:
                return str(value).strip()
        try:
            return json.dumps(raw_error)
        except Exception:  # pragma: no cover - fallback defensive
            return str(raw_error)
    return str(raw_error)


def aggregate_stats(data: Dict) -> Dict[str, int]:
    """Aggregate stats blocks to recover totals when no per-test data exists."""
    totals = {"tests": 0, "passes": 0, "failures": 0, "pending": 0}
    for stats in iter_stats_blocks(data):
        totals["tests"] += int(stats.get("tests", 0))
        totals["passes"] += int(
            stats.get("passes")
            or stats.get("pass")
            or stats.get("testsPassed")
            or stats.get("successes", 0)
        )
        totals["failures"] += int(
            stats.get("failures")
            or stats.get("failed")
            or stats.get("testsFailed")
            or stats.get("fail", 0)
        )
        totals["pending"] += int(stats.get("pending") or stats.get("skipped", 0))

    return totals


def iter_stats_blocks(data: Dict) -> Iterable[Dict]:
    """Yield every stats dictionary found within the Cypress results."""
    stats = data.get("stats")
    if isinstance(stats, dict):
        yield stats

    runs = data.get("runs")
    if isinstance(runs, list):
        for run in runs:
            run_stats = run.get("stats")
            if isinstance(run_stats, dict):
                yield run_stats


def is_probably_cypress_results(data: Dict) -> bool:
    """Heuristically determine if the JSON document looks like Cypress output."""
    if not isinstance(data, dict):
        return False

    if "runs" in data and isinstance(data["runs"], list):
        return True

    stats = data.get("stats")
    if isinstance(stats, dict) and any(
        key in stats for key in ("tests", "passes", "failures", "testsRegistered")
    ):
        return True

    if isinstance(data.get("tests"), list):
        return True

    if isinstance(data.get("results"), list):
        return True

    return False


def _candidate_roots(submission_root: Path) -> List[Path]:
    roots = []
    learn_path = submission_root / "learn"
    if learn_path.exists() and learn_path.is_dir():
        roots.append(learn_path)
    roots.append(submission_root)
    return roots


if __name__ == "__main__":
    try:
        # Support partId from env or CLI
        part_id = os.environ.get("partId")
        if not part_id and len(sys.argv) > 1:
            part_id = sys.argv[1]

        if not part_id:
            print_stderr("Warning: partId not set in environment or arguments. Grading may be insecure if no specific secret is used.")
            # We allow continuing because the user might have set CYPRESS_RESULTS_SECRET manually
        
        main(part_id)
    except CypressResultsError as err:
        print_stderr(f"Startup failed: {err}")
        send_feedback(0.0, str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        print_stderr("Grader interrupted by user.")
        send_feedback(0.0, "Grader interrupted.")
        sys.exit(1)
