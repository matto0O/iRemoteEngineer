<script setup>
import EngineerPanel from './components/EngineerPanel.vue';
import { ref } from 'vue';

const websocketLink = ref(null);
const inputWebsocketLink = ref('');
const confirmWebsocketLink = () => {
  if (inputWebsocketLink.value) {
    websocketLink.value = inputWebsocketLink.value;
  } else {
    alert('Please enter a valid WebSocket link.');
  }
};
// wss://3dd4-185-164-143-35.ngrok-free.app/ws
</script>
<template>
  <main>
    <div v-if="!websocketLink">
      <div class="websocket-input">
        <input 
          type="text" 
          v-model="inputWebsocketLink" 
          placeholder="Enter WebSocket link"
          class="ws-input"
        />
        <button @click="confirmWebsocketLink" class="confirm-btn">Connect</button>
      </div>
    </div>
    <EngineerPanel v-else :socketAddress="websocketLink" />
  </main>
</template>