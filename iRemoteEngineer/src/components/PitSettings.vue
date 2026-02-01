<template>
  <div class="settings-panel">
    <Card class="pit-settings-card">
      <template #title>
        <div class="card-header">
          <div class="card-header-left">
            <i class="pi pi-wrench"></i>
            <span>Pit Stop Settings</span>
          </div>
          <Button
            :icon="showCommandPreview ? 'pi pi-eye' : 'pi pi-eye-slash'"
            @click="showCommandPreview = !showCommandPreview"
            size="small"
            severity="secondary"
            :label="showCommandPreview ? 'Hide Preview' : 'Show Preview'"
            class="preview-toggle-btn"
          />
        </div>
      </template>
      <template #content>
        <div class="compact-grid">
          <!-- Fuel Row -->
          <div class="grid-item fuel-item">
            <span class="item-label"><i class="pi pi-bolt"></i> Fuel</span>
            <div class="item-controls">
              <InputNumber
                id="fuel"
                v-model="fuelAmount"
                :disabled="!isRefueling"
                mode="decimal"
                showButtons
                :step="1"
                :min="1"
                :max="200"
                :suffix="' ' + getFuelUnit()"
                class="fuel-input-compact"
              />
              <Button
                :label="isRefueling ? 'On' : 'Off'"
                :icon="isRefueling ? 'pi pi-check' : 'pi pi-times'"
                :class="isRefueling ? 'p-button-success p-button-sm' : 'p-button-secondary p-button-sm'"
                @click="toggleRefueling"
              />
            </div>
          </div>

          <!-- Tyres Row -->
          <div class="grid-item tyres-item">
            <span class="item-label"><i class="pi pi-circle"></i> Tyres</span>
            <div class="item-controls tyre-controls">
              <Button
                label="FL"
                :class="tyreStatus.frontLeft ? 'p-button-info p-button-sm tyre-btn' : 'p-button-outlined p-button-sm tyre-btn'"
                @click="toggleTyre('frontLeft')"
              />
              <Button
                label="FR"
                :class="tyreStatus.frontRight ? 'p-button-info p-button-sm tyre-btn' : 'p-button-outlined p-button-sm tyre-btn'"
                @click="toggleTyre('frontRight')"
              />
              <Button
                label="RL"
                :class="tyreStatus.rearLeft ? 'p-button-info p-button-sm tyre-btn' : 'p-button-outlined p-button-sm tyre-btn'"
                @click="toggleTyre('rearLeft')"
              />
              <Button
                label="RR"
                :class="tyreStatus.rearRight ? 'p-button-info p-button-sm tyre-btn' : 'p-button-outlined p-button-sm tyre-btn'"
                @click="toggleTyre('rearRight')"
              />
              <Button
                label="All"
                icon="pi pi-sync"
                class="p-button-secondary p-button-sm"
                @click="toggleAllTyres"
              />
              <Button
                :label="isWetTyres ? 'Wet' : 'Dry'"
                :class="isWetTyres ? 'p-button-info p-button-sm' : 'p-button-secondary p-button-sm'"
                @click="toggleTyreType"
              />
            </div>
          </div>

          <!-- Fast Repair Row -->
          <div class="grid-item">
            <span class="item-label"><i class="pi pi-cog"></i> Fast Repair</span>
            <div class="item-controls">
              <Button
                :label="fastRepair ? 'Yes' : 'No'"
                :icon="fastRepair ? 'pi pi-check' : 'pi pi-times'"
                :class="fastRepair ? 'p-button-warning p-button-sm' : 'p-button-outlined p-button-sm'"
                @click="toggleFastRepair"
              />
            </div>
          </div>

          <!-- Windshield Row -->
          <div class="grid-item">
            <span class="item-label"><i class="pi pi-tablet"></i> Tearoff</span>
            <div class="item-controls">
              <Button
                :label="windshieldWiper ? 'Yes' : 'No'"
                :icon="windshieldWiper ? 'pi pi-check' : 'pi pi-times'"
                :class="windshieldWiper ? 'p-button-warning p-button-sm' : 'p-button-outlined p-button-sm'"
                @click="toggleWindshieldWiper"
              />
            </div>
          </div>
        </div>

        <!-- Command Preview Box -->
        <div v-if="showCommandPreview" class="command-preview">
          <div class="preview-content">
            <code>{{ currentCommand }}</code>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <Button
            label="Clear"
            icon="pi pi-refresh"
            class="p-button-outlined p-button-danger p-button-sm"
            @click="clearSettings"
          />
          <Button
            label="Send"
            icon="pi pi-send"
            class="p-button-success p-button-sm send-btn"
            @click="createCommand"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import useRaceData from '@/composables/useRaceData'
import { useUnits } from '@/composables/useUnits'

const props = defineProps({
  socket: {
    type: Object,
    required: true
  },
  authToken: {
    type: String,
    required: true
  }
})

const { sendCommand } = useRaceData(props.socket, props.authToken)
const { getFuelUnit, getFuelCommandSuffix } = useUnits()

// Load saved preference from localStorage
const loadShowCommandPreview = () => {
  const saved = localStorage.getItem('pitSettingsShowCommandPreview')
  return saved !== null ? saved === 'true' : false
}

// Command Preview
const showCommandPreview = ref(loadShowCommandPreview())

// Save preference to localStorage whenever it changes
watch(showCommandPreview, (value) => {
  localStorage.setItem('pitSettingsShowCommandPreview', value ? 'true' : 'false')
})

// Fuel
const fuelAmount = ref(10)
const isRefueling = ref(true)

// Tyres
const tyreStatus = ref({
  frontLeft: false,
  frontRight: false,
  rearLeft: false,
  rearRight: false,
})
const isWetTyres = ref(false)

