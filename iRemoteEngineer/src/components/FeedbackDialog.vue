<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    header="Submit Feedback"
    :modal="true"
    :style="{ width: '500px' }"
  >
    <div class="feedback-form">
      <div class="form-field">
        <label for="feedback-type">Type</label>
        <Dropdown
          id="feedback-type"
          v-model="feedbackType"
          :options="typeOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Select type"
          style="width: 100%"
        />
      </div>

      <div class="form-field">
        <label for="feedback-email">Email <span class="optional">(optional)</span></label>
        <InputText
          id="feedback-email"
          v-model="email"
          placeholder="your@email.com"
          style="width: 100%"
        />
      </div>

      <div class="form-field">
        <label for="feedback-topic">Topic</label>
        <InputText
          id="feedback-topic"
          v-model="topic"
          placeholder="Brief summary"
          style="width: 100%"
        />
      </div>

      <div class="form-field">
        <label for="feedback-description">Description</label>
        <Textarea
          id="feedback-description"
          v-model="description"
          placeholder="Describe the bug, feature, or inquiry..."
          rows="5"
          style="width: 100%"
        />
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" severity="secondary" @click="close" />
      <Button label="Submit" icon="pi pi-send" @click="submit" :disabled="!isValid" :loading="submitting" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';

const toast = useToast();

defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:visible']);

const typeOptions = [
  { label: 'Bug Report', value: 'bug_report' },
  { label: 'Feature Request', value: 'feature_request' },
  { label: 'Inquiry', value: 'inquiry' }
];

const feedbackType = ref(null);
const email = ref('');
const topic = ref('');
const description = ref('');

const isValid = computed(() => feedbackType.value && topic.value.trim() && description.value.trim());

function resetForm() {
  feedbackType.value = null;
  email.value = '';
  topic.value = '';
  description.value = '';
}

function close() {
  emit('update:visible', false);
  resetForm();
}

const submitting = ref(false);

async function submit() {
  if (!isValid.value) return;

  submitting.value = true;
  try {
    const response = await fetch(import.meta.env.VITE_FEEDBACK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: feedbackType.value,
        email: email.value || null,
        title: topic.value,
        description: description.value
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    toast.add({
      severity: 'success',
      summary: 'Feedback Submitted',
      detail: `Issue created: #${data.issue_id}`,
      sticky: true
    });

    close();
  } catch (error) {
    console.error('Error submitting feedback:', error);
    toast.add({
      severity: 'error',
      summary: 'Submission Failed',
      detail: 'Could not submit feedback. Please try again.',
      life: 5000
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.feedback-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-field label {
  font-weight: 600;
  font-size: 0.9rem;
}

.optional {
  font-weight: 400;
  color: var(--text-secondary);
  font-size: 0.85rem;
}
</style>
