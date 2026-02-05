<template>
  <div class="fuel-container">
    <Card class="fuel-card">
      <template #title>
        <div class="card-header">
          <div class="card-header-left">
            <i class="pi pi-bolt"></i>
            <span>Fuel Analysis</span>
          </div>
          <Button
            :icon="displayMode === 'base' ? 'pi pi-eye' : 'pi pi-eye-slash'"
            @click="toggleDisplayMode"
            size="small"
            severity="secondary"
            :label="displayMode === 'base' ? 'Detailed' : 'Base'"
            class="view-toggle-btn"
          />
        </div>
      </template>
      <template #content>
        <!-- Base mode: horizontal stats row -->
        <div v-if="displayMode === 'base'" class="summary-row">
          <div class="summary-item compact">
            <div class="summary-label">
              <i class="pi pi-gauge"></i>
              Remaining
            </div>
            <div :class="['summary-value', { 'fuel-critical': fuelData.current_fuel_level < avgBurn }]">
              {{ formatFuelValue(fuelData.current_fuel_level) }}
            </div>
          </div>
          <div class="summary-item compact">
            <div class="summary-label">
              <i class="pi pi-calculator"></i>
              Avg Burn
            </div>
            <div class="summary-value">
              {{ formatFuelValue(avgBurn) }}
            </div>
          </div>
          <div class="summary-item compact">
            <div class="summary-label">
              <i class="pi pi-map"></i>
              Estimated Laps
            </div>
            <div class="summary-value">
              {{ lapsLeftEstimate }}
            </div>
          </div>
        </div>

        <!-- Detailed mode: vertical stats + chart -->
        <div v-if="displayMode === 'detailed'" class="summary-grid">
          <div class="summary-column">
            <div class="summary-item compact">
              <div class="summary-label">
                <i class="pi pi-gauge"></i>
                Remaining
              </div>
              <div :class="['summary-value', { 'fuel-critical': fuelData.current_fuel_level < avgBurn }]">
                {{ formatFuelValue(fuelData.current_fuel_level) }}
              </div>
            </div>
            <div class="summary-item compact">
              <div class="summary-label">
                <i class="pi pi-calculator"></i>
                Avg Burn
              </div>
              <div class="summary-value">
                {{ formatFuelValue(avgBurn) }}
              </div>
            </div>
            <div class="summary-item compact">
              <div class="summary-label">
                <i class="pi pi-map"></i>
                Estimated Laps
              </div>
              <div class="summary-value">
                {{ lapsLeftEstimate }}
              </div>
            </div>
          </div>
          <div class="summary-item history-item">
            <div class="summary-label">
              <i class="pi pi-chart-bar"></i>
              Recent Consumption
            </div>
            <div class="burn-chart" v-if="burnChartData.length > 0">
              <div class="chart-bars">
                <div
                  v-for="(bar, index) in burnChartData"
                  :key="index"
                  class="chart-bar-container"
                >
                  <div class="bar-value">{{ bar.displayValue }}</div>
                  <div class="bar-wrapper">
                    <div
                      class="bar"
                      :style="{ height: bar.height + '%' }"
                      :class="{ 'bar-high': bar.isHigh, 'bar-low': bar.isLow }"
                    ></div>
                  </div>
                  <div class="bar-label">{{ bar.label }}</div>
                </div>
              </div>
            </div>
            <div v-else class="summary-value">No data</div>
          </div>
        </div>

        <!-- Lap-Fuel Consumption Table -->
        <DataTable :value="lapFuelPairs" stripedRows :scrollable="false" class="fuel-table">
          <Column header="Laps">
            <template #body="slotProps">
              <span class="laps-value">{{ slotProps.data.laps }}</span>
            </template>
            <template #footer>
              <input
                type="text"
                inputmode="decimal"
                class="calc-input"
                :value="calcLaps"
                @input="onCalcLapsInput"
                placeholder="Laps"
              />
            </template>
          </Column>
          <Column header="Target Fuel">
            <template #body="slotProps">
              <span class="fuel-target">{{ formatFuelValue(slotProps.data.target) }}</span>
            </template>
            <template #footer>
              <input
                type="text"
                inputmode="decimal"
                class="calc-input"
                :value="calcFuel"
                @input="onCalcFuelInput"
                :placeholder="'Fuel (' + getFuelUnit() + ')'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import useRaceData from '@/composables/useRaceData';
