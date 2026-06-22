<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  applyReviewAction,
  fetchReviewItems,
  type ReviewAction,
  type ReviewItem,
  type ReviewStatus
} from "./api";

const currentReviewer = "alex";
const items = ref<ReviewItem[]>([]);
const selectedId = ref<string | null>(null);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const pendingAction = ref<ReviewAction | null>(null);

const TERMINAL_STATUSES = new Set<ReviewStatus>(["approved", "rejected", "escalated"]);

function isTerminal(item: ReviewItem): boolean {
  return TERMINAL_STATUSES.has(item.status);
}

const selectedItem = computed(() =>
  items.value.find((item) => item.id === selectedId.value) ?? items.value[0] ?? null
);

async function loadItems() {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    items.value = await fetchReviewItems();
    selectedId.value = selectedItem.value?.id ?? null;
  } catch {
    errorMessage.value = "Something went wrong loading the queue.";
  } finally {
    isLoading.value = false;
  }
}

async function performAction(action: ReviewAction) {
  if (!selectedItem.value) return;

  pendingAction.value = action;
  errorMessage.value = null;

  try {
    const updated = await applyReviewAction(selectedItem.value.id, action, currentReviewer);
    if (isTerminal(updated)) {
      items.value = items.value.filter((item) => item.id !== updated.id);
      selectedId.value = items.value[0]?.id ?? null;
    } else {
      items.value = items.value.map((item) => (item.id === updated.id ? updated : item));
    }
  } catch {
    errorMessage.value = "That action could not be completed.";
  } finally {
    pendingAction.value = null;
  }
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

onMounted(loadItems);
</script>

<template>
  <main class="page-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Reviewer workspace</p>
        <h1>Active queue</h1>
      </div>
      <div class="reviewer">Signed in as {{ currentReviewer }}</div>
    </header>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
    <p v-if="isLoading" class="loading">Loading review items...</p>

    <section v-else class="workspace">
      <aside class="queue-list" aria-label="Review queue">
        <p v-if="items.length === 0" class="queue-empty">No active items in the queue.</p>
        <button
          v-for="item in items"
          :key="item.id"
          class="queue-item"
          :class="{ selected: item.id === selectedItem?.id }"
          type="button"
          @click="selectedId = item.id"
        >
          <span class="queue-title">{{ item.title }}</span>
          <div class="queue-badges">
            <span class="risk-badge" :class="`risk-badge--${item.risk_level}`">
              {{ item.risk_level }} risk
            </span>
            <span
              class="tier-badge"
              :class="{ 'tier-badge--priority': item.customer_tier === 'priority' }"
            >
              {{ item.customer_tier }}
            </span>
          </div>
          <span class="queue-meta">
            {{ item.status.replace("_", " ") }} · {{ item.assigned_reviewer ?? "unassigned" }}
          </span>
        </button>
      </aside>

      <section v-if="selectedItem" class="detail-panel">
        <div class="detail-header">
          <div>
            <p class="eyebrow">{{ selectedItem.id }}</p>
            <h2>{{ selectedItem.title }}</h2>
          </div>
          <span class="status-pill" :class="`status-pill--${selectedItem.status}`">
            {{ selectedItem.status.replace("_", " ") }}
          </span>
        </div>

        <dl class="facts">
          <div>
            <dt>Submitted</dt>
            <dd>{{ formatDate(selectedItem.submitted_at) }}</dd>
          </div>
          <div>
            <dt>Risk</dt>
            <dd>{{ selectedItem.risk_level }}</dd>
          </div>
          <div>
            <dt>Customer tier</dt>
            <dd>{{ selectedItem.customer_tier }}</dd>
          </div>
          <div>
            <dt>Assignee</dt>
            <dd>{{ selectedItem.assigned_reviewer ?? "None" }}</dd>
          </div>
        </dl>

        <p class="summary">{{ selectedItem.summary }}</p>
        <p class="notes">{{ selectedItem.notes_count }} notes on this item</p>

        <div class="actions" aria-label="Workflow actions">
          <template v-if="selectedItem.status === 'unassigned'">
            <button
              type="button"
              :disabled="Boolean(pendingAction)"
              @click="performAction('claim')"
            >
              Claim
            </button>
          </template>

          <template v-else-if="selectedItem.status === 'in_review'">
            <button
              type="button"
              :disabled="Boolean(pendingAction)"
              @click="performAction('approve')"
            >
              Approve
            </button>
            <button
              type="button"
              :disabled="Boolean(pendingAction)"
              @click="performAction('reject')"
            >
              Reject
            </button>
            <button
              type="button"
              :disabled="Boolean(pendingAction)"
              @click="performAction('escalate')"
            >
              Escalate
            </button>
          </template>

          <p v-else class="terminal-notice">
            This item is closed — no further actions available.
          </p>
        </div>
      </section>

      <section v-else class="detail-panel detail-panel--empty">
        <p>Select an item from the queue to review it.</p>
      </section>
    </section>
  </main>
</template>
