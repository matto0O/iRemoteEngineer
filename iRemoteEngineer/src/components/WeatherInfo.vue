<template>
    <div class="weather-data-container">
      <div v-if="!isConnected" class="connection-error">
        Connection lost - {{ connectionError || 'Attempting to reconnect...' }}
      </div>
      <h3>Weather Conditions</h3>
      
      <DataTable :value="tableData" stripedRows responsiveLayout="scroll">
        <Column field="label" header="Metric"></Column>
        <Column field="value" header="Value">
          <template #body="slotProps">
            <span :class="{ 'weather-alert': isAlert(slotProps.data.key) }">
              {{ formatValue(slotProps.data.value, slotProps.data.key) }}
            </span>
          </template>
        </Column>
      </DataTable>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import DataTable from 'primevue/datatable';
  import Column from 'primevue/column';
  import useRaceData from '@/composables/useRaceData';
  
  // Get shared race data from composable
  const { data, isConnected, connectionError } = useRaceData();
  
  // Watch race data for weather information
  const weatherData = computed(() => {
    return data.value?.weather || {
      air_temp: 0,
      track_temp: 0,
      wind_speed: 0,
      wind_direction: 0,
      track_wetness: 0,
      precipitation: 0,
      declared_wet: false
    };
  });
  
  // Map of keys to human-readable labels
  const labels = {
    air_temp: "Air Temperature",
    track_temp: "Track Temperature",
    wind_speed: "Wind Speed",
    wind_direction: "Wind Direction",
    track_wetness: "Track Wetness",
    precipitation: "Precipitation",
    declared_wet: "Declared Wet"
  };
  
  // Format value based on the type of data
  const formatValue = (value, key) => {
    if (key === 'air_temp' || key === 'track_temp') {
      return `${value.toFixed(1)}°C`;
    } else if (key === 'wind_speed') {
      return `${value.toFixed(1)} kph`;
    } else if (key === 'wind_direction' || key === 'track_wetness' || key === 'precipitation') {
      return value;
    } else if (key === 'declared_wet') {
      return value ? 'Yes' : 'No';
    }
    return typeof value === 'number' ? value.toFixed(2) : value;
  };
  
  // Check if value should be highlighted as an alert
  const isAlert = (key) => {
    // Alert conditions
    if (key === 'track_wetness' && weatherData.value.track_wetness !== "Dry") {
      return true;
    }
    if (key === 'precipitation' && weatherData.value.precipitation > 0.05) {
      return true;
    }
    if (key === 'declared_wet' && weatherData.value.declared_wet) {
      return true;
    }
    return false;
  };
  
  // Transform weather data into table format for display
  const tableData = computed(() => {
    return Object.entries(weatherData.value).map(([key, value]) => ({
      key,
      label: labels[key] || key,
      value
    }));
  });
  </script>
  
  <style scoped>
  .weather-data-container {
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
  
  .connection-error {
    background-color: #fff3f3;
    color: #ff3333;
    padding: 0.5rem;
    margin-bottom: 1rem;
    border-radius: 4px;
    text-align: center;
  }
  
  .weather-alert {
    color: #0066cc;
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