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
        <!-- Summary Data (Detailed only) -->
        <div v-if="displayMode === 'detailed'" class="summary-grid">
          <div class="summary-column">
            <div class="summary-item compact">
              <div class="summary-label">
                <i class="pi pi-gauge"></i>
                Remaining
              </div>
              <div :class="['summary-value', { 'fuel-critical': fuelData.current_fuel_level < fuelData.average_burn }]">
                {{ formatFuelValue(fuelData.current_fuel_level) }}
              </div>
            </div>
            <div class="summary-item compact">
              <div class="summary-label">
                <i class="pi pi-calculator"></i>
                Avg Burn
              </div>
              <div class="summary-value">
                {{ formatFuelValue(fuelData.average_burn) }}
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

        <!-- View Mode Toggle -->
        <div class="toggle-container">
          <Button
            :label="'Average Consumption'"
            :icon="'pi pi-chart-line'"
            :class="viewMode === 'average' ? 'p-button-info toggle-btn active' : 'p-button-outlined toggle-btn'"
            @click="viewMode = 'average'"
          />
          <Button
            :label="'Last Lap Consumption'"
            :icon="'pi pi-flag'"
            :class="viewMode === 'last' ? 'p-button-info toggle-btn active' : 'p-button-outlined toggle-btn'"
            @click="viewMode = 'last'"
          />
        </div>

        <!-- Lap-Fuel Consumption Table -->
        <DataTable :value="lapFuelPairs" stripedRows class="fuel-table">
          <Column header="Laps">
            <template #body="slotProps">
              <div class="laps-cell">
                <span class="laps-value">{{ slotProps.data.laps }}</span>
                <div class="tooltip-wrapper">
                  <i class="pi pi-info-circle tooltip-icon"></i>
                  <span class="tooltip-text">{{ slotProps.data.tooltip }}</span>
                </div>
              </div>
            </template>
          </Column>
          <Column header="Target Fuel">
            <template #body="slotProps">
              <span class="fuel-target">{{ formatFuelValue(slotProps.data.target) }}</span>
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

const loadViewMode = () => {
  const saved = localStorage.getItem('fuelAnalysisViewMode')
  return saved !== null ? saved : 'average'
}

const displayMode = ref(loadDisplayMode()); // 'base' or 'detailed'
const viewMode = ref(loadViewMode()); // 'average' or 'last'
const { data } = useRaceData(props.socket);
const { convertFuel, getFuelUnit } = useUnits();

// Save preferences to localStorage whenever they change
watch(displayMode, (value) => {
  localStorage.setItem('fuelAnalysisDisplayMode', value)
})

watch(viewMode, (value) => {
  localStorage.setItem('fuelAnalysisViewMode', value)
})

const toggleDisplayMode = () => {
  displayMode.value = displayMode.value === 'base' ? 'detailed' : 'base';
};

const fuelData = computed(() => {
    return data.value?.fuel || {
        current_fuel_level: -1.0,
        burn_history: [],
        average_burn: -1.0,
        avg_laps_left_estimate: -1.0,
        avg_target_laps: -1.0,
        avg_floor_laps: -1.0,
        avg_floor_lap_target: -1.0,
        avg_ceil_laps: -1.0,
        avg_ceil_lap_target: -1.0,
        avg_one_lap_less_left: -1,
        avg_one_lap_less_target: -1.0,
        avg_one_lap_more_left: -1,
        avg_one_lap_more_target: -1.0,
        last_laps_left_estimate: -1.0,
        last_target_laps: -1.0,
        last_floor_laps: -1.0,
        last_floor_lap_target: -1.0,
        last_ceil_laps: -1.0,
        last_ceil_lap_target: -1.0,
        last_one_lap_less_left: -1,
        last_one_lap_less_target: -1.0,
        last_one_lap_more_left: -1,
        last_one_lap_more_target: -1.0,
    };
});

const summaryData = computed(() => {
  return [
    {
      key: 'current_fuel_level',
      label: 'Fuel Remaining',
      value: fuelData.value.current_fuel_level
    },
    {
      key: 'burn_history',
      label: 'Recent Consumption History',
      value: fuelData.value.burn_history
    },
    {
      key: 'average_burn',
      label: 'Average Consumption',
      value: fuelData.value.average_burn
    }
  ];
});

const lapFuelPairs = computed(() => {
  const prefix = viewMode.value === 'average' ? 'avg' : 'last';
  const consumptionType = viewMode.value === 'average'
    ? 'average fuel consumption'
    : "last lap's fuel consumption";

  const lapsLeftEstimate = fuelData.value[`${prefix}_laps_left_estimate`];
  const floorLaps = fuelData.value[`${prefix}_floor_laps`];
  const ceilLaps = fuelData.value[`${prefix}_ceil_laps`];
  const oneLapLess = fuelData.value[`${prefix}_one_lap_less_left`];
  const oneLapMore = fuelData.value[`${prefix}_one_lap_more_left`];

  return [
    {
      laps: typeof lapsLeftEstimate === 'number' ? lapsLeftEstimate.toFixed(2) : '-',
      target: fuelData.value.current_fuel_level,
      tooltip: `Exact laps left for ${consumptionType}`
    },
    {
      laps: floorLaps ?? '-',
      target: fuelData.value[`${prefix}_floor_lap_target`],
      tooltip: `Fuel target for ${floorLaps} whole laps`
    },
    {
      laps: ceilLaps ?? '-',
      target: fuelData.value[`${prefix}_ceil_lap_target`],
      tooltip: `Fuel target for ${ceilLaps} laps (rounded up)`
    },
    {
      laps: oneLapLess ?? '-',
      target: fuelData.value[`${prefix}_one_lap_less_target`],
      tooltip: `Fuel target for ${oneLapLess} laps (one less)`
    },
    {
      laps: oneLapMore ?? '-',
      target: fuelData.value[`${prefix}_one_lap_more_target`],
      tooltip: `Fuel target for ${oneLapMore} laps (one more)`
    }
  ];
});

