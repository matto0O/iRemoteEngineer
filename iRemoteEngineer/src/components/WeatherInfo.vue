<template>
  <div class="weather-container">
    <Card class="weather-card">
      <template #title>
        <div class="card-header">
          <div class="card-header-left">
            <i class="pi pi-cloud"></i>
            <span>Weather Conditions</span>
          </div>
          <Button
            :icon="viewMode === 'graphical' ? 'pi pi-table' : 'pi pi-chart-bar'"
            @click="toggleViewMode"
            size="small"
            severity="secondary"
            :label="viewMode === 'graphical' ? 'Table' : 'Graphical'"
            class="view-toggle-btn"
          />
        </div>
      </template>
      <template #content>
        <!-- Weather Summary Cards (Graphical View) -->
        <div v-if="viewMode === 'graphical'" class="weather-grid">
          <div class="weather-item temperature-item">
            <div class="weather-icon">
              <i class="pi pi-sun"></i>
            </div>
            <div class="weather-data">
              <div class="weather-label">Air Temperature</div>
              <div class="weather-value">{{ formatTemp(convertTemp(weatherData.air_temp)) }}{{ getTempUnit() }}</div>
            </div>
          </div>

          <div class="weather-item temperature-item">
            <div class="weather-icon track-icon">
              <i class="pi pi-circle-fill"></i>
            </div>
            <div class="weather-data">
              <div class="weather-label">Track Temperature</div>
              <div class="weather-value">{{ formatTemp(convertTemp(weatherData.track_temp)) }}{{ getTempUnit() }}</div>
            </div>
          </div>

          <div class="weather-item wind-item">
            <div class="weather-icon">
              <i class="pi pi-directions"></i>
            </div>
            <div class="weather-data">
              <div class="weather-label">Wind</div>
              <div class="weather-value">{{ formatTemp(convertSpeed(weatherData.wind_speed)) }} {{ getSpeedUnit() }}</div>
              <div class="weather-subvalue">{{ weatherData.wind_direction }}</div>
            </div>
          </div>

          <div :class="['weather-item', 'wetness-item', { 'weather-alert': isAlert('track_wetness') }]">
            <div class="weather-icon">
              <i :class="weatherData.track_wetness !== 'Dry' ? 'pi pi-cloud' : 'pi pi-sun'"></i>
            </div>
            <div class="weather-data">
              <div class="weather-label">Track Condition</div>
              <div class="weather-value">{{ weatherData.track_wetness }}</div>
              <div v-if="weatherData.precipitation && weatherData.precipitation > 0" class="weather-subvalue">
                Rain: {{ formatTemp(weatherData.precipitation) }}%
              </div>
            </div>
          </div>

          <div :class="['weather-item', 'declared-wet-item', { 'weather-alert': weatherData.declared_wet }]">
            <div class="weather-icon">
              <i :class="weatherData.declared_wet ? 'pi pi-exclamation-triangle' : 'pi pi-check-circle'"></i>
            </div>
            <div class="weather-data">
              <div class="weather-label">Session Status</div>
              <div class="weather-value">{{ weatherData.declared_wet ? 'WET' : 'DRY' }}</div>
            </div>
          </div>

          <div :class="['weather-item', 'precipitation-item', { 'weather-alert': isAlert('precipitation') }]">
            <div class="weather-icon">
              <i :class="weatherData.precipitation > 0 ? 'pi pi-cloud-download' : 'pi pi-sun'"></i>
            </div>
            <div class="weather-data">
              <div class="weather-label">Precipitation</div>
              <div class="weather-value">{{ formatTemp(weatherData.precipitation) }}%</div>
              <div class="weather-subvalue">{{ getPrecipitationStatus(weatherData.precipitation) }}</div>
            </div>
          </div>
        </div>

        <!-- Detailed Table (Table View) -->
        <div v-if="viewMode === 'table'" class="table-section">
          <DataTable :value="tableData" stripedRows class="weather-table">
            <Column field="label" header="Metric" style="min-width: 150px"></Column>
            <Column field="value" header="Value">
              <template #body="slotProps">
                <span :class="{ 'weather-alert-text': isAlert(slotProps.data.key) }">
                  {{ formatValue(slotProps.data.value, slotProps.data.key) }}
                </span>
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
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

const { data } = useRaceData(props.socket);
const { convertTemp, getTempUnit, convertSpeed, getSpeedUnit } = useUnits();

// Load saved preference from localStorage
const loadViewMode = () => {
  const saved = localStorage.getItem('weatherInfoViewMode')
  return saved !== null ? saved : 'graphical'
}

