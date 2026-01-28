<template>
  <div class="engineer-panel-wrapper">
    <!-- Header with controls -->
    <div class="panel-header">
      <Button
        icon="pi pi-arrow-left"
        label="Back to Lobby"
        severity="secondary"
        size="small"
        @click="$emit('back-to-lobby')"
        class="back-button"
      />
      <h2 class="panel-title">Race Engineer Panel</h2>
      <div class="header-buttons">
        <Button
          :icon="showUnitsSettings ? 'pi pi-cog' : 'pi pi-sliders-h'"
          label="Units"
          severity="secondary"
          size="small"
          @click="showUnitsSettings = !showUnitsSettings"
          class="units-toggle"
        />
        <Button
          :icon="isDarkMode ? 'pi pi-sun' : 'pi pi-moon'"
          :label="isDarkMode ? 'Light' : 'Dark'"
          severity="secondary"
          size="small"
          @click="toggleDarkMode"
          class="dark-mode-toggle"
        />
      </div>
    </div>

    <!-- Units Settings Panel -->
    <div v-if="showUnitsSettings" class="units-settings-panel">
      <div class="units-settings-container">
        <h3 class="units-settings-title">Unit Settings</h3>
        <div class="unit-toggles">
          <div class="unit-toggle-item">
            <span class="unit-label">Temperature:</span>
            <div class="toggle-buttons">
              <Button
                label="°C"
                size="small"
                :severity="!useFahrenheit ? 'info' : 'secondary'"
                :outlined="useFahrenheit"
                @click="useFahrenheit && toggleTemp()"
                class="unit-btn"
              />
              <Button
                label="°F"
                size="small"
                :severity="useFahrenheit ? 'info' : 'secondary'"
                :outlined="!useFahrenheit"
                @click="!useFahrenheit && toggleTemp()"
                class="unit-btn"
              />
            </div>
          </div>
          <div class="unit-toggle-item">
            <span class="unit-label">Speed:</span>
            <div class="toggle-buttons">
              <Button
                label="kph"
                size="small"
                :severity="!useMph ? 'info' : 'secondary'"
                :outlined="useMph"
                @click="useMph && toggleSpeed()"
                class="unit-btn"
              />
              <Button
                label="mph"
                size="small"
                :severity="useMph ? 'info' : 'secondary'"
                :outlined="!useMph"
                @click="!useMph && toggleSpeed()"
                class="unit-btn"
              />
            </div>
          </div>
          <div class="unit-toggle-item">
            <span class="unit-label">Fuel:</span>
            <div class="toggle-buttons">
              <Button
                label="Liters"
                size="small"
                :severity="!useGallons ? 'info' : 'secondary'"
                :outlined="useGallons"
                @click="useGallons && toggleFuel()"
                class="unit-btn"
              />
              <Button
                label="Gallons"
                size="small"
                :severity="useGallons ? 'info' : 'secondary'"
                :outlined="!useGallons"
                @click="!useGallons && toggleFuel()"
                class="unit-btn"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Debug info -->
    <div v-if="true" class="debug-info">
      <strong>Debug Info:</strong><br>
      isConnected: {{ isConnected }}<br>
      safeSocket: {{ safeSocket ? 'exists' : 'null' }}<br>
      useMockMode: {{ useMockMode }}<br>
      connectionError: {{ connectionError }}<br>
      lobby_name: {{ lobby_name }}<br>
      auth_token: {{ auth_token }}
    </div>

    <div v-if="isConnected && safeSocket" class="dashboard-container">
      <!-- Main area: Car Tracker takes full width -->
      <div class="dashboard-main">
        <CarTracker :socket="safeSocket" />
      </div>

      <!-- Second row: Fuel Analysis, Pit Settings, Race Events -->
      <div class="dashboard-row">
        <FuelAnalysis :socket="safeSocket" />
        <PitSettings :socket="safeSocket" :authToken="auth_token" />
        <EventTracker :socket="safeSocket" />
      </div>

      <!-- Third row: Lap History, Tyre Details, Weather -->
      <div class="dashboard-row">
        <LapHistory :socket="safeSocket" />
        <TyreDetails :socket="safeSocket" />
        <WeatherInfo :socket="safeSocket" />
      </div>
    </div>
    <div v-else class="loading-container">
      <p>{{ useMockMode ? 'Initializing mock data...' : 'Connecting to race data...' }}</p>
      <p v-if="connectionError" class="error-message">{{ connectionError }}</p>
    </div>
  </div>
</template>

