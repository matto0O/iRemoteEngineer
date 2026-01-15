<template>
  <div class="lap-history-container">
    <Card class="lap-history-card">
      <template #title>
        <div class="card-header">
          <div class="card-header-left">
            <i class="pi pi-flag"></i>
            <span>Lap History</span>
          </div>
          <div class="card-header-buttons">
            <Button
              :label="showFilters ? 'Hide Filters' : 'Show Filters'"
              :icon="showFilters ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
              size="small"
              severity="secondary"
              class="filter-toggle-btn"
              @click="showFilters = !showFilters"
            />
            <Button
              :icon="displayMode === 'base' ? 'pi pi-eye' : 'pi pi-eye-slash'"
              @click="toggleDisplayMode"
              size="small"
              severity="secondary"
              :label="displayMode === 'base' ? 'Detailed' : 'Base'"
              class="view-toggle-btn"
            />
          </div>
        </div>
      </template>
      <template #content>

    <div v-if="lapHistory.length === 0" class="no-laps">
      <i class="pi pi-inbox"></i>
      <p>No lap history available</p>
    </div>

    <div v-else>
      <!-- Filters (Collapsible) -->
      <div v-if="showFilters" class="filters-container">
        <!-- Driver Selection Filter -->
        <div class="filter-group">
          <label class="filter-label">Drivers:</label>
          <div class="driver-filters">
            <Button
              v-for="driver in uniqueDrivers"
              :key="driver"
              :label="driver"
              :class="selectedDrivers.includes(driver) ? 'p-button-sm filter-btn active' : 'p-button-outlined p-button-sm filter-btn'"
              @click="toggleDriver(driver)"
            />
          </div>
        </div>
        
        <!-- Incident Filter -->
        <div class="filter-group">
          <label class="filter-label">Show:</label>
          <div class="incident-filters">
            <Button
              v-for="option in incidentFilterOptions"
              :key="option.value"
              :label="option.label"
              :class="incidentFilter === option.value ? 'p-button-sm filter-btn active' : 'p-button-outlined p-button-sm filter-btn'"
              @click="incidentFilter = option.value"
            />
          </div>
        </div>
      </div>
      
      <!-- Lap History Table -->
      <div class="lap-history-table-container">
        <DataTable
          :value="filteredLaps"
          :scrollable="true"
          scrollHeight="300px"
          stripedRows
          sortMode="single"
          class="p-datatable-sm lap-history-table"
          :rowClass="getRowClass"
          tableStyle="width: 100%;"
        >
          <Column field="lapNumber" header="Lap" sortable style="width: 50px; max-width: 50px;"></Column>
          <Column field="driver_name" header="Driver" sortable style="min-width: 80px;"></Column>
          <Column field="lap_time" header="Time" sortable style="width: 80px; max-width: 80px;">
            <template #body="slotProps">
              <div class="time-cell">{{ slotProps.data.lap_time }}</div>
            </template>
          </Column>
          <Column field="fuel_consumed" header="Fuel" sortable style="width: 70px; max-width: 70px;">
            <template #body="slotProps">
              <div :class="getFuelCellClass(slotProps.data)">
                {{ convertFuel(slotProps.data.fuel_consumed).toFixed(2) }}
              </div>
            </template>
          </Column>
          <Column field="incidents_incurred" header="Inc" sortable style="width: 40px; max-width: 40px;">
            <template #body="slotProps">
              <div :class="['incident-cell', { 'has-incident': slotProps.data.incidents_incurred > 0 }]">
                {{ slotProps.data.incidents_incurred }}
              </div>
            </template>
          </Column>
        </DataTable>
        
        <div v-if="filteredLaps.length === 0" class="no-filtered-laps">
          No laps match the current filters
        </div>
      </div>


      <!-- Statistics (Detailed mode only) -->
      <div v-if="displayMode === 'detailed'" class="statistics-container">
        <div class="stat-item">
          <span class="stat-label">Total Laps:</span>
          <span class="stat-value">{{ statistics.totalLaps }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Average Lap Time:</span>
          <span class="stat-value">{{ statistics.averageLapTime }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Average Fuel Used:</span>
          <span class="stat-value">{{ statistics.averageFuel }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Total Incidents:</span>
          <span class="stat-value" :class="{ 'high-incidents': statistics.totalIncidents > 0 }">
            {{ statistics.totalIncidents }}
          </span>
        </div>
      </div>
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
});

// Get shared race data from composable
const { data } = useRaceData(props.socket);
const { convertFuel, getFuelUnit } = useUnits();

// Display mode
const displayMode = ref('base'); // 'base' or 'detailed'

const toggleDisplayMode = () => {
  displayMode.value = displayMode.value === 'base' ? 'detailed' : 'base';
};

// Filter states
const selectedDrivers = ref([]);
const incidentFilter = ref('all'); // 'all', 'with_incidents', 'without_incidents'
const showFilters = ref(false);

// Filter options
const incidentFilterOptions = [
  { value: 'all', label: 'All Laps' },
  { value: 'with_incidents', label: 'With Incidents' },
  { value: 'without_incidents', label: 'Without Incidents' }
];

// Get lap history from race data with lap numbers
const lapHistory = computed(() => {
  const history = data.value?.lap_history || [];
  return history.map((lap, index) => ({
    ...lap,
    lapNumber: index + 1
  }));
});

// Get unique drivers from lap history
const uniqueDrivers = computed(() => {
  const drivers = new Set(lapHistory.value.map(lap => lap.driver_name));
  return Array.from(drivers).sort();
});

// Initialize selected drivers when data loads (select all by default)
watch(uniqueDrivers, (newDrivers) => {
  if (selectedDrivers.value.length === 0 && newDrivers.length > 0) {
    selectedDrivers.value = [...newDrivers];
  }
}, { immediate: true });

// Toggle driver selection
const toggleDriver = (driver) => {
  const index = selectedDrivers.value.indexOf(driver);
  if (index === -1) {
    selectedDrivers.value.push(driver);
  } else {
    // Don't allow deselecting all drivers
    if (selectedDrivers.value.length > 1) {
      selectedDrivers.value.splice(index, 1);
    }
  }
};

// Filter laps based on selected filters
const filteredLaps = computed(() => {
  let filtered = lapHistory.value.filter(lap => {
    // Driver filter
    if (!selectedDrivers.value.includes(lap.driver_name)) {
      return false;
    }
    
    // Incident filter
    if (incidentFilter.value === 'with_incidents' && lap.incidents_incurred === 0) {
      return false;
    }
    if (incidentFilter.value === 'without_incidents' && lap.incidents_incurred > 0) {
      return false;
    }
    
    return true;
  });
  
  return filtered;
});

// Check if lap time is valid (not --:--.---)
const isValidLapTime = (timeStr) => {
  return timeStr && typeof timeStr === 'string' && !timeStr.startsWith('--');
};

// Convert lap time string to seconds for comparison
const lapTimeToSeconds = (timeStr) => {
  if (!isValidLapTime(timeStr)) return Infinity;

  const parts = timeStr.split(':');
  if (parts.length !== 2) return Infinity;

  const minutes = parseInt(parts[0]);
  const seconds = parseFloat(parts[1]);

  if (isNaN(minutes) || isNaN(seconds)) return Infinity;

  return minutes * 60 + seconds;
};

// Find the overall best lap time (prioritize laps without incidents)
const bestLapTime = computed(() => {
  if (lapHistory.value.length === 0) return null;

  // Filter out invalid lap times first
  const validLaps = lapHistory.value.filter(lap => isValidLapTime(lap.lap_time));
  if (validLaps.length === 0) return null;

  // First, try to find the best lap without incidents
  const cleanLaps = validLaps.filter(lap => lap.incidents_incurred === 0);

  let lapsToConsider = cleanLaps.length > 0 ? cleanLaps : validLaps;

  let best = null;
  let bestSeconds = Infinity;

  lapsToConsider.forEach(lap => {
    const seconds = lapTimeToSeconds(lap.lap_time);
    if (seconds < bestSeconds) {
      bestSeconds = seconds;
      best = lap.lap_time;
    }
  });

  return best;
});

// Find personal best lap times for each driver (prioritize laps without incidents)
const personalBests = computed(() => {
  const bests = {};

  // Group laps by driver
  const lapsByDriver = {};
  lapHistory.value.forEach(lap => {
    if (!lapsByDriver[lap.driver_name]) {
      lapsByDriver[lap.driver_name] = [];
    }
    lapsByDriver[lap.driver_name].push(lap);
  });

  // For each driver, find their best lap
  Object.keys(lapsByDriver).forEach(driver => {
    const driverLaps = lapsByDriver[driver];

    // Filter out invalid lap times first
    const validLaps = driverLaps.filter(lap => isValidLapTime(lap.lap_time));
    if (validLaps.length === 0) {
      bests[driver] = null;
      return;
    }

    // First, try to find the best lap without incidents
    const cleanLaps = validLaps.filter(lap => lap.incidents_incurred === 0);
    const lapsToConsider = cleanLaps.length > 0 ? cleanLaps : validLaps;

    let bestTime = null;
    let bestSeconds = Infinity;

    lapsToConsider.forEach(lap => {
      const seconds = lapTimeToSeconds(lap.lap_time);
      if (seconds < bestSeconds) {
        bestSeconds = seconds;
        bestTime = lap.lap_time;
      }
    });

    bests[driver] = bestTime;
  });

  return bests;
});

// Find lowest fuel consumption for each driver (only for valid laps with positive fuel)
const lowestFuelPerDriver = computed(() => {
  const lowest = {};

  // Group laps by driver
  const lapsByDriver = {};
  lapHistory.value.forEach(lap => {
    if (!lapsByDriver[lap.driver_name]) {
      lapsByDriver[lap.driver_name] = [];
    }
    lapsByDriver[lap.driver_name].push(lap);
  });

  // For each driver, find their lowest fuel consumption (only on valid laps with positive fuel)
  Object.keys(lapsByDriver).forEach(driver => {
    const driverLaps = lapsByDriver[driver];

    // Filter out invalid lap times and negative/zero fuel values
    const validLaps = driverLaps.filter(lap =>
      isValidLapTime(lap.lap_time) && lap.fuel_consumed > 0
    );
    if (validLaps.length === 0) {
      lowest[driver] = Infinity;
      return;
    }

    let lowestFuel = Infinity;

    validLaps.forEach(lap => {
      if (lap.fuel_consumed < lowestFuel) {
        lowestFuel = lap.fuel_consumed;
      }
    });

    lowest[driver] = lowestFuel;
  });

  return lowest;
});

// Determine row class for highlighting
const getRowClass = (lap) => {
  const classes = [];
  
  // Check if this is the overall best lap
  if (lap.lap_time === bestLapTime.value) {
    classes.push('best-lap-row');
  }
  // Check if this is a personal best (but not the overall best)
  else if (lap.lap_time === personalBests.value[lap.driver_name]) {
    classes.push('personal-best-row');
  }
  
  return classes.join(' ');
};

// Determine fuel cell class
const getFuelCellClass = (lap) => {
  const classes = ['fuel-cell'];
  
  // Check if this is the lowest fuel for this driver
  if (lap.fuel_consumed === lowestFuelPerDriver.value[lap.driver_name]) {
    // Check if this row has a green background (personal best)
    const isPersonalBest = lap.lap_time === personalBests.value[lap.driver_name];
    const isBestLap = lap.lap_time === bestLapTime.value;
    
    // If row has green background, use a different color for fuel
    if (isPersonalBest || isBestLap) {
      classes.push('lowest-fuel-alt');
    } else {
      classes.push('lowest-fuel');
    }
  }
  
  return classes.join(' ');
};

// Calculate statistics based on filtered laps (only valid laps)
const statistics = computed(() => {
  // Filter to only valid laps for statistics
  const validFilteredLaps = filteredLaps.value.filter(lap => isValidLapTime(lap.lap_time));
  const totalLaps = filteredLaps.value.length;
  const validLapsCount = validFilteredLaps.length;

  if (totalLaps === 0) {
    return {
      totalLaps: 0,
      averageLapTime: '-',
      averageFuel: '-',
      totalIncidents: 0
    };
  }

  // Calculate total seconds for average lap time (only from valid laps)
  let totalSeconds = 0;
  let totalFuel = 0;
  let totalIncidents = 0;

  filteredLaps.value.forEach(lap => {
    if (isValidLapTime(lap.lap_time)) {
      totalSeconds += lapTimeToSeconds(lap.lap_time);
      totalFuel += lap.fuel_consumed;
    }
    totalIncidents += lap.incidents_incurred;
  });

  // Calculate average lap time only if we have valid laps
  let avgLapTime = '-';
  let avgFuel = '-';

  if (validLapsCount > 0) {
    const avgSeconds = totalSeconds / validLapsCount;
    const minutes = Math.floor(avgSeconds / 60);
    const seconds = avgSeconds % 60;
    avgLapTime = `${minutes}:${seconds.toFixed(3).padStart(6, '0')}`;
    avgFuel = `${convertFuel(totalFuel / validLapsCount).toFixed(2)}${getFuelUnit()}`;
  }

  return {
    totalLaps,
    averageLapTime: avgLapTime,
    averageFuel: avgFuel,
    totalIncidents
  };
});
</script>

<style scoped>
.lap-history-container {
  width: 100%;
  height: 100%;
  padding: 0;
}

.lap-history-card {
  background: linear-gradient(135deg, #8e44ad 0%, #3498db 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.dark-mode .lap-history-card {
  background: linear-gradient(135deg, #6a3580 0%, #2a70a0 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.lap-history-card :deep(.p-card-body) {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0;
}

.lap-history-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #8e44ad 0%, #3498db 100%);
  color: white;
  padding: 1rem;
  border-radius: 16px 16px 0 0;
  margin: 0;
}

.dark-mode .lap-history-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #6a3580 0%, #2a70a0 100%);
}

.lap-history-card :deep(.p-card-content) {
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

.card-header-buttons {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.card-header i {
  font-size: 1.25rem;
}

.view-toggle-btn,
.filter-toggle-btn {
  flex-shrink: 0;
}

.no-laps {
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
}

.no-laps i {
  font-size: 3rem;
  color: #dee2e6;
  margin-bottom: 1rem;
}

.no-laps p {
  font-size: 1.1rem;
  font-style: italic;
}

.legend-container {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #495057;
}

.legend-color {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.fastest-lap-legend {
  background: linear-gradient(135deg, #e1bee7 0%, #ba68c8 100%);
}

.personal-best-legend {
  background: linear-gradient(135deg, #c8e6c9 0%, #81c784 100%);
}

.filters-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.filter-label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.filter-label::before {
  content: "•";
  color: #8e44ad;
  font-size: 1rem;
}

.driver-filters,
.incident-filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  font-weight: 600;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  transform: translateY(-2px);
}

.filter-btn.active {
  box-shadow: 0 4px 12px rgba(142, 68, 173, 0.4);
}

.lap-history-table-container {
  max-height: 350px;
  overflow-y: auto;
  overflow-x: auto;
  margin-bottom: 0.75rem;
  border: 1px solid #eee;
  border-radius: 4px;
  position: relative;
}

.lap-history-table {
  width: 100% !important;
}

:deep(.p-datatable) {
  font-size: 0.8rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f1f1f1;
  padding: 0.4rem 0.5rem;
  position: sticky;
  top: 0;
  z-index: 1;
  border-bottom: 2px solid #ddd;
  font-size: 0.75rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid #eee;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  cursor: default;
}

/* Highlighting for best laps - PURPLE for fastest, GREEN for personal best */
:deep(.p-datatable .p-datatable-tbody > tr.best-lap-row) {
  background: linear-gradient(135deg, #e1bee7 0%, #ce93d8 100%) !important;
  font-weight: 600;
  box-shadow: inset 0 0 0 2px #ba68c8;
}

:deep(.p-datatable .p-datatable-tbody > tr.personal-best-row) {
  background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%) !important;
  font-weight: 500;
  box-shadow: inset 0 0 0 2px #81c784;
}

.time-cell {
  font-family: monospace;
  font-size: 0.8rem;
}

.fuel-cell {
  font-family: monospace;
  text-align: right;
}

.fuel-cell.lowest-fuel {
  background-color: #c8e6c9;
  font-weight: 600;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
}

.fuel-cell.lowest-fuel-alt {
  background-color: #fff9c4;
  font-weight: 600;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
}

.incident-cell {
  text-align: center;
  font-weight: 500;
}

.incident-cell.has-incident {
  color: #d32f2f;
  font-weight: 600;
}

.dark-mode .incident-cell.has-incident {
  color: #d32f2f;
}

.no-filtered-laps {
  text-align: center;
  color: #999;
  padding: 2rem;
  font-style: italic;
}

.statistics-container {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.4rem 0.6rem;
  background: white;
  border-radius: 6px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  flex: 1;
  min-width: 80px;
}

.stat-item:hover {
  border-color: #8e44ad;
  box-shadow: 0 2px 8px rgba(142, 68, 173, 0.2);
  transform: translateY(-1px);
}

.stat-label {
  font-size: 0.65rem;
  color: #6c757d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: #2c3e50;
  font-family: monospace;
}

.stat-value.high-incidents {
  color: #dc3545;
  animation: pulse-warn 2s infinite;
}

@keyframes pulse-warn {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

:deep(.p-button) {
  border-radius: 8px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .legend-container {
    flex-direction: column;
    align-items: center;
  }

  .statistics-container {
    grid-template-columns: 1fr;
  }
}

/* Dark mode overrides */
.dark-mode .filters-container {
  background: var(--filter-content-bg);
  border-color: var(--border-color);
}

.dark-mode .filter-label {
  color: var(--text-primary);
}

.dark-mode .lap-history-table-container :deep(.p-datatable .p-datatable-thead > tr > th) {
  background: var(--table-header-bg-start) !important;
  color: var(--table-header-text) !important;
  border-bottom-color: var(--table-border) !important;
}

.dark-mode .statistics-container {
  background: var(--filter-content-bg);
  border-color: var(--border-color);
}

.dark-mode .stat-item {
  background: var(--card-bg);
  border-color: var(--border-color);
}

.dark-mode .stat-label {
  color: var(--text-secondary);
}

.dark-mode .stat-value {
  color: var(--text-primary);
}

.dark-mode .lap-history-table-container {
  border-color: var(--border-color);
}

.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row) {
  color: #000000 !important;
}

.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row > td),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row > td) {
  color: #000000 !important;
}

.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row > td > div),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row > td > div) {
  color: #000000 !important;
}

.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row .time-cell),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row .time-cell),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row .fuel-cell),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row .fuel-cell),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row .incident-cell),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row .incident-cell) {
  color: #000000 !important;
}

