# Submission

## Summary of changes

Fixed the state machine bugs that were letting invalid transitions through, tightened up the active queue filtering and sort order, made the action buttons contextual so the UI only shows what's actually allowed, and added test coverage for all the workflow rules.

## Bugs fixed

**Active queue included `rejected` and `escalated` items**
`list_review_items` only filtered out `approved`. The other two terminal statuses slipped through and showed up in the queue with no valid actions available. Fixed by filtering against all three terminal statuses.

**Queue sort order was wrong**
Items were sorted by `submitted_at` newest-first, which is the opposite of the tiebreaker rule, and risk level and customer tier were ignored entirely. Fixed the sort key to: risk level descending → customer tier descending → submitted_at ascending.

**`claim` allowed reclaiming an `in_review` item**
The guard was checking for terminal states but not for `in_review`. An item already assigned to another reviewer could be claimed again, silently overwriting the assignee. Fixed to require `status == "unassigned"`.

**`approve / reject / escalate` had almost no guards**
The check only blocked re-approving an already-approved item. You could reject a rejected item, escalate an approved one, or approve something that was never claimed. Fixed with a terminal state check first (returns 409), then a guard requiring `status == "in_review"`.

**All four action buttons always visible**
The UI showed Claim, Approve, Reject, and Escalate for every item regardless of status. Clicking an invalid action gave a generic error with no explanation. Buttons are now gated on the item's current status — `unassigned` shows only Claim, `in_review` shows the three closing actions, terminal items show a "closed" notice.

**Terminal items stayed in the queue after closing**
After approving or rejecting an item it stayed in the sidebar with nothing to do on it. Fixed to remove it from the local list on a terminal action response and auto-select the next item.

## Product / UX decisions

**Color-coded risk badges in the queue list.** Wanted reviewers to be able to confirm at a glance that the list is sorted correctly. Red for high, amber for medium, green for low. Didn't add filter/sort controls — the ordering spec is fixed and adding UI for it would just be noise.

**Contextual action buttons instead of disabled ones.** Hiding the inapplicable buttons is cleaner than disabling them with a tooltip. It also makes the mental model clearer: one action to claim, three to close.

**Color-coded status pill in the detail panel.** Quick visual cue when glancing at a neighboring item's status without reading the text.

## Tests added

14 new tests in `backend/tests/test_smoke.py`:

- Queue excludes all three terminal statuses
- Queue ordering (high risk before medium, priority before standard, older before newer)
- Claim works on `unassigned`, fails 409 on `in_review`
- Approve/reject/escalate work on `in_review`, fail 409 on `unassigned`
- All three terminal statuses block any further action with 409

Added an `autouse` fixture to reset seed data before each test so they don't share state.

## Known gaps

- No per-button loading state — all buttons disable during a request which is fine at this scale but would feel sluggish with real latency.
- No confirmation on Reject/Escalate — these are irreversible and probably should have a confirm step in production, but that needs modal infrastructure that isn't here yet.
- Reviewer is hardcoded as `alex` per the brief.
- No frontend tests — the state machine lives entirely in the backend, so that's where the test value is. The Vue layer is just display logic.

## Files changed and why

- `backend/app/main.py` — state machine guards, filtering, sorting, constants
- `backend/tests/test_smoke.py` — 14 new workflow tests, reset fixture
- `frontend/src/App.vue` — contextual buttons, terminal item removal, status/risk badges
- `frontend/src/styles.css` — styles for the new badge and pill variants


## Loom 
https://www.loom.com/share/16082a51831441ec9f8d7e4210448de5
