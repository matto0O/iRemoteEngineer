<template>
    <div class="fuel-data-container">
        <div v-if="!isConnected" class="connection-error">
        Connection lost - {{ connectionError || 'Attempting to reconnect...' }}
        </div>
      <h3>Fuel Analysis</h3>
      <DataTable :value="tableData" stripedRows responsiveLayout="scroll">
        <Column field="label" header="Metric"></Column>
        <Column field="value" header="Value">
          <template #body="slotProps">
            <span :class="{ 'fuel-critical': isCritical(slotProps.data.key) }">
              {{ formatValue(slotProps.data.value) }}
            </span>
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

// Get shared race data from composable
const { data, isConnected, connectionError } = useRaceData()

// Watch race data for fuel analysis information
const fuelData = computed(() => {
    return data.value?.fuel_analysis || {
        fuel_left: -1.0,
        average_consumption: -1.0,
        target_laps_avg: -1,
        target_laps_avg_consumption: -1.0,
        ollavg: -1,
        ollavg_consumption_target: -1.0,
        omlavg: -1,
        omlavg_consumption_target: -1.0,
        last_lap_consumption: -1.0,
        target_laps_last: -1,
        target_laps_last_consumption: -1.0
    };
});

// Updated tableData to use the computed fuelData
const tableData = computed(() => {
    return Object.entries(fuelData.value).map(([key, value]) => ({
        key,
        label: labels[key] || key,
        value
    }));
});

// Update isCritical to use fuelData
const isCritical = (key) => {
    // Example logic - fuel is critical if less than 10 units
    if (key === 'fuel_left' && fuelData.value.fuel_left < fuelData.value.average_consumption) {
        return true;
    }
    // Lap count is critical if less than 3
    if (['target_laps_avg', 'target_laps_last', 'ollavg', 'omlavg'].includes(key) && 
            fuelData.value[key] < 3) {
        return true;
    }
    return false;
};
  
  // Map of keys to human-readable labels
  const labels = {
    fuel_left: "Fuel Remaining",
    average_consumption: "Average Consumption",
    target_laps_avg: "Target Laps (Average Consumption)",
    target_laps_avg_consumption: "Target Average Consumption",
    ollavg: "One Lap Less by Average Consumption",
    ollavg_consumption_target: "One Lap Less by Avg - Target Consumption",
    omlavg: "One Lap More by Average Consumption",
    omlavg_consumption_target: "One Lap More by Avg - Target Consumption",
    last_lap_consumption: "Last Lap Consumption",
    target_laps_last: "Target Laps (Last Lap Consumption)",
    target_laps_last_consumption: "Target Consumption (Last Lap Consumption)"
  };
  
  // Format numeric values with 2 decimal places
  const formatValue = (value) => {
    return typeof value === 'number' 
      ? value.toFixed(2) 
      : value;
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