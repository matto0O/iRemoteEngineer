// src/composables/useRaceData.js
import { ref } from 'vue'

export default function useRaceData(socket) {
  if (!socket) {
    return {
      data: null,
      sendCommand: () => {
        console.warn("Socket not provided")
      }
    }
  }

  // Race data state
  const data = ref({
    player_car_number: null,
    cars: [],
    fuel_analysis: {}
  })

  // Setup the message handler
  const originalOnMessage = socket.onmessage
  socket.onmessage = (event) => {
    try {
      const data_json = JSON.parse(event.data)
      // Update main data
      data.value = data_json
    } catch (error) {
      console.error("Error parsing WebSocket data:", error)
    }
    
    // Call the original handler if it exists
    if (typeof originalOnMessage === 'function') {
      originalOnMessage(event)
    }
  }

  const sendCommand = (commandString) => {
    if (socket && isConnected.value) {
      socket.send(commandString)
      console.log("Command sent:", commandString)
    } else {
      console.warn("Cannot send command, socket not connected")
      console.log(socket, isConnected.value)
    }
  }

  return {
    data,
    sendCommand
  }
}