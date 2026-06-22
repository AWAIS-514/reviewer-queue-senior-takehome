# Senior Full-Stack Take-Home: Reviewer Queue

This repository contains a small existing full-stack application for a senior full-stack engineering take-home.

The goal is to assess how you improve a real but imperfect product slice under time pressure:

- understand an existing frontend and backend
- identify the highest-impact workflow and UX issues
- enforce business rules reliably
- add targeted tests
- explain pragmatic product and engineering tradeoffs

## Timebox

A strong senior candidate should be able to make a meaningful improvement in **60 minutes**.

Please stop after **90 minutes** and ensure that your changes are pushed.

Only commits pushed within the 90-minute limit will be reviewed. Please do not push additional commits after the time limit.

We do not expect you to fix every issue in the app.

## Setup and submission workflow

1. Fork this public repository into your own GitHub account.
2. Work in your fork.
3. Commit and push your changes to your fork before the 90-minute limit.
4. Submit the link to your fork, your `SUBMISSION.md`, and your walkthrough recording.

If your fork is private, please add `soccer-fan` and `muzer` as reviewers.

## Scenario

You are improving a small internal tool for an operations team.

Reviewers use the tool to:

- see which review items need attention
- inspect item details
- claim work
- approve, reject, or escalate items

The tool should help a reviewer answer:

- what should I work on next?
- who owns this item right now?
- what information do I need to make a decision?
- what actions are allowed on this item right now?

## What you need to submit

This starter app intentionally contains product and engineering rough edges. Improve it as if you were preparing a small but important production change.

Your final submission must include:

- a working local app
- fixes for the workflow correctness issues you judge most important
- at least one deliberate product or UX improvement
- a short `SUBMISSION.md`
- a short recorded walkthrough, ideally **about 3 minutes**

You have freedom to decide the best shape of the solution. We are interested in your judgment, not a checklist of framework-specific techniques.

## How to approach the work

Use the timebox to make the strongest improvement you can. We recommend prioritizing in this order:

1. **Workflow correctness**: state transitions should follow the rules below and invalid actions should fail cleanly.
2. **Reviewer experience**: the app should help a reviewer understand the item, its ownership, and what they can do next.
3. **Maintainability**: business rules should be easy to find, reason about, and test.
4. **Tests**: add targeted coverage for high-risk behavior you changed.
5. **Explanation**: document your decisions, known gaps, and how you used AI tools.

You do not need to fix every issue in the app. We care more about well-chosen, coherent improvements than a long list of shallow changes.

## Required workflow rules

The reviewer workflow must support these actions:

- `claim`
- `approve`
- `reject`
- `escalate`

Use these rules:

- only items with status `unassigned` can be claimed
- claiming an item moves it to `in_review`
- claiming an item records the acting reviewer
- only items with status `in_review` can be approved, rejected, or escalated
- `approved`, `rejected`, and `escalated` are terminal states
- terminal items must not allow further actions
- invalid actions should be rejected cleanly

For this exercise, you may hardcode the current reviewer identity as `alex`.

## Queue behavior

The active queue must exclude terminal items:

- `approved`
- `rejected`
- `escalated`

The active queue should be ordered by urgency:

1. higher `risk_level` outranks lower (`high > medium > low`)
2. within the same risk level, `priority` customers outrank `standard`
3. within the same bucket, older items outrank newer items

You may change how urgency is displayed if you think another presentation is clearer for reviewers.

## Product judgment

Make at least one deliberate product or UX improvement as part of your submission.

Choose the improvement based on what you think matters most for the reviewer workflow. Be prepared to explain:

- what problem you saw
- why you prioritized it
- what tradeoff you made inside the timebox

You do not need polished visual design.

## Running the app

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API runs at `http://localhost:8000`.

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

## Tests

Backend smoke tests are included:

```bash
cd backend
source .venv/bin/activate
pytest
```

You may add frontend or backend tests. Prefer tests that cover business behavior over broad snapshot or boilerplate coverage.

## What to submit

Please send us:

1. a link to your GitHub fork with your implementation
2. a `SUBMISSION.md`
3. a short recorded walkthrough, ideally **about 3 minutes**

Your fork must contain all commits you want us to review within the 90-minute limit. Commits pushed after the limit will not be counted.

## `SUBMISSION.md` convention

Write this in a way that makes your work easy to review. You can use the template below, or equivalent clear headings.

```markdown
# Submission

## Summary of changes

## Bugs fixed

## Product/UX decisions

## Tests added

## Known gaps

## Files changed and why

## AI assistance used
```

Keep it concise. Specific, evidence-backed statements are more useful than generic descriptions.

Good submissions make it clear:

- what behavior changed
- which files contain the important changes
- what tests or manual checks you ran
- what you intentionally did not address
- how AI tools helped and how you reviewed their output

You can start from [`SUBMISSION_TEMPLATE.md`](SUBMISSION_TEMPLATE.md).

## Code comments

You may use comments like this for non-obvious decisions:

```ts
// TAKEHOME: Explain the product or engineering tradeoff here.
```

or:

```py
# TAKEHOME: Explain the product or engineering tradeoff here.
```

Do not comment every change. Use these only when a reviewer would otherwise miss an important decision.

## Loom walkthrough

Please cover:

- a quick demo of the fixed workflow
- the highest-impact bug or UX issue you fixed
- where the business rules are enforced
- one product tradeoff you made
- what you would improve next with more time

## What we are looking for

We will review:

- whether the workflow rules are correctly enforced
- whether the reviewer experience is clear and practical
- whether tests cover meaningful behavior
- whether your code is maintainable for a small product team
- whether your written and recorded explanations match the actual implementation

We are not looking for:

- production infrastructure
- deployment
- authentication
- a full database migration
- pixel-perfect design
- large rewrites for their own sake

AI tools are allowed. We expect you to understand, own, and be able to defend the final submission.