const getSummaryIcon = (key) => {
  const icons = {
    current_fuel_level: 'pi pi-gauge',
    burn_history: 'pi pi-chart-bar',
    average_burn: 'pi pi-calculator'
  };
  return icons[key] || 'pi pi-info-circle';
};

const isCritical = (key) => {
    if (key === 'current_fuel_level' && fuelData.value.current_fuel_level < fuelData.value.average_burn) {
        return true;
    }
    return false;
};

const formatValue = (value, key) => {
  if (key === 'burn_history') {
    return Array.isArray(value)
      ? value.map(v => convertFuel(v).toFixed(2)).join(', ') + getFuelUnit()
      : value;
  }
  return typeof value === 'number'
    ? `${convertFuel(value).toFixed(2)}${getFuelUnit()}`
    : value;
};

const formatFuelValue = (value) => {
  return typeof value === 'number'
    ? `${convertFuel(value).toFixed(2)}${getFuelUnit()}`
    : value;
};

const formatBurnHistory = (value) => {
  return Array.isArray(value)
    ? value.map(v => convertFuel(v).toFixed(2)).join(', ') + getFuelUnit()
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

.summary-grid {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.summary-column {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 90px;
}

.summary-item {
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  flex: 1;
}

.summary-item.compact {
  padding: 0.3rem 0.5rem;
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
  gap: 0.3rem;
  align-items: flex-end;
  height: 50px;
}

.chart-bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}

.bar-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
  font-family: monospace;
  margin-bottom: 2px;
  white-space: nowrap;
}

.bar-wrapper {
  width: 100%;
  height: 35px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 80%;
  max-width: 20px;
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
  font-size: 0.75rem;
  font-weight: 600;
  color: #6c757d;
  margin-top: 2px;
}

.summary-label {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.summary-label i {
  color: #f5576c;
  font-size: 0.85rem;
}

.summary-value {
  font-size: 1rem;
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

.toggle-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 8px;
}

.toggle-btn {
  flex: 1;
  font-weight: 600;
  font-size: 0.8rem;
  padding: 0.4rem 0.6rem;
}

.toggle-btn.active {
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.fuel-table {
  border-radius: 8px;
  overflow: hidden;
}

.laps-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.laps-value {
  font-weight: 600;
  font-size: 0.9rem;
  color: #2c3e50;
}

.dark-mode .laps-value {
  color: var(--text-primary);
}

.tooltip-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.tooltip-icon {
  color: #17a2b8;
  cursor: help;
  font-size: 1.1rem;
  transition: all 0.2s ease;
}

.tooltip-icon:hover {
  color: #0c7489;
  transform: scale(1.2);
}

.tooltip-text {
  visibility: hidden;
  width: max-content;
  max-width: 300px;
  background-color: #2c3e50;
  color: #fff;
  text-align: left;
  border-radius: 8px;
  padding: 10px 14px;
  position: absolute;
  z-index: 1000;
  right: calc(100% + 10px);
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.85rem;
  font-weight: normal;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  pointer-events: none;
}

.tooltip-text::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 100%;
  margin-top: -6px;
  border-width: 6px;
  border-style: solid;
  border-color: transparent transparent transparent #2c3e50;
}

.tooltip-wrapper:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
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


:deep(.p-button) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .toggle-container {
    flex-direction: column;
  }

  .tooltip-text {
    left: auto;
    right: -10px;
    top: 100%;
    transform: translateY(10px);
    margin-top: 5px;
  }

  .tooltip-text::before {
    top: -12px;
    right: 20px;
    left: auto;
    border-color: transparent transparent #2c3e50 transparent;
  }
}

/* Dark mode overrides */
.dark-mode .summary-grid,
.dark-mode .toggle-container {
  background: var(--filter-content-bg);
  color: var(--text-primary);
}

.dark-mode .fuel-table :deep(.p-datatable-thead > tr > th) {
  background: var(--table-header-bg-start) !important;
  color: var(--table-header-text) !important;
  border-bottom-color: var(--table-border) !important;
}

.dark-mode .tooltip-text {
  background: var(--filter-content-bg);
  color: var(--text-primary);
}

.dark-mode .summary-item {
  background: var(--card-bg);
  border-color: var(--border-color);
}

.dark-mode .summary-label,
.dark-mode .summary-value,
.dark-mode .laps-cell,
.dark-mode .fuel-target {
  color: var(--text-primary);
}

.dark-mode .tooltip-text::before {
  border-color: transparent transparent var(--filter-content-bg) transparent;
}
</style>
