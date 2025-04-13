<template>
    <div class="incident-container">
      <h3>Incident Timeline</h3>
      
      <div v-if="totalIncidents === 0" class="no-incidents">
        No incidents recorded
      </div>

      <div v-else-if="incidents.length === 0" class="no-incidents">
        No new incidents recorded
      </div>
      
      <div v-else class="incident-timeline">
        <div v-for="(incident, index) in incidents" :key="index" class="incident-item">
          <div class="incident-time">{{ formatTime(incident[0]) }}</div>
          <div class="incident-count">
            <span v-if="incident[1] === 1" class="incident-number-1x" >+{{ incident[1] }}</span>
            <span v-else-if="incident[1] === 2" class="incident-number-2x" >+{{ incident[1] }}</span>
            <span v-else class="incident-number-4x" >+{{ incident[1] }}</span>
            <span class="incident-text">{{ incident[1] > 1 ? 'incidents' : 'incident' }}</span>
          </div>
        </div>
      </div>
      <div class="incident-total">
        <span>Total Incidents: </span>
        <span class="total-number" :class="{'high-incidents': totalIncidents > 15}">
          {{ totalIncidents }}
        </span>
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
})
  
  // Get shared race data from composable
  const { data } = useRaceData(props.socket);
  
  // Watch race data for incident information
  const incidentData = computed(() => {
    return data.value?.incidents || {
      total_incidents: 0,
      incidents: []
    };
  });
  
  // Get total incidents
  const totalIncidents = computed(() => {
    return incidentData.value.total_incidents || 0;
  });
  
  // Get incident list
  const incidents = computed(() => {
    return incidentData.value.incidents || [];
  });
  
  // Format the timestamp to be more readable
  const formatTime = (timestamp) => {
    // If timestamp includes date (like "12/04/2025, 14:32:45")
    // Extract just the time portion for display
    if (timestamp.includes(',')) {
      return timestamp.split(', ')[1];
    }
    return timestamp;
  };
  </script>
  
  <style scoped>
  .incident-container {
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
  
  .no-incidents {
    text-align: center;
    color: #666;
    padding: 1rem 0;
    font-style: italic;
  }
  
  .incident-timeline {
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 1rem;
    border: 1px solid #eee;
    border-radius: 4px;
  }
  
  .incident-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #eee;
  }
  
  .incident-item:last-child {
    border-bottom: none;
  }
  
  .incident-time {
    color: #666;
    font-size: 0.85rem;
  }
  
  .incident-count {
    display: flex;
    align-items: center;
  }
  
  .incident-number-1x {
    background-color: #e2c234;
    color: rgb(255, 255, 255);
    border-radius: 12px;
    padding: 0.1rem 0.5rem;
    font-weight: bold;
    margin-right: 0.3rem;
  }

  .incident-number-2x {
    background-color: #db8400;
    color: rgb(255, 255, 255);
    border-radius: 12px;
    padding: 0.1rem 0.5rem;
    font-weight: bold;
    margin-right: 0.3rem;
  }

  .incident-number-4x {
    background-color: #b22222;
    color: white;
    border-radius: 12px;
    padding: 0.1rem 0.5rem;
    font-weight: bold;
    margin-right: 0.3rem;
  }
  
  .incident-text {
    color: #666;
    font-size: 0.85rem;
  }
  
  .incident-total {
    font-weight: bold;
    text-align: right;
    padding: 0.5rem 1rem;
    background-color: #f1f1f1;
    border-radius: 4px;
  }
  
  .total-number {
    font-size: 1.1rem;
  }
  
  .high-incidents {
    color: #cc0000;
  }
  </style>