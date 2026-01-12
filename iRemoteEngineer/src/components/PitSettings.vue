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
        <div class="settings-grid">
          <!-- Fuel Section -->
          <div class="section fuel-section">
            <div class="section-header">
              <i class="pi pi-bolt"></i>
              <h4>Fuel</h4>
            </div>
            <div class="section-content">
              <div class="fuel-controls">
                <div class="fuel-input-group">
                  <label for="fuel">Amount</label>
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
                    class="fuel-input"
                  />
                </div>
                <Button
                  :label="isRefueling ? 'Refueling' : 'Not Refueling'"
                  :icon="isRefueling ? 'pi pi-check' : 'pi pi-times'"
                  :class="isRefueling ? 'p-button-success toggle-btn' : 'p-button-secondary toggle-btn'"
                  @click="toggleRefueling"
                />
              </div>
            </div>
          </div>

          <!-- Tyres Section -->
          <div class="section tyres-section">
            <div class="section-header">
              <i class="pi pi-circle"></i>
              <h4>Tyres</h4>
            </div>
            <div class="section-content">
              <div class="tyre-grid">
                <Button
                  label="FL"
                  :icon="tyreStatus.frontLeft ? 'pi pi-check' : ''"
                  :class="tyreStatus.frontLeft ? 'p-button-info tyre-btn active' : 'p-button-outlined tyre-btn'"
                  @click="toggleTyre('frontLeft')"
                />
                <Button
                  label="FR"
                  :icon="tyreStatus.frontRight ? 'pi pi-check' : ''"
                  :class="tyreStatus.frontRight ? 'p-button-info tyre-btn active' : 'p-button-outlined tyre-btn'"
                  @click="toggleTyre('frontRight')"
                />
                <Button
                  label="RL"
                  :icon="tyreStatus.rearLeft ? 'pi pi-check' : ''"
                  :class="tyreStatus.rearLeft ? 'p-button-info tyre-btn active' : 'p-button-outlined tyre-btn'"
                  @click="toggleTyre('rearLeft')"
                />
                <Button
                  label="RR"
                  :icon="tyreStatus.rearRight ? 'pi pi-check' : ''"
                  :class="tyreStatus.rearRight ? 'p-button-info tyre-btn active' : 'p-button-outlined tyre-btn'"
                  @click="toggleTyre('rearRight')"
                />
              </div>
              <div class="tyre-options">
                <Button
                  label="All Tyres"
                  icon="pi pi-sync"
                  class="p-button-secondary p-button-sm"
                  @click="toggleAllTyres"
                />
                <Button
                  :label="isWetTyres ? 'Wet' : 'Dry'"
                  :icon="isWetTyres ? 'pi pi-cloud' : 'pi pi-sun'"
                  :class="isWetTyres ? 'p-button-info p-button-sm' : 'p-button-secondary p-button-sm'"
                  @click="toggleTyreType"
                />
              </div>
            </div>
          </div>

          <!-- Fast Repair Section -->
          <div class="section repair-section">
            <div class="section-header">
              <i class="pi pi-cog"></i>
              <h4>Fast Repair</h4>
            </div>
            <div class="section-content">
              <Button
                :label="fastRepair ? 'Using Fast Repair' : 'No Fast Repair'"
                :icon="fastRepair ? 'pi pi-check-circle' : 'pi pi-times-circle'"
                :class="fastRepair ? 'p-button-warning toggle-btn' : 'p-button-outlined toggle-btn'"
                @click="toggleFastRepair"
              />
            </div>
          </div>

          <!-- Windshield Tearoff Section -->
          <div class="section windshield-section">
            <div class="section-header">
              <i class="pi pi-tablet"></i>
              <h4>Windshield Tearoff</h4>
            </div>
            <div class="section-content">
              <Button
                :label="windshieldWiper ? 'Tearoff Windshield' : 'No Tearoff'"
                :icon="windshieldWiper ? 'pi pi-check-circle' : 'pi pi-times-circle'"
                :class="windshieldWiper ? 'p-button-warning toggle-btn' : 'p-button-outlined toggle-btn'"
                @click="toggleWindshieldWiper"
              />
            </div>
          </div>
        </div>

        <!-- Command Preview Box -->
        <div v-if="showCommandPreview" class="command-preview">
          <div class="preview-header">
            <i class="pi pi-code"></i>
            <span>Command Preview</span>
          </div>
          <div class="preview-content">
            <code>{{ currentCommand }}</code>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <Button
            label="Clear All"
            icon="pi pi-refresh"
            class="p-button-outlined p-button-danger clear-btn"
            @click="clearSettings"
          />
          <Button
            label="Send to Pit"
            icon="pi pi-send"
            class="p-button-success send-btn"
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

console.log("pit", props.authToken)
const { sendCommand } = useRaceData(props.socket, props.authToken)
const { convertFuel, getFuelUnit, getFuelCommandSuffix } = useUnits()

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
  max-width: 900px;
  margin: 20px auto;
  padding: 1rem;
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
  padding: 1.5rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-header i {
  font-size: 1.75rem;
}

.preview-toggle-btn {
  flex-shrink: 0;
}

/* Command Preview */
.command-preview {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border: 2px solid #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-header i {
  font-size: 1rem;
}

.preview-content {
  background: #2c3e50;
  border-radius: 8px;
  padding: 0.875rem 1rem;
  overflow-x: auto;
}

.preview-content code {
  font-family: 'Courier New', monospace;
  font-size: 0.95rem;
  color: #4ade80;
  font-weight: 600;
  white-space: nowrap;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.section:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e9ecef;
}

.section-header i {
  color: #667eea;
  font-size: 1.25rem;
}

.section-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Fuel Section */
.fuel-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fuel-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.fuel-input-group label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.fuel-input {
  width: 100%;
}

/* Tyres Section */
.tyre-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.tyre-btn {
  font-weight: 600;
  transition: all 0.2s ease;
  min-height: 3rem;
}

.tyre-btn:hover {
  transform: scale(1.05);
}

.tyre-btn.active {
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}

.tyre-options {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tyre-options button {
  flex: 1;
}

/* Toggle Buttons */
.toggle-btn {
  width: 100%;
  font-weight: 600;
  justify-content: center;
  transition: all 0.2s ease;
  min-height: 2.75rem;
}

.toggle-btn:hover {
  transform: scale(1.02);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 2px solid #e9ecef;
}

.action-buttons button {
  flex: 1;
  font-weight: 600;
  font-size: 1.1rem;
  padding: 0.875rem;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.send-btn {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border: none;
}

.send-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
  background: linear-gradient(135deg, #218838 0%, #1aa179 100%);
}

/* Responsive Design */
@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .tyre-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* PrimeVue Button Overrides */
:deep(.p-button) {
  border-radius: 8px;
}

:deep(.p-inputnumber) {
  width: 100%;
}

:deep(.p-inputnumber-input) {
  border-radius: 8px;
  font-weight: 600;
}

/* Dark mode overrides */
.dark-mode .section {
  background: var(--card-bg);
  border-color: var(--border-color);
}

.dark-mode .section:hover {
  border-color: #667eea;
}

.dark-mode .section-header {
  border-bottom-color: var(--border-color);
}

.dark-mode .section-header h4 {
  color: var(--text-primary);
}

.dark-mode .fuel-input-group label {
  color: var(--text-secondary);
}

.dark-mode .command-preview {
  background: var(--filter-content-bg);
  border-color: var(--border-color);
}

.dark-mode .action-buttons {
  border-top-color: var(--border-color);
}
</style>