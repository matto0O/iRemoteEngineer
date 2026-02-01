// src/composables/createSocket.js
import { ref, onMounted, onBeforeUnmount, shallowRef } from 'vue'
import { MockDataService } from './mockDataService.js'

export default function useWebSocketConnection(lobby_name = '', authToken = '', useMockMode = false) {
  // Use shallowRef for non-primitive objects like WebSocket
  const socket = shallowRef(null)
  const isConnected = ref(false)
  const connectionError = ref(null)

  const connect = () => {
    
    if (socket.value) {
      return socket.value;
    }

    // If in mock mode, use MockDataService instead of WebSocket
    if (useMockMode) {
      console.log("Using mock data service");
      const mockService = new MockDataService();
      
      // Set socket first
      socket.value = mockService;
      
      // Start mock data updates
      mockService.connect();
      
      // Set connected immediately for mock mode
      isConnected.value = true;
      connectionError.value = null;
      
      return mockService;
    }

    // Validate that we have a token before attempting connection
    if (!authToken) {
      connectionError.value = "No authentication token provided"
      console.error("Cannot connect: No authentication token")
      return null
    }

    const ws = new WebSocket(import.meta.env.VITE_WEBSOCKET_URL)
    
    ws.onopen = () => {
      isConnected.value = true
      connectionError.value = null
      
      // Send subscription message with JWT token instead of lobby/team directly
      ws.send(JSON.stringify({ 
        action: 'subscribe', 
        token: authToken 
      }))
    }

    ws.onerror = (error) => {
      connectionError.value = "WebSocket connection error"
      console.error("WebSocket error:", error)
    }

    ws.onclose = (event) => {
      isConnected.value = false
      
      // Check if it was an authentication error
      if (event.code === 1008 || event.reason?.includes('auth')) {
        connectionError.value = "Authentication failed - invalid or expired token"
      }
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        
        // Handle errors from the server
        if (message.error) {
          console.error("Server error:", message.error)
          connectionError.value = message.error
        }
      } catch (e) {
        console.error("Error parsing message:", e)
      }
    }
    
    // Important: set the ref's value to trigger reactivity
    socket.value = ws
    return ws
  }

  const disconnect = () => {
    if (socket.value) {
      if (useMockMode) {
        socket.value.disconnect()
      } else {
        socket.value.close()
      }
      socket.value = null
      isConnected.value = false
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
    socket,
    isConnected,
    connectionError,
    connect,
    disconnect
  }
}