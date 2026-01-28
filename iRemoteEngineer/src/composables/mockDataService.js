// Mock data service to simulate WebSocket updates
export class MockDataService {
  constructor() {
    this.listeners = [];
    this.intervalId = null;
    this.mockData = this.generateInitialMockData();
  }

  generateInitialMockData() {
    return {
      "lobby_name": "sdaf",
      "player_car_number": "11",
      "total_incidents": 4,
      "fast_repairs_used": 1,
      "cars": {
       "0": {
        "car_class_position": 0,
        "car_est_time": 57.671,
        "car_model_id": 136,
        "car_number": "0",
        "car_position": 0,
        "class_id": 11,
        "distance_pct": 0.987,
        "gap_leader": 0,
        "in_pit": true,
        "lap": -1,
        "team_name": "Pace Car",
        "user_name": "Pace Car"
       },
       "1": {
        "car_class_position": 1,
        "car_est_time": 62.282,
        "car_model_id": 195,
        "car_number": "1",
        "car_position": 11,
        "class_id": 4073,
        "distance_pct": 0.974,
        "gap_leader": 0.01,
        "in_pit": false,
        "lap": 0,
        "team_name": "Alex Horn",
        "user_name": "Alex Horn"
       },
       "2": {
        "car_class_position": 1,
        "car_est_time": 66.03,
        "car_model_id": 160,
        "car_number": "2",
        "car_position": 12,
        "class_id": 4012,
        "distance_pct": 0.955,
        "gap_leader": 0.011,
        "in_pit": false,
        "lap": 0,
        "team_name": "Alex Gustafson",
        "user_name": "Alex Gustafson"
       },
       "3": {
        "car_class_position": 3,
        "car_est_time": 62.316,
        "car_model_id": 112,
        "car_number": "3",
        "car_position": 10,
        "class_id": 4085,
        "distance_pct": 0.984,
        "gap_leader": 0.009,
        "in_pit": false,
        "lap": 0,
        "team_name": "Vicente Maestre",
        "user_name": "Vicente Maestre"
       },
       "4": {
        "car_class_position": 3,
        "car_est_time": 0.756,
        "car_model_id": 157,
        "car_number": "4",
        "car_position": 6,
        "class_id": 2268,
        "distance_pct": 0.016,
        "gap_leader": 0.005,
        "in_pit": false,
        "lap": 1,
        "team_name": "David LoVecchio",
        "user_name": "David LoVecchio"
       },
       "5": {
        "car_class_position": 2,
        "car_est_time": 62.186,
        "car_model_id": 146,
        "car_number": "5",
        "car_position": 9,
        "class_id": 4085,
        "distance_pct": 0.981,
        "gap_leader": 0.008,
        "in_pit": false,
        "lap": 0,
        "team_name": "Kim Berry",
        "user_name": "Kim Berry"
       },
       "6": {
        "car_class_position": 1,
        "car_est_time": 62.884,
        "car_model_id": 147,
        "car_number": "6",
        "car_position": 8,
        "class_id": 4085,
        "distance_pct": 0.992,
        "gap_leader": 0.007,
        "in_pit": false,
        "lap": 0,
        "team_name": "Dale Earnhardt Jr.",
        "user_name": "Dale Earnhardt Jr."
       },
       "7": {
        "car_class_position": 1,
        "car_est_time": 67.443,
        "car_model_id": 67,
        "car_number": "7",
        "car_position": 13,
        "class_id": 74,
        "distance_pct": 0.95,
        "gap_leader": 0.012,
        "in_pit": false,
        "lap": 0,
        "team_name": "John West",
        "user_name": "John West"
       },
       "8": {
        "car_class_position": 2,
        "car_est_time": 3.15,
        "car_model_id": 156,
        "car_number": "8",
        "car_position": 2,
        "class_id": 2708,
        "distance_pct": 0.074,
        "gap_leader": 0.001,
        "in_pit": false,
        "lap": 1,
        "team_name": "Greg Hill",
        "user_name": "Greg Hill"
       },
       "10": {
        "car_class_position": 3,
        "car_est_time": 2.4,
        "car_model_id": 173,
        "car_number": "10",
        "car_position": 3,
        "class_id": 2708,
        "distance_pct": 0.057,
        "gap_leader": 0.002,
        "in_pit": false,
        "lap": 1,
        "team_name": "Grant Reeve",
        "user_name": "Grant Reeve"
       },
       "11": {
        "car_class_position": 1,
        "car_est_time": 57.946,
        "car_model_id": 150,
        "car_number": "11",
        "car_position": 4,
        "class_id": 2268,
        "distance_pct": 0.941,
        "gap_leader": 0.003,
        "in_pit": false,
        "lap": 0,
        "team_name": "Mateusz Wozniak3",
        "user_name": "Mateusz Wozniak3"
       },
       "14": {
        "car_class_position": 4,
        "car_est_time": 0.408,
        "car_model_id": 189,
        "car_number": "14",
        "car_position": 7,
        "class_id": 2268,
        "distance_pct": 0.009,
        "gap_leader": 0.006,
        "in_pit": false,
        "lap": 1,
        "team_name": "Kevin Bobbitt",
        "user_name": "Kevin Bobbitt"
       },
       "30": {
        "car_class_position": 2,
        "car_est_time": 0.668,
        "car_model_id": 135,
        "car_number": "30",
        "car_position": 5,
        "class_id": 2268,
        "distance_pct": 0.014,
        "gap_leader": 0.004,
        "in_pit": false,
        "lap": 1,
        "team_name": "Tyler Holhubner",
        "user_name": "Tyler Holhubner"
       },
       "77": {
        "car_class_position": 1,
        "car_est_time": 3.212,
        "car_model_id": 188,
        "car_number": "77",
        "car_position": 1,
        "class_id": 2708,
        "distance_pct": 0.077,
        "gap_leader": 0,
        "in_pit": false,
        "lap": 1,
        "team_name": "Sarah Ohanian",
        "user_name": "Sarah Ohanian"
       }
      },
      "lap_history": [
        {
          "driver_name": "Mateusz Woźniak",
          "fuel_consumed": 3.4,
          "incidents_incurred": 2,
          "lap_time": "1:34.990"
        },
        {
          "driver_name": "Tanguy Francheateau",
          "fuel_consumed": 3.2,
          "incidents_incurred": 1,
          "lap_time": "1:34.021"
        },
        {
          "driver_name": "Tanguy Francheateau",
          "fuel_consumed": 3.2,
          "incidents_incurred": 1,
          "lap_time": "1:32.021"
        },
        {
          "driver_name": "Mateusz Woźniak",
          "fuel_consumed": 3.3,
          "incidents_incurred": 0,
          "lap_time": "1:33.211"
        },
        {
          "driver_name": "Mateusz Woźniak",
          "fuel_consumed": 3.1,
          "incidents_incurred": 3,
          "lap_time": "1:31.551"
        }
      ],
      "change_timestamp": "20251224T112018",
      "expiry_timestamp": 1766661618,
      "session_info": {
       "car_name": null,
       "session_id": 0,
       "split_time_info": {
        "1": 0,
        "2": 60.79
       },
       "subsession_id": 0,
       "track_config": "Speed Circuit Medium",
       "track_name": "Circuito de Navarra"
      },
      "tyres": {
       "front_left": {
        "left_carcass_temp": 56.8,
        "left_tread_remaning": 100,
        "middle_carcass_temp": 66.8,
        "middle_tread_remaning": 20,
        "right_carcass_temp": 46.8,
        "right_tread_remaning": 50
       },
       "front_right": {
        "left_carcass_temp": 76.8,
        "left_tread_remaning": 90,
        "middle_carcass_temp": 86.8,
        "middle_tread_remaning": 80,
        "right_carcass_temp": 16.8,
        "right_tread_remaning": 70
       },
       "rear_left": {
        "left_carcass_temp": 86.8,
        "left_tread_remaning": 60,
        "middle_carcass_temp": 96.8,
        "middle_tread_remaning": 50,
        "right_carcass_temp": 46.8,
        "right_tread_remaning": 75
       },
       "rear_right": {
        "left_carcass_temp": 100.8,
        "left_tread_remaning": 100,
        "middle_carcass_temp": 46.8,
        "middle_tread_remaning": 100,
        "right_carcass_temp": 46.8,
        "right_tread_remaning": 100
       }
      },
      "weather": {
       "air_temp": 19.3,
       "declared_wet": false,
       "precipitation": 0,
       "track_temp": 33.3,
       "track_wetness": "Dry",
       "wind_direction": "East (89.1°)",
       "wind_speed": 15.5
      },
      "fuel": {
        "current_fuel_level": 45.5,
        "burn_history": [3.2, 3.4, 3.1, 3.3, 3.2],
        "average_burn": 3.24,
        "avg_laps_left_estimate": 14.04,
        "avg_target_laps": 14,
        "avg_floor_laps": 14,
        "avg_floor_lap_target": 45.36,
        "avg_ceil_laps": 15,
        "avg_ceil_lap_target": 48.60,
        "avg_one_lap_less_left": 13,
        "avg_one_lap_less_target": 42.12,
        "avg_one_lap_more_left": 15,
        "avg_one_lap_more_target": 48.60,
        "last_laps_left_estimate": 14.22,
        "last_target_laps": 14,
        "last_floor_laps": 14,
        "last_floor_lap_target": 44.80,
        "last_ceil_laps": 15,
        "last_ceil_lap_target": 48.00,
        "last_one_lap_less_left": 13,
        "last_one_lap_less_target": 41.60,
        "last_one_lap_more_left": 15,
        "last_one_lap_more_target": 48.00
      },
      "event": [
        {
          "time": "2025-01-07, 14:23:45",
          "type": "incident",
          "description": "Contact with wall - 2x incident points"
        },
        {
          "time": "2025-01-07, 14:28:12",
          "type": "pit_stop",
          "description": "Pit stop completed - 4 tires changed, 25.5L fuel added"
        },
        {
          "time": "2025-01-07, 14:35:22",
          "type": "weather",
          "description": "Track condition changed to Damp"
        },
        {
          "time": "2025-01-07, 14:38:55",
          "type": "command",
          "description": "Executed commands: lf, rf, fuel.50"
        },
        {
          "time": "2025-01-07, 14:42:10",
          "type": "incident",
          "description": "Off track - 1x incident point"
        }
      ]
     };
  }

