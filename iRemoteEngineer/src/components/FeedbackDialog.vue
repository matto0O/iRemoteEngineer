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
      <Button label="Submit" icon="pi pi-send" @click="submit" :disabled="!isValid" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';

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

function submit() {
  if (!isValid.value) return;

  console.log({
    type: feedbackType.value,
    email: email.value || null,
    topic: topic.value,
    description: description.value
  });

  close();
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
