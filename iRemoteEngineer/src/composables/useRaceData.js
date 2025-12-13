import { ref } from 'vue'

// Singleton instance
let instance = null

export default function useRaceData(socket) {
  // Return existing instance if available
  if (instance) {
    return instance
  }

  if (!socket) {
    return {
      data: ref(null),
      sendCommand: () => {
        console.warn("Socket not provided")
      }
    }
  }

  console.log("Creating new useRaceData instance") // Debug log

  // Race data state
  const data = ref({
    player_car_number: null,
    cars: [],
    fuel_analysis: {},
    weather: {} // Ensure weather is included
  })

  // Setup the message handler ONLY ONCE
  const originalOnMessage = socket.onmessage
  socket.onmessage = (event) => {
    console.log("WebSocket message received:", event) // Debug log
    try {
      const data_json = JSON.parse(event.data)
      console.log("Received WebSocket data:", data_json) // This should now work
      
      // Update main data
      data.value = data_json
      console.log("Data updated:", data.value) // Additional debug
    } catch (error) {
      console.error("Error parsing WebSocket data:", error, "Raw data:", event.data)
    }
    
    // Call the original handler if it exists
    if (typeof originalOnMessage === 'function') {
      originalOnMessage(event)
    }
  }

  const sendCommand = (commandString) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(commandString)
      console.log("Command sent:", commandString)
    } else {
      console.warn("Cannot send command, socket not connected or not ready. ReadyState:", socket?.readyState)
    }
  }

  // Check socket connection status
  console.log("Socket ready state:", socket.readyState)
  console.log("WebSocket.OPEN constant:", WebSocket.OPEN)

  // Create the instance
  instance = {
    data,
    sendCommand
  }

  return instance
}