.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row .fuel-cell.lowest-fuel),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row .fuel-cell.lowest-fuel),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.best-lap-row .fuel-cell.lowest-fuel-alt),
.dark-mode .lap-history-table-container :deep(.p-datatable.p-datatable-sm .p-datatable-tbody > tr.personal-best-row .fuel-cell.lowest-fuel-alt) {
  color: #000000 !important;
}

/* Force black text for highlighted rows with extreme specificity */
.dark-mode .lap-history-table-container :deep(.p-datatable-striped.p-datatable-sm .p-datatable-tbody > tr.best-lap-row),
.dark-mode .lap-history-table-container :deep(.p-datatable-striped.p-datatable-sm .p-datatable-tbody > tr.personal-best-row),
.dark-mode .lap-history-table-container :deep(.p-datatable-striped.p-datatable-sm .p-datatable-tbody > tr.best-lap-row) *,
.dark-mode .lap-history-table-container :deep(.p-datatable-striped.p-datatable-sm .p-datatable-tbody > tr.personal-best-row) * {
  color: #000000 !important;
}

/* Keep incident red color even in highlighted rows */
.dark-mode .lap-history-table-container :deep(.p-datatable-striped.p-datatable-sm .p-datatable-tbody > tr.best-lap-row .incident-cell.has-incident),
.dark-mode .lap-history-table-container :deep(.p-datatable-striped.p-datatable-sm .p-datatable-tbody > tr.personal-best-row .incident-cell.has-incident) {
  color: #d32f2f !important;
}
</style>