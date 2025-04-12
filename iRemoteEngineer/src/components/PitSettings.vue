<template>
  <div class="settings-panel">
    <Card>
      <template #title>Pit Stop Settings</template>
      <template #content>
        <!-- Fuel Section -->
        <div class="section">
          <h4>Fuel</h4>
          <div class="p-field">
            <label for="fuel">Amount (liters)</label>
            <InputNumber
              id="fuel"
              v-model="fuelAmount"
              :disabled="!isRefueling"
              mode="decimal"
              showButtons
              :step="1"
              :min="1"
              :max="200"
              suffix=" L"
            />
          </div>
          <div class="p-field">
            <Button
              :label="isRefueling ? 'Refueling' : 'Not Refueling'"
              :class="isRefueling ? 'p-button-success' : 'p-button-secondary'"
              @click="toggleRefueling"
            />
          </div>
        </div>

        <!-- Tyres Section -->
        <div class="section">
          <h4>Tyres</h4>
          <div class="tyre-buttons">
            <Button
              label="Front Left"
              :class="tyreStatus.frontLeft ? 'p-button-info' : 'p-button-outlined'"
              @click="toggleTyre('frontLeft')"
            />
            <Button
              label="Front Right"
              :class="tyreStatus.frontRight ? 'p-button-info' : 'p-button-outlined'"
              @click="toggleTyre('frontRight')"
            />
            <Button
              label="Rear Left"
              :class="tyreStatus.rearLeft ? 'p-button-info' : 'p-button-outlined'"
              @click="toggleTyre('rearLeft')"
            />
            <Button
              label="Rear Right"
              :class="tyreStatus.rearRight ? 'p-button-info' : 'p-button-outlined'"
              @click="toggleTyre('rearRight')"
            />
          </div>
          <div class="p-field">
            <Button
              label="Toggle All Tyres"
              class="p-button-secondary"
              @click="toggleAllTyres"
            />
          </div>
          <div class="p-field">
            <Button
              :label="isWetTyres ? 'Wet Tyres' : 'Dry Tyres'"
              :class="isWetTyres ? 'p-button-info' : 'p-button-secondary'"
              @click="toggleTyreType"
            />
          </div>
        </div>

        <!-- Fast Repair Section -->
        <div class="section">
          <h4>Fast Repair</h4>
          <Button
            :label="fastRepair ? 'Using Fast Repair' : 'No Fast Repair'"
            :class="fastRepair ? 'p-button-warning' : 'p-button-outlined'"
            @click="toggleFastRepair"
          />
        </div>

        <!-- Clear + Send Buttons -->
        <div class="section" style="display: flex; gap: 10px; flex-wrap: wrap;">
          <Button
            label="Clear All Settings"
            class="p-button-outlined p-button-danger"
            @click="clearSettings"
          />
          <Button
            label="Send Command"
            class="p-button-success"
            @click="createCommand"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import useRaceData from '@/composables/useRaceData'

const { sendCommand } = useRaceData()

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

const toggleTyreType = () => {
  isWetTyres.value = !isWetTyres.value
}

// Reset all
const clearSettings = () => {
  fuelAmount.value = 10
  isRefueling.value = true
  for (let key in tyreStatus.value) {
    tyreStatus.value[key] = false
  }
  fastRepair.value = false
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
  // command.push(isWetTyres.value ? 'tc.2' : 'tc.1') to solve later

  // Fuel
  if (!isRefueling.value) {
    command.push('clear_fuel')
  } else {
    command.push(`fuel.${Math.floor(fuelAmount.value)}`)
  }

  // Fast Repair
  command.push(fastRepair.value ? 'fr' : 'clear_fr')

  const finalCommand = command.join(' ')
  console.log('Command sent:', finalCommand)
  sendCommand(finalCommand)
}
</script>

<style scoped>
.settings-panel {
  max-width: 600px;
  margin: 20px auto;
  padding: 1rem;
}

.section {
  margin-bottom: 1.5rem;
}

.p-field {
  margin-bottom: 1rem;
}

.tyre-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
