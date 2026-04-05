# Homework 2: Simple GenAI Workflow Prototype

This repository contains my work for Homework 2 in the Generative AI course. The goal of this project is to build and evaluate a simple LLM-based workflow for a business writing task.

## Business Workflow
The workflow I chose is turning messy internal meeting notes into structured action items.

## User
The main user is a project coordinator, team lead, or manager who needs a clear follow-up draft after a meeting.

## Input
The system receives raw meeting notes. These notes may be incomplete, informal, mixed in quality, or partially ambiguous.

## Output
The system should produce:
- a short meeting summary
- a structured list of action items
- a section for missing, unclear, or conflicting information that requires human review

## Why This Task Is Valuable
This task is valuable because teams often lose time after meetings trying to clean up notes, identify next steps, and assign responsibilities. A first-pass LLM workflow can save time and improve consistency, but it still needs human review when details are missing or ambiguous.

## Files in This Repository
- `README.md`: project overview, workflow description, setup notes, commit summary, and video link
- `app.py`: the Python prototype that runs the workflow and makes real LLM API calls
- `prompts.md`: the prompt versions and notes on prompt iteration
- `eval_set.json`: a small reusable evaluation set with 5 test cases
- `report.md`: the short written report for this assignment

## Model and Tooling
This project uses the Gemini API through Google AI Studio. The Python script is designed to run from the command line and use an API key stored in an environment variable.

## Walkthrough Video
https://youtu.be/HmvwWbnEhRM