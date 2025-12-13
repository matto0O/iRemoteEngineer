<template>
  <div class="fuel-data-container">
    <h3>Fuel Analysis</h3>
    
    <!-- Always visible summary data -->
    <DataTable :value="summaryData" stripedRows responsiveLayout="scroll" class="summary-table">
      <Column field="label" header="Metric"></Column>
      <Column field="value" header="Value">
        <template #body="slotProps">
          <span :class="{ 'fuel-critical': isCritical(slotProps.data.key) }">
            {{ formatValue(slotProps.data.value, slotProps.data.key) }}
          </span>
        </template>
      </Column>
    </DataTable>

    <!-- Toggle buttons -->
    <div class="toggle-container">
      <button 
        :class="['toggle-btn', { active: viewMode === 'average' }]"
        @click="viewMode = 'average'"
      >
        Average Consumption
      </button>
      <button 
        :class="['toggle-btn', { active: viewMode === 'last' }]"
        @click="viewMode = 'last'"
      >
        Last Lap Consumption
      </button>
    </div>

    <!-- Lap-fuel consumption pairs table -->
    <DataTable :value="lapFuelPairs" stripedRows responsiveLayout="scroll" class="laps-table">
      <Column header="Laps">
        <template #body="slotProps">
          <div class="laps-cell">
            <span>{{ slotProps.data.laps }}</span>
            <span class="tooltip-wrapper">
              <span class="tooltip-icon">ⓘ</span>
              <span class="tooltip-text">{{ slotProps.data.tooltip }}</span>
            </span>
          </div>
        </template>
      </Column>
      <Column header="Target Fuel Consumption">
        <template #body="slotProps">
          <span>{{ formatFuelValue(slotProps.data.target) }}</span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import useRaceData from '@/composables/useRaceData';

const props = defineProps({
  socket: {
    type: Object,
    required: true
  }
})

const viewMode = ref('average'); // 'average' or 'last'

// Get shared race data from composable
const { data } = useRaceData(props.socket)

// Watch race data for fuel analysis information
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

// Summary data (always visible)
const summaryData = computed(() => {
  return [
    {
      key: 'current_fuel_level',
      label: 'Fuel remaining',
      value: fuelData.value.current_fuel_level
    },
    {
      key: 'burn_history',
      label: "Last laps' fuel consumption history",
      value: fuelData.value.burn_history
    },
    {
      key: 'average_burn',
      label: 'Recent average fuel consumption',
      value: fuelData.value.average_burn
    }
  ];
});

// Lap-fuel pairs based on selected view mode
const lapFuelPairs = computed(() => {
  const prefix = viewMode.value === 'average' ? 'avg' : 'last';
  const consumptionType = viewMode.value === 'average' 
    ? 'average fuel consumption' 
    : "last lap's fuel consumption";

  const floorLaps = fuelData.value[`${prefix}_floor_laps`];
  const ceilLaps = fuelData.value[`${prefix}_ceil_laps`];
  const oneLapLess = fuelData.value[`${prefix}_one_lap_less_left`];
  const oneLapMore = fuelData.value[`${prefix}_one_lap_more_left`];

  return [
    {
      laps: `${fuelData.value[`${prefix}_laps_left_estimate`].toFixed(2)}`,
      target: fuelData.value.current_fuel_level,
      tooltip: `Exact laps left for ${consumptionType}`
    },
    {
      laps: floorLaps,
      target: fuelData.value[`${prefix}_floor_lap_target`],
      tooltip: `Fuel consumption target for ${floorLaps} whole laps`
    },
    {
      laps: ceilLaps,
      target: fuelData.value[`${prefix}_ceil_lap_target`],
      tooltip: `Fuel consumption target for ${ceilLaps} laps (rounded up)`
    },
    {
      laps: oneLapLess,
      target: fuelData.value[`${prefix}_one_lap_less_target`],
      tooltip: `Fuel consumption target for ${oneLapLess} laps (one less than whole laps)`
    },
    {
      laps: oneLapMore,
      target: fuelData.value[`${prefix}_one_lap_more_target`],
      tooltip: `Fuel consumption target for ${oneLapMore} laps (one more than rounded up)`
    }
  ];
});

const isCritical = (key) => {
    // Fuel is critical if less than average burn
    if (key === 'current_fuel_level' && fuelData.value.current_fuel_level < fuelData.value.average_burn) {
        return true;
    }
    return false;
};

// Format numeric values with 2 decimal places
const formatValue = (value, key) => {
  if (key === 'burn_history') {
    return Array.isArray(value) ? value.map(v => v.toFixed(2)).join(', ') + 'L' : value;
  }
  return typeof value === 'number' 
    ? `${value.toFixed(2)}L` 
    : value;
};

const formatFuelValue = (value) => {
  return typeof value === 'number' ? `${value.toFixed(2)}L` : value;
};
</script>

<style scoped>
.fuel-data-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
  border-radius: 8px;
  background-color: #f8f8f8;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #ddd;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.summary-table {
  margin-bottom: 1.5rem;
}

.toggle-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  justify-content: center;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background-color: white;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.toggle-btn:hover {
  background-color: #f0f0f0;
}

.toggle-btn.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.laps-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tooltip-wrapper {
  position: relative;
  display: inline-block;
}

.tooltip-icon {
  color: #007bff;
  cursor: help;
  font-size: 1rem;
  margin-left: 0.25rem;
  display: inline-block;
  font-weight: bold;
}

.tooltip-icon:hover {
  color: #0056b3;
  transform: scale(1.1);
}

.tooltip-text {
  visibility: hidden;
  width: 250px;
  background-color: #333;
  color: #fff;
  text-align: left;
  border-radius: 6px;
  padding: 8px 12px;
  position: absolute;
  z-index: 1000;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 10px;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.85rem;
  font-weight: normal;
  white-space: normal;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.tooltip-text::before {
  content: "";
  position: absolute;
  top: 50%;
  right: 100%;
  margin-top: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent #333 transparent transparent;
}

.tooltip-wrapper:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

.fuel-critical {
  color: #ff3333;
  font-weight: bold;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f1f1f1;
  padding: 0.5rem 0.75rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 0.75rem;
}
</style>