  // Simulate WebSocket connection
  connect() {
    console.log("Mock WebSocket connected");
    this.connected = true;
  }

  // Add listener (mimics WebSocket onmessage)
  set onmessage(callback) {
    this.listeners = [callback];

    // Emit initial data when handler is attached
    if (this.connected) {
      setTimeout(() => {
        this.emit(this.mockData);
      }, 50);
    }
  }

  // Emit data to all listeners
  emit(data) {
    this.listeners.forEach((callback) => {
      if (callback) {
        callback({ data: JSON.stringify(data) });
      }
    });
  }

  // Send command (mock)
  send(command) {
    console.log("Mock command sent:", command);
    
    // Simulate command response
    try {
      const parsedCommand = JSON.parse(command);
      if (parsedCommand.action === 'subscribe') {
        console.log("Mock subscription confirmed for token:", parsedCommand.token);
      }
    } catch (e) {
      // Just a regular command string
      console.log("Mock pit command:", command);
    }
  }

  // Disconnect
  disconnect() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    this.listeners = [];
    console.log("Mock WebSocket disconnected");
  }

  // Properties to match WebSocket API
  get readyState() {
    return 1; // OPEN
  }
}

// Export WebSocket constant for compatibility
export const WebSocket = {
  OPEN: 1,
  CONNECTING: 0,
  CLOSING: 2,
  CLOSED: 3,
};