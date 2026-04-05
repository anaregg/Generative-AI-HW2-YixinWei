"""Simple meeting-notes-to-follow-up draft generator.

Run:
    python app.py --list
    python app.py case_1_normal
"""

import argparse
import json
import os
import sys
from pathlib import Path

from google import genai


# Change this model name if you want to test a different Gemini model later.
MODEL_NAME = "gemini-2.5-flash"

# One reusable instruction block for the whole workflow.
SYSTEM_INSTRUCTION = """You turn raw internal meeting notes into a concise follow-up draft.

Return markdown with exactly these section headings and in this order:
## Meeting Summary
## Action Items
## Needs Human Review

Rules:
- Keep the writing concise and businesslike.
- Do not use tables.
- Use only information supported by the notes.
- If details are unclear, say what is missing instead of guessing.
- Put unresolved conflicts, missing owners, uncertain deadlines, and speculative items in Needs Human Review.
- Under Action Items, use short bullet points when there are actions to take.
"""


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
