# Report: Building and Evaluating a Simple GenAI Workflow

## Business Use Case

The business workflow I chose is turning raw internal meeting notes into a structured follow-up draft. In many teams, meeting notes are incomplete, informal, and inconsistent. A manager, project lead, or coordinator may need to read through scattered notes and quickly identify what happened, what needs to be done next, and what still requires clarification. This is a realistic business writing task because the output is not just a summary. It is a usable follow-up draft that can support project coordination and team communication.

In this workflow, the input is a short set of raw meeting notes, often written in fragments or mixed quality language. The desired output is a concise markdown draft with three sections: a short meeting summary, a list of action items, and a section for unclear or conflicting details that require human review. I chose this task because it is common, easy to evaluate with a small fixed test set, and useful enough to justify partial automation.

## Model Choice

I used the Gemini API through Google AI Studio and set the model in my script as `gemini-2.5-flash`. I chose this model mainly because it was easy to access through Google AI Studio, simple to connect in Python, and fast enough for repeated testing during prompt iteration. My goal was not to find the strongest possible model, but to build a small reproducible prototype that could make real LLM calls and be tested across multiple cases. The final script uses the Google GenAI SDK, loads cases from `eval_set.json`, and saves outputs to files for comparison. :contentReference[oaicite:2]{index=2}

I did not run a formal comparison across multiple models. In this assignment, I prioritized a stable workflow and prompt iteration over model benchmarking. If I had more time, I would compare the same prompt on another Gemini model to see whether conflict handling or summary quality improves.

## Baseline vs. Final Design

My baseline design used a much simpler instruction. It asked the model to turn raw meeting notes into a follow-up draft with a short summary, action items, and a section for unclear information. This baseline was readable, but it had two important weaknesses. First, it sometimes dropped incomplete but valid action items. Second, it could still present uncertain or conflicted next steps too confidently.

One clear example appeared in the normal case. The earlier version correctly kept action items for Sarah and Mike, but it dropped the onboarding mockup update as a true action item because the owner was missing. Instead of keeping the task and marking the missing field, it pushed the issue into human review too aggressively. This showed that the baseline was conservative, but not complete enough.

In the next revision, I changed the prompt so that supported actions should remain in `Action Items` even if some fields are missing. I also made the output easier to compare by saving different runs with tags. This improved the result because the model no longer removed incomplete but valid tasks as often. However, conflict cases still exposed a problem: the model could treat blocked or disputed next steps as committed actions.

The final design added stricter rules for ambiguity and conflict. I explicitly told the model not to present an item as a committed action if it was blocked by unresolved conflict, missing approval, or disputed ownership. I also improved the instruction for the summary so that it had to mention the actual topics and uncertainty in the notes instead of using generic filler. In the final version, the system instruction also tells the model to separate supported actions from blocked or speculative items and place the latter in `Needs Human Review`. :contentReference[oaicite:3]{index=3}

This change improved the output in the conflict case. Earlier, the model turned the client update into an action item even though the release date and owner were still disputed. In the final version, it stopped doing that and instead wrote that no unblocked actions were identified with clear ownership and deadlines. It also surfaced the release-date conflict, disputed ownership, and unclear finance-number status in `Needs Human Review`. This final behavior is more cautious, but it is also more appropriate for a real business setting where the model should not silently make decisions.

## Where the Prototype Still Fails or Requires Human Review

Even in the final version, this prototype still requires human review. The biggest limitation is that the model must interpret short and messy notes, and sometimes the boundary between a discussion point and a true next step is not fully explicit. In ambiguous cases, a model may still be too cautious and produce fewer action items than a human would want, or it may miss useful implied structure. In mixed-language or sparse cases, the model can also produce summaries that are technically correct but still too generic. More importantly, the model cannot be trusted to resolve ownership disputes, approval dependencies, or conflicting timelines on its own. For this reason, the `Needs Human Review` section is not just a fallback; it is an essential part of the workflow.

## Deployment Recommendation

I would not recommend deploying this workflow as a fully automated system. I would recommend it only as a first-pass drafting tool under clear human-review conditions. In practice, this means the model could be used to organize messy notes, suggest action items, and highlight uncertainty, but a human manager or coordinator should review the draft before it is shared or used for execution. This is especially important when ownership is unclear, approvals are pending, or different parts of the notes conflict with each other.

Overall, I think this workflow is valuable enough to partially automate, but not safe enough to automate end to end. The final prompt design is better than the baseline because it is more structured, more conservative, and more honest about uncertainty. However, the assignment also showed that prompt iteration improves behavior without removing the need for human judgment.