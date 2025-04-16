<template>
  <div class="events-container">
    <h3>Race Events</h3>
    
    <div v-if="events.length === 0" class="no-events">
      No events recorded
    </div>
    
    <div v-else class="events-table-container">
      <table class="events-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(event, index) in sortedEvents" :key="index" :class="`event-type-${event.type}`">
            <td class="event-time">{{ formatTime(event.time) }}</td>
            <td class="event-type">
              <span class="event-badge" :class="`event-badge-${event.type}`">
                {{ formatEventType(event.type) }}
              </span>
            </td>
            <td class="event-description">{{ event.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="counters-container">
      <div class="counter-item">
        <span class="counter-label">Total Incidents:</span>
        <span class="counter-value" :class="{'high-value': totalIncidents > 15}">
          {{ totalIncidents }}
        </span>
      </div>
      <div class="counter-item">
        <span class="counter-label">Fast Repairs Used:</span>
        <span class="counter-value" :class="{'high-value': fastRepairsUsed > 1}">
          {{ fastRepairsUsed }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import useRaceData from '@/composables/useRaceData';

const props = defineProps({
  socket: {
    type: Object,
    required: true
  }
});

// Get shared race data from composable
const { data } = useRaceData(props.socket);

// Get events from race data
const events = computed(() => {
  return data.value?.events || [];
});

// Sort events to show newest at the top
const sortedEvents = computed(() => {
  return [...events.value].reverse();
});

// Get total incidents count
const totalIncidents = computed(() => {
  return data.value?.total_incidents || 0;
});

// Get fast repairs used count
const fastRepairsUsed = computed(() => {
  return data.value?.fast_repairs_used || 0;
});

// Format the timestamp to be more readable
const formatTime = (timestamp) => {
  // If timestamp includes date (like "12/04/2025, 14:32:45")
  // Extract just the time portion for display
  if (timestamp && timestamp.includes(',')) {
    return timestamp.split(', ')[1];
  }
  return timestamp || '';
};

// Format event type for display
const formatEventType = (type) => {
  if (!type) return '';
  
  const typeMap = {
    incident: 'Incident',
    weather: 'Weather',
    pit_stop: 'Pit Stop',
    commands: 'Command'
  };
  
  return typeMap[type] || type.charAt(0).toUpperCase() + type.slice(1);
};
</script>

<style scoped>
.events-container {
  max-width: 800px;
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

.no-events {
  text-align: center;
  color: #666;
  padding: 1rem 0;
  font-style: italic;
}

.events-table-container {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 1rem;
  border: 1px solid #eee;
  border-radius: 4px;
}

.events-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.events-table th {
  background-color: #f1f1f1;
  padding: 0.6rem;
  text-align: left;
  position: sticky;
  top: 0;
  z-index: 1;
  border-bottom: 2px solid #ddd;
}

.events-table td {
  padding: 0.6rem;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

.events-table th:nth-child(1),
.events-table td:nth-child(1) {
  width: 20%;
}

.events-table th:nth-child(2),
.events-table td:nth-child(2) {
  width: 20%;
}

.events-table th:nth-child(3),
.events-table td:nth-child(3) {
  width: 60%;
}

.event-time {
  color: #666;
  font-size: 0.85rem;
}

.event-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.event-badge-incident {
  background-color: #b22222;
  color: white;
}

.event-badge-weather {
  background-color: #1e90ff;
  color: white;
}

.event-badge-pit_stop {
  background-color: #228b22;
  color: white;
}

.event-badge-command {
  background-color: #9370db;
  color: white;
}

.event-type-incident {
  background-color: rgba(178, 34, 34, 0.05);
}

.event-type-weather {
  background-color: rgba(147, 112, 219, 0.05);
}

.event-type-pit_stop {
  background-color: rgba(34, 139, 34, 0.05);
}

.counters-container {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  background-color: #f1f1f1;
  border-radius: 4px;
  padding: 0.8rem 1rem;
}

.counter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.counter-label {
  font-weight: 500;
}

.counter-value {
  font-size: 1.1rem;
  font-weight: bold;
}

.high-value {
  color: #cc0000;
}
</style>