import { useUnits } from '@/composables/useUnits';

const props = defineProps({
  socket: {
    type: Object,
    required: true
  }
})

// Load saved preferences from localStorage
const loadDisplayMode = () => {
  const saved = localStorage.getItem('fuelAnalysisDisplayMode')
  return saved !== null ? saved : 'base'
}

const displayMode = ref(loadDisplayMode()); // 'base' or 'detailed'
const { data } = useRaceData(props.socket);
const { convertFuel, getFuelUnit, useGallons } = useUnits();

// Save preferences to localStorage whenever they change
watch(displayMode, (value) => {
  localStorage.setItem('fuelAnalysisDisplayMode', value)
})

const toggleDisplayMode = () => {
  displayMode.value = displayMode.value === 'base' ? 'detailed' : 'base';
};

const fuelData = computed(() => {
    return data.value?.fuel || {
        current_fuel_level: -1.0,
        burn_history: [],
    };
});

const avgBurn = computed(() => {
  const history = fuelData.value.burn_history;
  if (!Array.isArray(history) || history.length === 0) return -1;
  return history.reduce((sum, v) => sum + v, 0) / history.length;
});

const lapsLeftEstimate = computed(() => {
  const burn = avgBurn.value;
  const fuel = fuelData.value.current_fuel_level;
  if (burn > 0 && fuel >= 0) {
    return (fuel / burn).toFixed(2);
  }
  return '-';
});

const lapFuelPairs = computed(() => {
  const burn = avgBurn.value;
  const fuel = fuelData.value.current_fuel_level;
  if (burn <= 0 || fuel < 0) return [];

  const exactLaps = fuel / burn;
  const floorLaps = Math.floor(exactLaps);
  const ceilLaps = Math.ceil(exactLaps);
  const oneLapMore = ceilLaps + 1;

  const entries = new Map();
  const add = (laps) => {
    if (!entries.has(laps) && laps > 0) {
      entries.set(laps, { laps, target: fuel / laps });
    }
  };

  add(floorLaps);
  add(ceilLaps);
  add(oneLapMore);

  return Array.from(entries.values()).sort((a, b) => a.laps - b.laps);
});

// Calculator
const calcLaps = ref(null);
const calcFuel = ref(null);

const sanitizeNumericInput = (event) => {
  const raw = event.target.value.replace(',', '.');
  const cleaned = raw.replace(/[^0-9.]/g, '');
  if (raw !== event.target.value) {
    event.target.value = cleaned;
  }
  return parseFloat(cleaned);
};

const onCalcLapsInput = (event) => {
  const val = sanitizeNumericInput(event);
  calcLaps.value = isNaN(val) ? null : val;
  const fuel = fuelData.value.current_fuel_level;
  if (calcLaps.value != null && calcLaps.value > 0 && fuel > 0) {
    calcFuel.value = parseFloat(convertFuel(fuel / calcLaps.value).toFixed(2));
  } else {
    calcFuel.value = null;
  }
};

const onCalcFuelInput = (event) => {
  const val = sanitizeNumericInput(event);
  calcFuel.value = isNaN(val) ? null : val;
  const fuel = fuelData.value.current_fuel_level;
  if (calcFuel.value != null && calcFuel.value > 0 && fuel > 0) {
    const burnInLiters = useGallons.value ? calcFuel.value / 0.264172 : calcFuel.value;
    calcLaps.value = parseFloat((fuel / burnInLiters).toFixed(2));
  } else {
    calcLaps.value = null;
  }
};

const formatFuelValue = (value) => {
  return typeof value === 'number'
    ? `${convertFuel(value).toFixed(2)}${getFuelUnit()}`
    : value;
};

const burnChartData = computed(() => {
  const history = fuelData.value.burn_history;
  if (!Array.isArray(history) || history.length === 0) return [];

  const convertedValues = history.map(v => convertFuel(v));
  const minVal = Math.min(...convertedValues);
  const maxVal = Math.max(...convertedValues);
  const range = maxVal - minVal || 1;

  return convertedValues.map((value, index) => {
    const heightPercent = ((value - minVal) / range) * 70 + 30;
    return {
      value,
      displayValue: value.toFixed(2),
      height: heightPercent,
      label: `-${index + 1}`,
      isHigh: value === maxVal && convertedValues.length > 1,
      isLow: value === minVal && convertedValues.length > 1
    };
  });
});
</script>

