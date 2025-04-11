// src/composables/useRaceData.js
import { ref, onMounted, onBeforeUnmount } from 'vue'

export default function useRaceData(wsUrl = 'ws://localhost:8000/ws') {
  const data = ref({
    player_car_number: null,
    cars: [],
    fuel_analysis: {}
  })
  
  const isConnected = ref(false)
  const connectionError = ref(null)
  let socket = null

  const connect = () => {
    if (socket) return

    socket = new WebSocket(wsUrl)
    
    socket.onopen = () => {
      isConnected.value = true
      connectionError.value = null
      console.log("WebSocket connection established")
    }

    socket.onmessage = (event) => {
      try {
        const data_json = JSON.parse(event.data)
        // Update main data
        data.value = data_json
        console.log("WebSocket data received")
      } catch (error) {
        console.error("Error parsing WebSocket data:", error)
      }
    }

    socket.onerror = (error) => {
      connectionError.value = "WebSocket connection error"
      console.error("WebSocket error:", error)
    }

    socket.onclose = () => {
      isConnected.value = false
      console.log("WebSocket connection closed")
    }
  }

  const disconnect = () => {
    if (socket) {
      socket.close()
      socket = null
    }
  }

  // Auto-connect when mounted
  onMounted(() => {
    connect()
  })

  // Clean up connection when component unmounts
  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    data,
    isConnected,
    connectionError,
    connect,
    disconnect
  }
}