const viewMode = ref(loadViewMode()); // 'graphical' or 'table'

// Save preference to localStorage whenever it changes
watch(viewMode, (value) => {
  localStorage.setItem('weatherInfoViewMode', value)
})

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'graphical' ? 'table' : 'graphical';
};

const weatherData = computed(() => {
  return data.value?.weather_data || {
    air_temp: 0,
    track_temp: 0,
    wind_speed: 0,
    wind_direction: 0,
    track_wetness: 0,
    precipitation: 0,
    declared_wet: false
  };
});

const labels = {
  air_temp: "Air Temperature",
  track_temp: "Track Temperature",
  wind_speed: "Wind Speed",
  wind_direction: "Wind Direction",
  track_wetness: "Track Wetness",
  precipitation: "Precipitation",
  declared_wet: "Declared Wet"
};

const formatTemp = (value) => {
  return typeof value === 'number' ? Math.round(value) : '0';
};

const formatValue = (value, key) => {
  if (key === 'air_temp' || key === 'track_temp') {
    return `${formatTemp(convertTemp(value))}${getTempUnit()}`;
  } else if (key === 'wind_speed') {
    return `${formatTemp(convertSpeed(value))} ${getSpeedUnit()}`;
  } else if (key === 'wind_direction' || key === 'track_wetness' || key === 'precipitation') {
    return value || '0';
  } else if (key === 'declared_wet') {
    return value ? 'Yes' : 'No';
  }
  return typeof value === 'number' ? Math.round(value) : value;
};

const isAlert = (key) => {
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

const getPrecipitationStatus = (value) => {
  if (value === 0) return 'No Rain';
  if (value < 0.1) return 'Light Drizzle';
  if (value < 0.3) return 'Light Rain';
  if (value < 0.6) return 'Moderate Rain';
  return 'Heavy Rain';
};

const tableData = computed(() => {
  return Object.entries(weatherData.value).map(([key, value]) => ({
    key,
    label: labels[key] || key,
    value
  }));
});
</script>

<style scoped>
.weather-container {
  width: 100%;
  height: 100%;
  padding: 0;
}

.weather-card {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.dark-mode .weather-card {
  background: linear-gradient(135deg, #507580 0%, #a07080 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.weather-card :deep(.p-card-body) {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0;
}

.weather-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: white;
  padding: 1rem;
  border-radius: 16px 16px 0 0;
  margin: 0;
}

.dark-mode .weather-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #507580 0%, #a07080 100%);
}

.weather-card :deep(.p-card-content) {
  padding: 0.75rem;
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

.weather-grid {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0;
}

.weather-item {
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 6px;
  padding: 0.35rem 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.weather-item:hover {
  border-color: #a8edea;
  box-shadow: 0 2px 8px rgba(168, 237, 234, 0.3);
}

.weather-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: white;
  flex-shrink: 0;
}

.track-icon {
  background: linear-gradient(135deg, #ff9a56 0%, #ffcd3c 100%);
}

.weather-data {
  flex: 1;
  min-width: 0;
}

.weather-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 0;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.weather-value {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary, #2c3e50);
  line-height: 1.1;
}

.weather-subvalue {
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0;
}

.weather-alert {
  background: linear-gradient(135deg, #fff3cd 0%, #ffe5b4 100%);
  border-color: #ffc107;
  animation: pulse-alert 2s infinite;
}

.weather-alert .weather-icon {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
  animation: shake 0.5s infinite;
}

@keyframes pulse-alert {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(255, 193, 7, 0);
  }
}

@keyframes shake {
  0%, 100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-5deg);
  }
  75% {
    transform: rotate(5deg);
  }
}

.table-section {
  margin-top: 0;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e9ecef;
}

.table-title i {
  color: #a8edea;
}

.weather-table {
  border-radius: 8px;
  overflow: hidden;
}

.weather-alert-text {
  color: #ff6b00;
  font-weight: 600;
}

:deep(.p-datatable) {
  font-size: 0.95rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 0.875rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #dee2e6;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.875rem;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8f9fa !important;
}

@media (max-width: 768px) {
  .weather-grid {
    grid-template-columns: 1fr;
  }
}

/* Dark mode overrides */
.dark-mode .weather-grid,
.dark-mode .weather-item {
  background: var(--filter-content-bg);
  color: var(--text-primary);
}

.dark-mode .weather-label,
.dark-mode .weather-value {
  color: var(--text-primary);
}
</style>
