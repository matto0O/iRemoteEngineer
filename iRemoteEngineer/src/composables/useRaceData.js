import { ref } from 'vue'

// Singleton instance - stores the data and socket reference
let instance = null
let currentSocket = null
let currentAuthToken = null

export default function useRaceData(socket, authToken = null) {
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
    // Update authToken if a new one is provided
    if (authToken !== null && authToken !== currentAuthToken) {
      currentAuthToken = authToken
    }
    return instance
  }

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
    // First, call the original handler if it exists (for subscription confirmations, etc.)
    if (typeof originalOnMessage === 'function') {
      originalOnMessage(event)
    }

    try {
      const data_json = JSON.parse(event.data)

      // Skip messages that are just confirmations/errors (not data updates)
      if (data_json.message || data_json.error) {
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
    } else if (socket && typeof socket.send === 'function') {
      // For demo socket
      socket.send(message)
    } else {
      console.warn("Cannot send command, socket not ready. ReadyState:", socket?.readyState)
    }
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