<script setup>
import CarTracker from './CarTracker.vue';
import FuelAnalysis from './FuelAnalysis.vue';
import EventTracker from './EventTracker.vue';
import TyreDetails from './TyreDetails.vue';
import WeatherInfo from './WeatherInfo.vue';
import PitSettings from './PitSettings.vue';
import LapHistory from './LapHistory.vue';
import Button from 'primevue/button';
import useWebSocketConnection from '../composables/createSocket.js';
import { useDarkMode } from '../composables/useDarkMode.js';
import { useUnits } from '../composables/useUnits.js';
import { computed, ref, onMounted, onBeforeUnmount, watch } from 'vue';

const props = defineProps({
  lobby_name: {
    type: String,
    required: true
  },
  auth_token: {
    type: String,
    required: true
  },
  use_mock_mode: {
    type: Boolean,
    default: false
  }
})

defineEmits(['back-to-lobby']);

console.log('EngineerPanel props:', props);

const useMockMode = computed(() => props.use_mock_mode);

const { socket, isConnected, connectionError, connect } = useWebSocketConnection(
  props.lobby_name,
  props.auth_token,
  props.use_mock_mode
);

const { isDarkMode, toggleDarkMode } = useDarkMode();
const { useFahrenheit, useMph, useGallons, toggleTemp, toggleSpeed, toggleFuel } = useUnits();
const showUnitsSettings = ref(false);

const safeSocket = computed(() => isConnected.value ? socket.value : null);

// Watch for connection changes
watch(isConnected, (newVal) => {
  console.log('isConnected changed to:', newVal);
});

watch(safeSocket, (newVal) => {
  console.log('safeSocket changed to:', newVal);
});

// Attempt to reconnect if connection fails (only in non-mock mode)
const reconnectInterval = ref(null);

onMounted(() => {
  console.log('EngineerPanel mounted');
  if (!props.use_mock_mode) {
    reconnectInterval.value = setInterval(() => {
      if (!isConnected.value) {
        console.log('Attempting to reconnect...');
        connect();
      }
    }, 5000); // Try reconnecting every 5 seconds
  }
});

onBeforeUnmount(() => {
  console.log('EngineerPanel unmounting');
  if (reconnectInterval.value) {
    clearInterval(reconnectInterval.value);
  }
});
</script>

<style scoped>
.engineer-panel-wrapper {
  min-height: 100vh;
  background: var(--color-background);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--card-bg);
  border-bottom: 2px solid var(--border-color);
  box-shadow: 0 2px 8px var(--card-shadow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.panel-title {
  color: var(--text-primary);
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.back-button {
  flex-shrink: 0;
}

.header-buttons {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.units-toggle,
.dark-mode-toggle {
  flex-shrink: 0;
}

.units-settings-panel {
  background: var(--card-bg);
  border-bottom: 2px solid var(--border-color);
  box-shadow: 0 2px 8px var(--card-shadow);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.units-settings-container {
  padding: 1.5rem 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.units-settings-title {
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.unit-toggles {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.unit-toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: var(--color-background);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.unit-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
  min-width: 120px;
}

.toggle-buttons {
  display: flex;
  gap: 0.5rem;
}

.unit-btn {
  min-width: 80px;
}

.debug-info {
  background: var(--debug-bg);
  padding: 10px;
  margin: 10px;
  border: 1px solid var(--debug-border);
  color: var(--text-primary);
}

/* Dashboard Grid Layout */
.dashboard-container {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.dashboard-main {
  width: 100%;
}

.dashboard-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

/* Third row: Lap History and Tyre Details get more space, Weather is thinner */
.dashboard-row:last-child {
  grid-template-columns: 1.3fr 1.3fr 0.7fr;
}

/* Make widgets fill their grid cells */
.dashboard-row > :deep(*),
.dashboard-main > :deep(*) {
  margin: 0 !important;
  max-width: none !important;
  width: 100% !important;
}

/* Responsive: 2 columns on medium screens */
@media (max-width: 1400px) {
  .dashboard-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Responsive: 1 column on small screens */
@media (max-width: 900px) {
  .dashboard-row {
    grid-template-columns: 1fr;
  }

}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  gap: 1rem;
  color: var(--text-primary);
}

.error-message {
  color: #d32f2f;
  font-weight: 500;
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
  }

  .panel-title {
    font-size: 1.25rem;
    text-align: center;
  }

  .back-button {
    width: 100%;
  }

  .header-buttons {
    width: 100%;
    flex-direction: row;
  }

  .units-toggle,
  .dark-mode-toggle {
    flex: 1;
  }

  .units-settings-container {
    padding: 1rem;
  }

  .unit-toggle-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .unit-label {
    min-width: auto;
  }

  .toggle-buttons {
    width: 100%;
  }

  .unit-btn {
    flex: 1;
  }
}
</style>