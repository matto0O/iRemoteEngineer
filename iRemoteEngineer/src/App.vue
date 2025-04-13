<script setup>
import { onMounted, computed } from 'vue';
import CarTracker from './components/CarTracker.vue';
import FuelAnalysis from './components/FuelAnalysis.vue';
import IncidentTracker from './components/IncidentTracker.vue';
import TyreDetails from './components/TyreDetails.vue';
import WeatherInfo from './components/WeatherInfo.vue';
import PitSettings from './components/PitSettings.vue';
import useWebSocketConnection from './composables/createSocket.js';

const { socket, isConnected } = useWebSocketConnection();

// For debugging
onMounted(() => {
  console.log("App mounted");
  console.log("Initial socket state:", socket.value);
  console.log("Initial connection state:", isConnected.value);
  
  // Check again after a short delay
  setTimeout(() => {
    console.log("Socket after timeout:", socket.value);
    console.log("Connection after timeout:", isConnected.value);
  }, 1000);
});

// Instead of using socket directly, we can wrap it safely
const safeSocket = computed(() => isConnected.value ? socket.value : null);
</script>

<template>
  <main>
    <div v-if="isConnected && safeSocket" class="component-container">
      <CarTracker :socket="safeSocket" />
      <FuelAnalysis :socket="safeSocket" />
      <TyreDetails :socket="safeSocket" />
      <WeatherInfo :socket="safeSocket" />
      <IncidentTracker :socket="safeSocket" />
      <PitSettings :socket="safeSocket" />
    </div>
    <div v-else class="loading-container">
      <p>Connecting to race data... (Connection status: {{ isConnected ? 'Connected' : 'Disconnected' }})</p>
    </div>
  </main>
</template>