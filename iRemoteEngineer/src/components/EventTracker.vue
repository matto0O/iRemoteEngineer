<template>
  <div class="events-container">
    <Card class="events-card">
      <template #title>
        <div class="card-header">
          <div class="card-header-left">
            <i class="pi pi-history"></i>
            <span>Race Events</span>
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
        <div v-if="events.length === 0" class="no-events">
          <i class="pi pi-inbox"></i>
          <p>No events recorded yet</p>
        </div>

        <div v-else>
          <!-- Filters (Collapsible) -->
          <div v-if="showFilters" class="filters-container">
            <Button
              v-for="filter in filterOptions"
              :key="filter.value"
              :label="filter.label"
              :icon="getFilterIcon(filter.value)"
              :class="selectedFilter === filter.value ? 'p-button-sm filter-btn active' : 'p-button-outlined p-button-sm filter-btn'"
              @click="selectedFilter = filter.value"
            >
              <template #default>
                {{ filter.label }}
                <span v-if="filter.value !== 'all'" class="filter-count">
                  {{ getEventCountByType(filter.value) }}
                </span>
              </template>
            </Button>
          </div>

          <!-- Events Table -->
          <div class="events-table-container">
            <DataTable
              :value="filteredEvents"
              stripedRows
              :scrollable="true"
              scrollHeight="400px"
              class="events-table"
              :rowClass="(data) => `event-row-${data.type}`"
            >
              <Column field="time" header="Time" style="width: 120px">
                <template #body="slotProps">
                  <div class="event-time">
                    <i class="pi pi-clock"></i>
                    {{ formatTime(slotProps.data.time) }}
                  </div>
                </template>
              </Column>
              <Column field="type" header="Type" style="width: 140px">
                <template #body="slotProps">
                  <span :class="`event-badge event-badge-${slotProps.data.type}`">
                    <i :class="getEventIcon(slotProps.data.type)"></i>
                    {{ formatEventType(slotProps.data.type) }}
                  </span>
                </template>
              </Column>
              <Column field="description" header="Description" style="min-width: 300px">
                <template #body="slotProps">
                  <div class="event-description">{{ slotProps.data.description }}</div>
                </template>
              </Column>
            </DataTable>

            <div v-if="filteredEvents.length === 0" class="no-filtered-events">
              <i class="pi pi-filter-slash"></i>
              <p>No {{ selectedFilter }} events found</p>
            </div>
          </div>

          <!-- Counters (Detailed mode only, at bottom) -->
          <div v-if="displayMode === 'detailed'" class="counters-grid">
            <div class="counter-card">
              <div class="counter-icon incident-icon">
                <i class="pi pi-exclamation-triangle"></i>
              </div>
              <div class="counter-data">
                <div class="counter-label">Total Incidents</div>
                <div :class="['counter-value', {'high-value': totalIncidents > 15}]">
                  {{ totalIncidents }}
                </div>
              </div>
            </div>

            <div class="counter-card">
              <div class="counter-icon events-icon">
                <i class="pi pi-list"></i>
              </div>
              <div class="counter-data">
                <div class="counter-label">Total Events</div>
                <div class="counter-value">{{ events.length }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import useRaceData from '@/composables/useRaceData';

const props = defineProps({
  socket: {
    type: Object,
    required: true
  }
});

const { data } = useRaceData(props.socket);

const displayMode = ref('base'); // 'base' or 'detailed'
const showFilters = ref(false);
const selectedFilter = ref('all');

const toggleDisplayMode = () => {
  displayMode.value = displayMode.value === 'base' ? 'detailed' : 'base';
};

const filterOptions = [
  { value: 'all', label: 'All Events' },
  { value: 'incident', label: 'Incidents' },
  { value: 'pit_stop', label: 'Pit Stops' },
  { value: 'weather', label: 'Weather' },
  { value: 'command', label: 'Commands' }
];

const events = computed(() => {
  return data.value?.event || [];
});

const sortedEvents = computed(() => {
  return [...events.value].reverse();
});

const filteredEvents = computed(() => {
  if (selectedFilter.value === 'all') {
    return sortedEvents.value;
  }
  return sortedEvents.value.filter(event => event.type === selectedFilter.value);
});

const getEventCountByType = (type) => {
  return events.value.filter(event => event.type === type).length;
};

const totalIncidents = computed(() => {
  return data.value?.total_incidents || 0;
});

const formatTime = (timestamp) => {
  if (timestamp && timestamp.includes(',')) {
    return timestamp.split(', ')[1];
  }
  return timestamp || '';
};

const formatEventType = (type) => {
  if (!type) return '';

  const typeMap = {
    incident: 'Incident',
    weather: 'Weather',
    pit_stop: 'Pit Stop',
    command: 'Command'
  };

  return typeMap[type] || type.charAt(0).toUpperCase() + type.slice(1);
};

const getEventIcon = (type) => {
  const iconMap = {
    incident: 'pi pi-exclamation-triangle',
    weather: 'pi pi-cloud',
    pit_stop: 'pi pi-wrench',
    command: 'pi pi-send'
  };
  return iconMap[type] || 'pi pi-info-circle';
};

const getFilterIcon = (value) => {
  const iconMap = {
    all: 'pi pi-list',
    incident: 'pi pi-exclamation-triangle',
    pit_stop: 'pi pi-wrench',
    weather: 'pi pi-cloud',
    command: 'pi pi-send'
  };
  return iconMap[value] || 'pi pi-filter';
};
</script>

<style scoped>
.events-container {
  width: 100%;
  height: 100%;
  padding: 0;
}

.events-card {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.dark-mode .events-card {
  background: linear-gradient(135deg, #a85070 0%, #b8a030 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.events-card :deep(.p-card-body) {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0;
}

.events-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
  padding: 1rem;
  border-radius: 16px 16px 0 0;
  margin: 0;
}

.dark-mode .events-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #a85070 0%, #b8a030 100%);
}

.events-card :deep(.p-card-content) {
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

.card-header-buttons {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.view-toggle-btn,
.filter-toggle-btn {
  flex-shrink: 0;
}

.no-events {
  text-align: center;
  padding: 2rem 1rem;
  color: #6c757d;
}

.no-events i {
  font-size: 2rem;
  color: #dee2e6;
  margin-bottom: 0.5rem;
}

.no-events p {
  font-size: 0.95rem;
  font-style: italic;
}

.counters-grid {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.counter-card {
  background: var(--filter-content-bg);
  border-radius: 8px;
  flex: 1;
  padding: 0.6rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.counter-card:hover {
  border-color: #fa709a;
  box-shadow: 0 4px 12px rgba(250, 112, 154, 0.2);
  transform: translateY(-2px);
}

.dark-mode .counter-card:hover {
  border-color: #a85070;
  box-shadow: 0 4px 12px rgba(168, 80, 112, 0.3);
}

.counter-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  color: white;
  flex-shrink: 0;
}

.incident-icon {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
}

.repair-icon {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
}

.events-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.counter-data {
  flex: 1;
}

.counter-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 0.1rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.counter-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary, #2c3e50);
}

.high-value {
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

.filters-container {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  padding: 0.5rem;
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 8px;
}

.filter-btn {
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-btn:hover {
  transform: translateY(-2px);
}

.filter-btn.active {
  box-shadow: 0 4px 12px rgba(250, 112, 154, 0.4);
}

.filter-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 10px;
  font-size: 0.75rem;
  min-width: 20px;
  margin-left: 0.5rem;
}

.filter-btn.active .filter-count {
  background: rgba(255, 255, 255, 0.3);
}

.events-table-container {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #dee2e6;
}

.events-table {
  border-radius: 8px;
}

.event-time {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #6c757d;
  font-size: 0.8rem;
  font-family: monospace;
}

.event-time i {
  color: #fa709a;
}

.event-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.event-badge-incident {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
}

.event-badge-weather {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.event-badge-pit_stop {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
}

.event-badge-command {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.event-description {
  color: #2c3e50;
  font-weight: 500;
}

.event-row-incident {
  background-color: rgba(255, 107, 107, 0.05) !important;
}

.event-row-weather {
  background-color: rgba(79, 172, 254, 0.05) !important;
}

.event-row-pit_stop {
  background-color: rgba(40, 167, 69, 0.05) !important;
}

.event-row-command {
  background-color: rgba(102, 126, 234, 0.05) !important;
}

.no-filtered-events {
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
}

.no-filtered-events i {
  font-size: 2.5rem;
  color: #dee2e6;
  margin-bottom: 0.75rem;
}

.no-filtered-events p {
  font-size: 1rem;
  font-style: italic;
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
  position: sticky;
  top: 0;
  z-index: 1;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.875rem;
  border-bottom: 1px solid #f1f3f5;
}

:deep(.p-button) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .card-header-buttons {
    width: 100%;
    flex-wrap: wrap;
  }

  .card-header-buttons > button {
    flex: 1;
  }

  .counters-grid {
    flex-direction: column;
  }

  .filters-container {
    justify-content: center;
  }

  .events-table-container {
    overflow-x: auto;
  }
}

/* Dark mode overrides */
.dark-mode .filters-container,
.dark-mode .counter-label,
.dark-mode .counter-value,
.dark-mode .event-item,
.dark-mode .event-text {
  color: var(--text-primary);
}

.dark-mode .event-item {
  background: var(--filter-content-bg);
  border-color: var(--border-color);
}

.dark-mode .filters-container {
  background: var(--filter-content-bg);
}

.dark-mode .events-table :deep(.p-datatable-thead > tr > th) {
  background: var(--table-header-bg-start) !important;
  color: var(--table-header-text) !important;
  border-bottom-color: var(--table-border) !important;
}

.dark-mode .event-description {
  color: var(--text-primary);
}

.dark-mode .event-time {
  color: var(--text-secondary);
}

.dark-mode .events-table-container {
  border-color: var(--border-color);
}
</style>
