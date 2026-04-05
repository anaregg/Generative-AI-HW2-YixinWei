# The initial version
```
import argparse
import json
import os
import sys
from pathlib import Path

from google import genai


def load_eval_cases(eval_path: Path) -> list[dict]:
    """Load evaluation cases from the local JSON file."""
    if not eval_path.exists():
        raise FileNotFoundError(f"Missing evaluation file: {eval_path}")

    with eval_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def find_case(cases: list[dict], case_id: str) -> dict | None:
    """Return the matching case by id."""
    for case in cases:
        if case.get("id") == case_id:
            return case
    return None


def build_prompt(case: dict) -> str:
    """Build the final user prompt for the selected evaluation case."""
    return (
        f"Case ID: {case['id']}\n"
        f"Case Type: {case['case_type']}\n\n"
        f"Raw meeting notes:\n{case['input']}\n\n"
        "Write the follow-up draft now."
    )


def generate_output(client: genai.Client, case: dict) -> str:
    """Call Gemini and return the generated markdown text."""
    prompt = build_prompt(case)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"system_instruction": SYSTEM_INSTRUCTION},
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("The API returned an empty response.")
    return text.strip()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a structured follow-up draft from a meeting-notes evaluation case."
    )
    parser.add_argument(
        "case_id",
        nargs="?",
        help="The case id from eval_set.json, for example: case_1_normal",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the available case ids and exit.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the end-to-end workflow for one selected case."""
    args = parse_args()
    project_dir = Path(__file__).resolve().parent
    eval_path = project_dir / "eval_set.json"
    output_dir = project_dir / "outputs"

    try:
        cases = load_eval_cases(eval_path)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"Error: Could not parse eval_set.json: {error}", file=sys.stderr)
        return 1

    if args.list:
        print("Available case ids:")
        for case in cases:
            print(f"- {case.get('id')}")
        return 0

    if not args.case_id:
        print("Error: Please provide a case id or use --list.", file=sys.stderr)
        return 1

    case = find_case(cases, args.case_id)
    if case is None:
        print(f"Error: Invalid case id '{args.case_id}'.", file=sys.stderr)
        print("Use --list to see available case ids.", file=sys.stderr)
        return 1

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        return 1

    try:
        client = genai.Client(api_key=api_key)
        output_text = generate_output(client, case)
    except Exception as error:
        print(f"Error: Gemini API request failed: {error}", file=sys.stderr)
        return 1

    # Create the output folder only when we have a successful result to save.
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{case['id']}.md"
    output_path.write_text(output_text + "\n", encoding="utf-8")

    print(f"Case ID: {case['id']}")
    print()
    print(output_text)
    print()
    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

# Revision 1
```
import argparse
import json
import os
import sys
from pathlib import Path

from google import genai

def load_eval_cases(eval_path: Path) -> list[dict]:
    """Load evaluation cases from the local JSON file."""
    if not eval_path.exists():
        raise FileNotFoundError(f"Missing evaluation file: {eval_path}")

    with eval_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def find_case(cases: list[dict], case_id: str) -> dict | None:
    """Return the matching case by id."""
    for case in cases:
        if case.get("id") == case_id:
            return case
    return None


def build_prompt(case: dict) -> str:
    """Build the final user prompt for the selected evaluation case."""
    return (
        f"Case ID: {case['id']}\n"
        f"Case Type: {case['case_type']}\n\n"
        f"Raw meeting notes:\n{case['input']}\n\n"
        "Write the follow-up draft now."
    )


def generate_output(client: genai.Client, case: dict) -> str:
    """Call Gemini and return the generated markdown text."""
    prompt = build_prompt(case)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"system_instruction": SYSTEM_INSTRUCTION},
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("The API returned an empty response.")
    return text.strip()


def build_output_path(output_dir: Path, case_id: str, tag: str | None) -> Path:
    """Build the output file path, optionally including a short tag."""
    if not tag:
        filename = f"{case_id}.md"
    else:
        # Keep filenames simple and safe for repeated runs.
        safe_tag = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in tag)
        filename = f"{case_id}_{safe_tag}.md"
    return output_dir / filename


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a structured follow-up draft from a meeting-notes evaluation case."
    )
    parser.add_argument(
        "case_id",
        nargs="?",
        help="The case id from eval_set.json, for example: case_1_normal",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the available case ids and exit.",
    )
    parser.add_argument(
        "--tag",
        help="Optional tag for the saved file name, for example: outputs/case_1_normal_v2.md",
    )
    return parser.parse_args()


def main() -> int:
    """Run the end-to-end workflow for one selected case."""
    args = parse_args()
    project_dir = Path(__file__).resolve().parent
    eval_path = project_dir / "eval_set.json"
    output_dir = project_dir / "outputs"

    try:
        cases = load_eval_cases(eval_path)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"Error: Could not parse eval_set.json: {error}", file=sys.stderr)
        return 1

    if args.list:
        print("Available case ids:")
        for case in cases:
            print(f"- {case.get('id')}")
        return 0

    if not args.case_id:
        print("Error: Please provide a case id or use --list.", file=sys.stderr)
        return 1

    case = find_case(cases, args.case_id)
    if case is None:
        print(f"Error: Invalid case id '{args.case_id}'.", file=sys.stderr)
        print("Use --list to see available case ids.", file=sys.stderr)
        return 1

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        return 1

    try:
        client = genai.Client(api_key=api_key)
        output_text = generate_output(client, case)
    except Exception as error:
        print(f"Error: Gemini API request failed: {error}", file=sys.stderr)
        return 1

    # Create the output folder only when we have a successful result to save.
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = build_output_path(output_dir, case["id"], args.tag)
    output_path.write_text(output_text + "\n", encoding="utf-8")

    print(f"Case ID: {case['id']}")
    print()
    print(output_text)
    print()
    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## What changed and why