// Fast Repair
const fastRepair = ref(false)

// Windshield Wiper
const windshieldWiper = ref(false)

// Computed property for current command preview
const currentCommand = computed(() => {
  let command = []

  // Tyres
  Object.entries(tyreStatus.value).forEach(([key, value]) => {
    const shortKey = {
      frontLeft: 'lf',
      frontRight: 'rf',
      rearLeft: 'lr',
      rearRight: 'rr'
    }[key]
    if (value) {
      command.push(shortKey)
    }
  })

  // Tyre type
  command.push(isWetTyres.value ? 'tc.2' : 'tc.1')

  // Fuel
  if (!isRefueling.value) {
    command.push('clear_fuel')
  } else {
    command.push(`fuel.${Math.floor(fuelAmount.value)}${getFuelCommandSuffix()}`)
  }

  // Fast Repair
  command.push(fastRepair.value ? 'fr' : 'clear_fr')

  // Windshield Wiper
  command.push(windshieldWiper.value ? 'ws' : 'clear_ws')

  return command.join(' ')
})

// Toggle Functions
const toggleRefueling = () => {
  isRefueling.value = !isRefueling.value
}

const toggleTyre = (position) => {
  tyreStatus.value[position] = !tyreStatus.value[position]
}

const toggleAllTyres = () => {
  const newStatus = !areAllTyresSelected()
  for (let key in tyreStatus.value) {
    tyreStatus.value[key] = newStatus
  }
}

const areAllTyresSelected = () => {
  return Object.values(tyreStatus.value).every(status => status)
}

const toggleFastRepair = () => {
  fastRepair.value = !fastRepair.value
}

const toggleWindshieldWiper = () => {
  windshieldWiper.value = !windshieldWiper.value
}

const toggleTyreType = () => {
  isWetTyres.value = !isWetTyres.value
}

// Reset all
const clearSettings = () => {
  fuelAmount.value = 10
  isRefueling.value = false
  for (let key in tyreStatus.value) {
    tyreStatus.value[key] = false
  }
  fastRepair.value = false
  windshieldWiper.value = false
  isWetTyres.value = false
}

// Generate and send command
const createCommand = () => {
  let command = []

  // Tyres
  Object.entries(tyreStatus.value).forEach(([key, value]) => {
    const shortKey = {
      frontLeft: 'lf',
      frontRight: 'rf',
      rearLeft: 'lr',
      rearRight: 'rr'
    }[key]
    if (value) {
      command.push(shortKey)
    }
  })

  // // Tyre type
  command.push(isWetTyres.value ? 'tc.2' : 'tc.1') //to solve later

  // Fuel
  if (!isRefueling.value) {
    command.push('clear_fuel')
  } else {
    command.push(`fuel.${Math.floor(fuelAmount.value)}${getFuelCommandSuffix()}`)
  }

  // Fast Repair
  command.push(fastRepair.value ? 'fr' : 'clear_fr')
  
  // Windshield Wiper
  command.push(windshieldWiper.value ? 'ws' : 'clear_ws')

  const finalCommand = command.join(' ')
  console.log('Command sent:', finalCommand)
  sendCommand(finalCommand)
}
</script>

<style scoped>
.settings-panel {
  width: 100%;
  height: 100%;
  padding: 0;
}

.pit-settings-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.dark-mode .pit-settings-card {
  background: linear-gradient(135deg, #4a5f9d 0%, #5a3a7a 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.pit-settings-card :deep(.p-card-body) {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0;
}

.pit-settings-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 16px 16px 0 0;
  margin: 0;
}

.dark-mode .pit-settings-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #4a5f9d 0%, #5a3a7a 100%);
}

.pit-settings-card :deep(.p-card-content) {
  padding: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-header i {
  font-size: 1.25rem;
}

.preview-toggle-btn {
  flex-shrink: 0;
}

/* Compact Grid Layout */
.compact-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.grid-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 8px;
  gap: 0.75rem;
}

.item-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-primary, #2c3e50);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.item-label i {
  color: #667eea;
  font-size: 0.9rem;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.tyre-controls {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.fuel-input-compact {
  width: 100px;
}

.fuel-input-compact :deep(.p-inputnumber-input) {
  width: 60px;
  padding: 0.3rem 0.5rem;
  font-size: 0.85rem;
}

.tyre-btn {
  min-width: 36px;
  padding: 0.3rem 0.5rem !important;
}

/* Command Preview */
.command-preview {
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 6px;
  padding: 0.5rem;
  margin-bottom: 0.75rem;
}

.preview-content {
  background: #2c3e50;
  border-radius: 4px;
  padding: 0.4rem 0.6rem;
  overflow-x: auto;
}

.preview-content code {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: #4ade80;
  font-weight: 600;
  white-space: nowrap;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color, #e9ecef);
}

.action-buttons button {
  flex: 1;
  font-weight: 600;
}

.send-btn {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .grid-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .item-controls {
    width: 100%;
    flex-wrap: wrap;
  }

  .tyre-controls {
    justify-content: flex-start;
  }

  .fuel-input-compact {
    width: 100%;
  }

  .fuel-input-compact :deep(.p-inputnumber-input) {
    width: 100%;
  }
}

/* PrimeVue Button Overrides */
:deep(.p-button) {
  border-radius: 6px;
}

:deep(.p-inputnumber-input) {
  border-radius: 6px;
  font-weight: 600;
}

/* Dark mode overrides */
.dark-mode .grid-item {
  background: var(--filter-content-bg);
}

.dark-mode .action-buttons {
  border-top-color: var(--border-color);
}
</style>