<style scoped>
.fuel-container {
  width: 100%;
  height: 100%;
  padding: 0;
}

.fuel-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.dark-mode .fuel-card {
  background: linear-gradient(135deg, #a06ba8 0%, #a84050 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.fuel-card :deep(.p-card-body) {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0;
}

.fuel-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 1rem;
  border-radius: 16px 16px 0 0;
  margin: 0;
}

.dark-mode .fuel-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #a06ba8 0%, #a84050 100%);
}

.fuel-card :deep(.p-card-content) {
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

.view-toggle-btn {
  flex-shrink: 0;
}

.summary-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.summary-row > .summary-item {
  flex: 1;
}

.summary-grid {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.summary-column {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 120px;
  flex: 1;
}

.summary-item {
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  flex: 1;
}

.summary-item.compact {
  padding: 0.4rem 0.6rem;
}

.summary-item.history-item {
  flex: 2;
  display: flex;
  flex-direction: column;
}

.burn-chart {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.chart-bars {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  height: 65px;
}

.chart-bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}

.bar-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
  font-family: monospace;
  margin-bottom: 2px;
  white-space: nowrap;
}

.bar-wrapper {
  width: 100%;
  height: 45px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 100%;
  max-width: 36px;
  background: linear-gradient(180deg, #f5576c 0%, #f093fb 100%);
  border-radius: 2px 2px 0 0;
  transition: height 0.3s ease;
}

.bar.bar-high {
  background: linear-gradient(180deg, #dc3545 0%, #f5576c 100%);
}

.bar.bar-low {
  background: linear-gradient(180deg, #28a745 0%, #5cb85c 100%);
}

.bar-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6c757d;
  margin-top: 2px;
}

.summary-label {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.summary-label i {
  color: #f5576c;
  font-size: 0.95rem;
}

.summary-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary, #2c3e50);
  font-family: monospace;
}

.fuel-critical {
  color: #dc3545;
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.fuel-table {
  border-radius: 8px;
  overflow: hidden;
}

.laps-value {
  font-weight: 600;
  font-size: 0.9rem;
  color: #2c3e50;
}

.dark-mode .laps-value {
  color: var(--text-primary);
}

.fuel-target {
  font-family: monospace;
  font-weight: 600;
  font-size: 0.9rem;
  color: #28a745;
}

:deep(.p-datatable) {
  font-size: 0.85rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #dee2e6;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 0.75rem;
}

.calc-input {
  width: 100%;
  padding: 0.35rem 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85rem;
  font-weight: 600;
  background: var(--card-bg, #fff);
  color: var(--text-primary, #2c3e50);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.calc-input:focus {
  border-color: #f5576c;
  box-shadow: 0 0 0 2px rgba(245, 87, 108, 0.15);
}

.calc-input::placeholder {
  color: #adb5bd;
  font-weight: 400;
}

:deep(.p-datatable .p-datatable-tfoot > tr > td) {
  padding: 0.5rem 0.75rem;
  background: var(--card-bg, #fff);
  border-top: 1px dashed #dee2e6;
}

:deep(.p-button) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .summary-row {
    flex-direction: column;
  }

  .summary-grid {
    flex-direction: column;
  }

}

/* Dark mode overrides */
.dark-mode .summary-row,
.dark-mode .summary-grid {
  background: var(--filter-content-bg);
  color: var(--text-primary);
}

.dark-mode .fuel-table :deep(.p-datatable-thead > tr > th) {
  background: var(--table-header-bg-start) !important;
  color: var(--table-header-text) !important;
  border-bottom-color: var(--table-border) !important;
}

.dark-mode .summary-item {
  background: var(--card-bg);
  border-color: var(--border-color);
}

.dark-mode .calc-input {
  background: var(--card-bg);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.dark-mode .fuel-table :deep(.p-datatable-tfoot > tr > td) {
  background: var(--card-bg);
  border-top-color: var(--border-color);
}

.dark-mode .summary-label,
.dark-mode .summary-value,
.dark-mode .fuel-target {
  color: var(--text-primary);
}

</style>
