import { ref } from 'vue'

// Singleton instance - stores the data and socket reference
let instance = null
let currentSocket = null
let currentAuthToken = null

export default function useRaceData(socket, authToken = null) {
  console.log("urd", authToken)
  if (!socket) {
    return {
      data: ref({
        player_car_number: null,
        cars: {},
        fuel: {},
        weather_data: {},
        session_info: {},
        event: [],
        lap_history: [],
        tyres: {},
        total_incidents: 0,
        fast_repairs_used: 0
      }),
      sendCommand: () => {
        console.warn("Socket not provided")
      }
    }
  }

  // If instance exists and socket hasn't changed, return existing instance
  if (instance && currentSocket === socket) {
    console.log("Returning existing useRaceData instance")
    // Update authToken if a new one is provided
    if (authToken !== null && authToken !== currentAuthToken) {
      currentAuthToken = authToken
    }
    return instance
  }

  // If socket has changed or no instance exists, create/recreate
  console.log("Creating new useRaceData instance with socket:", socket)

  // Store the authToken (prefer non-null value)
  if (authToken !== null) {
    currentAuthToken = authToken
  }

  // Race data state
  const data = ref({
    player_car_number: null,
    cars: {},
    fuel: {},
    weather_data: {},
    session_info: {},
    event: [],
    lap_history: [],
    tyres: {},
    total_incidents: 0,
    fast_repairs_used: 0
  })

  // Setup the message handler
  // Store the original onmessage if it exists
  const originalOnMessage = socket.onmessage

  socket.onmessage = (event) => {
    console.log("[useRaceData] Received WebSocket message")

    // First, call the original handler if it exists (for subscription confirmations, etc.)
    if (typeof originalOnMessage === 'function') {
      originalOnMessage(event)
    }

    try {
      const data_json = JSON.parse(event.data)
      console.log("[useRaceData] Parsed message, keys:", Object.keys(data_json))

      // Skip messages that are just confirmations/errors (not data updates)
      if (data_json.message || data_json.error) {
        console.log("[useRaceData] Skipping confirmation/error message:", data_json)
        return
      }

      // Update main data - normalize field names
      // Real WebSocket uses: weather, event
      // Components expect: weather_data, event
      const hasRaceData = data_json.cars || data_json.fuel || data_json.weather

      if (hasRaceData) {
        data.value = {
          player_car_number: data_json.player_car_number ?? data.value.player_car_number,
          cars: data_json.cars ?? data.value.cars,
          fuel: data_json.fuel ?? data.value.fuel,
          weather_data: data_json.weather ?? data.value.weather_data,
          session_info: data_json.session_info ?? data.value.session_info,
          event: data_json.event ?? data.value.event,
          lap_history: data_json.lap_history ?? data.value.lap_history,
          tyres: data_json.tyres ?? data.value.tyres,
          total_incidents: data_json.total_incidents ?? data.value.total_incidents,
          fast_repairs_used: data_json.fast_repairs_used ?? data.value.fast_repairs_used
        }
      }
    } catch (error) {
      console.error("[useRaceData] Error parsing WebSocket data:", error, "Raw data:", event.data)
    }
  }

  const sendCommand = (commandString) => {
    if (!currentAuthToken) {
      console.warn("Cannot send command: no auth token available")
      return
    }

    const message = JSON.stringify({
      action: 'sendToServer',
      token: currentAuthToken,
      command: commandString
    })

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message)
      console.log("Command sent to AWS WebSocket:", commandString)
    } else if (socket && typeof socket.send === 'function') {
      // For mock socket
      socket.send(message)
      console.log("Command sent (mock):", commandString)
    } else {
      console.warn("Cannot send command, socket not ready. ReadyState:", socket?.readyState)
    }
  }

  // Check socket connection status
  console.log("Socket ready state:", socket.readyState)
  if (typeof WebSocket !== 'undefined') {
    console.log("WebSocket.OPEN constant:", WebSocket.OPEN)
  }

  // Create/update the instance
  instance = {
    data,
    sendCommand
  }

  // Store current socket reference
  currentSocket = socket

  return instance
}