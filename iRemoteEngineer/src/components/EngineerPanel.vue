<template>
  <div v-if="isConnected && safeSocket" class="component-container">
      <CarTracker :socket="safeSocket" />
      <FuelAnalysis :socket="safeSocket" />
      <TyreDetails :socket="safeSocket" />
      <WeatherInfo :socket="safeSocket" />
      <IncidentTracker :socket="safeSocket" />
      <PitSettings :socket="safeSocket" />
    </div>
    <div v-else class="loading-container">
      <p>Connecting to race data...</p>
    </div>
</template>

<script setup>
import CarTracker from './CarTracker.vue';
import FuelAnalysis from './FuelAnalysis.vue';
import IncidentTracker from './IncidentTracker.vue';
import TyreDetails from './TyreDetails.vue';
import WeatherInfo from './WeatherInfo.vue';
import PitSettings from './PitSettings.vue';
import useWebSocketConnection from '../composables/createSocket.js';
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
  socketAddress: {
    type: String,
    required: true
  }
})

const { socket, isConnected, connect } = useWebSocketConnection(props.socketAddress);

const safeSocket = computed(() => isConnected.value ? socket.value : null);

// Attempt to reconnect if connection fails
const reconnectInterval = ref(null);

onMounted(() => {
  reconnectInterval.value = setInterval(() => {
    if (!isConnected.value) {
      connect();
    }
  }, 5000); // Try reconnecting every 5 seconds
});

onBeforeUnmount(() => {
  if (reconnectInterval.value) {
    clearInterval(reconnectInterval.value);
  }
});
</script>