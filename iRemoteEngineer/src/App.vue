<script setup>
import EngineerPanel from './components/EngineerPanel.vue';
import { ref } from 'vue';
// Import PrimeVue components
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Message from 'primevue/message';

const websocketLink = ref(null);
const inputWebsocketLink = ref('');

const confirmWebsocketLink = () => {
  if (inputWebsocketLink.value) {
    websocketLink.value = inputWebsocketLink.value;
  }
};

// Example WebSocket URL: wss://3dd4-185-164-143-35.ngrok-free.app/ws
</script>

<template>
  <main class="p-4">
    <div v-if="!websocketLink" class="flex justify-content-center">
      <Card class="connection-card">
        <template #title>
          <div class="flex align-items-center">
            <i class="pi pi-link mr-2"></i>
            <span>Race Engineer Console</span>
          </div>
        </template>
        <template #subtitle>
          Connect to your racing telemetry WebSocket
        </template>
        <template #content>
          <div class="connection-form">
            <Message severity="info" class="mb-3">
              Your link likely looks like wss://{session_address}.ngrok-free.app/ws
            </Message>
            
            <div class="p-inputgroup">
              <span class="p-inputgroup-addon">
                <i class="pi pi-wifi"></i>
              </span>
              <InputText 
                v-model="inputWebsocketLink" 
                placeholder="Enter WebSocket link"
                class="w-full"
              />
              <Button 
                @click="confirmWebsocketLink" 
                icon="pi pi-check" 
                label="Connect"
                class="p-button-success"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>
    <EngineerPanel v-else :socketAddress="websocketLink" />
  </main>
</template>

<style>
/* Import PrimeVue theme - add this to your main.js or index.js */
/* 
import PrimeVue from 'primevue/config';
import 'primevue/resources/themes/lara-light-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
*/

.connection-card {
  max-width: 600px;
  width: 100%;
  margin-top: 2rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.connection-form {
  padding: 1rem 0;
}

main {
  min-height: 100vh;
  background-color: #f8f9fa;
}

@media (max-width: 768px) {
  .connection-card {
    margin: 1rem;
    width: auto;
  }
}
</style>