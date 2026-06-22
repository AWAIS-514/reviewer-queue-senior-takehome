import asyncio

import pytest
from fastapi import HTTPException

import app.main as main_module
from app.main import ActionRequest, apply_action, health, list_review_items


def run_async(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def reset_items():
    main_module.ITEMS = main_module.load_seed_items()
    yield


# ── original smoke tests ──────────────────────────────────────────────────────

def test_health_check() -> None:
    assert run_async(health()) == {"status": "ok"}


def test_review_items_endpoint_returns_seed_data() -> None:
    response = run_async(list_review_items())
    assert len(response["items"]) > 0


# ── active queue filtering ────────────────────────────────────────────────────

def test_active_queue_excludes_all_terminal_statuses() -> None:
    response = run_async(list_review_items(active_only=True))
    statuses = {item["status"] for item in response["items"]}
    assert "approved" not in statuses
    assert "rejected" not in statuses
    assert "escalated" not in statuses


def test_active_queue_includes_unassigned_and_in_review() -> None:
    response = run_async(list_review_items(active_only=True))
    statuses = {item["status"] for item in response["items"]}
    assert "unassigned" in statuses
    assert "in_review" in statuses


# ── queue ordering ────────────────────────────────────────────────────────────

def test_active_queue_orders_high_risk_priority_first() -> None:
    response = run_async(list_review_items(active_only=True))
    items = response["items"]
    # RV-1024: high risk, priority customer, 2026-04-02 — should rank #1
    assert items[0]["id"] == "RV-1024"
    assert items[0]["risk_level"] == "high"
    assert items[0]["customer_tier"] == "priority"


def test_active_queue_high_risk_outranks_medium_risk() -> None:
    response = run_async(list_review_items(active_only=True))
    items = response["items"]
    risk_levels = [item["risk_level"] for item in items]
    last_high = max(i for i, r in enumerate(risk_levels) if r == "high")
    first_medium = min(i for i, r in enumerate(risk_levels) if r == "medium")
    assert last_high < first_medium


# ── claim action ──────────────────────────────────────────────────────────────

def test_claim_unassigned_item() -> None:
    response = run_async(apply_action("RV-1024", ActionRequest(action="claim")))
    assert response["item"]["status"] == "in_review"
    assert response["item"]["assigned_reviewer"] == "alex"


def test_cannot_claim_already_in_review_item() -> None:
    with pytest.raises(HTTPException) as exc:
        run_async(apply_action("RV-1027", ActionRequest(action="claim")))
    assert exc.value.status_code == 409


# ── approve / reject / escalate ───────────────────────────────────────────────

def test_approve_in_review_item() -> None:
    response = run_async(apply_action("RV-1030", ActionRequest(action="approve")))
    assert response["item"]["status"] == "approved"


def test_reject_in_review_item() -> None:
    response = run_async(apply_action("RV-1027", ActionRequest(action="reject")))
    assert response["item"]["status"] == "rejected"


def test_escalate_in_review_item() -> None:
    response = run_async(apply_action("RV-1028", ActionRequest(action="escalate")))
    assert response["item"]["status"] == "escalated"


def test_cannot_approve_unassigned_item() -> None:
    with pytest.raises(HTTPException) as exc:
        run_async(apply_action("RV-1024", ActionRequest(action="approve")))
    assert exc.value.status_code == 409


def test_cannot_reject_unassigned_item() -> None:
    with pytest.raises(HTTPException) as exc:
        run_async(apply_action("RV-1024", ActionRequest(action="reject")))
    assert exc.value.status_code == 409


# ── terminal state protection ─────────────────────────────────────────────────

def test_cannot_act_on_approved_item() -> None:
    # RV-1029 is approved in seed data
    with pytest.raises(HTTPException) as exc:
        run_async(apply_action("RV-1029", ActionRequest(action="escalate")))
    assert exc.value.status_code == 409


def test_cannot_claim_escalated_item() -> None:
    # RV-1033 is escalated in seed data
    with pytest.raises(HTTPException) as exc:
        run_async(apply_action("RV-1033", ActionRequest(action="claim")))
    assert exc.value.status_code == 409


def test_cannot_approve_rejected_item() -> None:
    # RV-1034 is rejected in seed data
    with pytest.raises(HTTPException) as exc:
        run_async(apply_action("RV-1034", ActionRequest(action="approve")))
    assert exc.value.status_code == 409