I strengthened the instruction so that incomplete but supported actions would stay in the Action Items section, and I also added tagged output saving so I could compare different runs without overwriting earlier results. I made these changes because the earlier version sometimes dropped valid but incomplete actions and made it harder to keep evidence from repeated tests.

## What improved / stayed the same / got worse
The revised version became more conservative about uncertainty and did a better job surfacing the release-date conflict, ambiguous ownership, and unclear finance status in Needs Human Review. However, it still turned a conflicted next step into a committed action item, and the meeting summary remained too generic rather than highlighting the actual uncertainty in the notes.

# Revision 2
```
import argparse
import json
import os
import sys
from pathlib import Path

from google import genai

def load_eval_cases(eval_path: Path) -> list[dict]:
    """Load evaluation cases from the local JSON file."""
    if not eval_path.exists():
        raise FileNotFoundError(f"Missing evaluation file: {eval_path}")

    with eval_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def find_case(cases: list[dict], case_id: str) -> dict | None:
    """Return the matching case by id."""
    for case in cases:
        if case.get("id") == case_id:
            return case
    return None


def build_prompt(case: dict) -> str:
    """Build the final user prompt for the selected evaluation case."""
    return (
        f"Case ID: {case['id']}\n"
        f"Case Type: {case['case_type']}\n\n"
        f"Raw meeting notes:\n{case['input']}\n\n"
        "Write the follow-up draft now."
    )


def generate_output(client: genai.Client, case: dict) -> str:
    """Call Gemini and return the generated markdown text."""
    prompt = build_prompt(case)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"system_instruction": SYSTEM_INSTRUCTION},
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("The API returned an empty response.")
    return text.strip()


def build_output_path(output_dir: Path, case_id: str, tag: str | None) -> Path:
    """Build the output file path, optionally including a short tag."""
    if not tag:
        filename = f"{case_id}.md"
    else:
        # Keep filenames simple and safe for repeated runs.
        safe_tag = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in tag)
        filename = f"{case_id}_{safe_tag}.md"
    return output_dir / filename


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a structured follow-up draft from a meeting-notes evaluation case."
    )
    parser.add_argument(
        "case_id",
        nargs="?",
        help="The case id from eval_set.json, for example: case_1_normal",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the available case ids and exit.",
    )
    parser.add_argument(
        "--tag",
        help="Optional tag for the saved file name, for example: outputs/case_1_normal_v2.md",
    )
    return parser.parse_args()


def main() -> int:
    """Run the end-to-end workflow for one selected case."""
    args = parse_args()
    project_dir = Path(__file__).resolve().parent
    eval_path = project_dir / "eval_set.json"
    output_dir = project_dir / "outputs"

    try:
        cases = load_eval_cases(eval_path)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"Error: Could not parse eval_set.json: {error}", file=sys.stderr)
        return 1

    if args.list:
        print("Available case ids:")
        for case in cases:
            print(f"- {case.get('id')}")
        return 0

    if not args.case_id:
        print("Error: Please provide a case id or use --list.", file=sys.stderr)
        return 1

    case = find_case(cases, args.case_id)
    if case is None:
        print(f"Error: Invalid case id '{args.case_id}'.", file=sys.stderr)
        print("Use --list to see available case ids.", file=sys.stderr)
        return 1

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        return 1

    try:
        client = genai.Client(api_key=api_key)
        output_text = generate_output(client, case)
    except Exception as error:
        print(f"Error: Gemini API request failed: {error}", file=sys.stderr)
        return 1

    # Create the output folder only when we have a successful result to save.
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = build_output_path(output_dir, case["id"], args.tag)
    output_path.write_text(output_text + "\n", encoding="utf-8")

    print(f"Case ID: {case['id']}")
    print()
    print(output_text)
    print()
    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## What changed and why
In the final revision, I made the instruction stricter about conflict and uncertainty. I added clearer rules that blocked or disputed items should not be presented as committed action items, and that the model should not choose one owner when the notes only suggest multiple possibilities. I also revised the summary instruction so that it would mention the actual topics and uncertainty in the notes instead of using generic filler language. I made these changes because the previous version was more conservative than the baseline, but it still treated some conflicted next steps too confidently and produced summaries that were too generic.

## What improved / stayed the same / got worse
The final version improved mainly in how it handled conflict and uncertainty. Instead of turning the client update into a confirmed action item, it now keeps the issue in Needs Human Review, which is more accurate for this case. The summary is also better because it mentions the real uncertainty in the notes. The output stayed concise and structured. A possible downside is that the system is now more cautious, so it may produce fewer action items when the notes are ambiguous, but I think this is acceptable for a workflow that should still include human review.