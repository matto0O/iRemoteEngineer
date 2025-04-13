// src/composables/createSocket.js
import { ref, onMounted, onBeforeUnmount, shallowRef } from 'vue'

export default function useWebSocketConnection(wsUrl = 'ws://localhost:8000/ws') {
  // Use shallowRef for non-primitive objects like WebSocket
  const socket = shallowRef(null)
  const isConnected = ref(false)
  const connectionError = ref(null)

  const connect = () => {
    if (socket.value) return socket.value

    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      isConnected.value = true
      connectionError.value = null
      console.log("WebSocket connection established")
    }

    ws.onerror = (error) => {
      connectionError.value = "WebSocket connection error"
      console.error("WebSocket error:", error)
    }

    ws.onclose = () => {
      isConnected.value = false
      console.log("WebSocket connection closed")
    }
    
    // Important: set the ref's value to trigger reactivity
    socket.value = ws
    return ws
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
  }

  // Auto-connect when mounted
  onMounted(() => {
    console.log("Component mounted, connecting socket...")
    connect()
  })

  // Clean up connection when component unmounts
  onBeforeUnmount(() => {
    console.log("Component unmounting, disconnecting socket...")
    disconnect()
  })

  return {
    socket,
    isConnected,
    connectionError,
    connect,
    disconnect
  }
}