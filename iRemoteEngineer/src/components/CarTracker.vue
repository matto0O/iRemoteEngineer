<template>
  <div class="car-track-container">
    <!-- Track Strip -->
    <div class="track-strip">
      <div
        v-for="car in filteredCars"
        :key="car.id"
        class="car-marker"
        :style="{
          left: car.distance_pct * 100 + '%',
          backgroundColor: getClassColor(car.class_id),
          top: getClassOffset(car.class_id),
          zIndex: car.id === hoveredCarId ? 10 : 1
        }"
        :class="{ 'player-car': car.id === data.player_car_idx }"
        @mouseenter="hoveredCarId = car.id"
        @mouseleave="hoveredCarId = null"
        @click="selectCar(car)"
      >
        {{ car.car_number }}
      </div>
    </div>
    <div style="height: 50px;"></div>
    <!-- Class Filter -->
    <div class="filter">
      <label>Show class:</label>
      <ButtonGroup>
      <Button
        v-for="classId in uniqueClassIds"
        :key="classId"
        :label="'Class ' + classId"
        :class="{ 'p-button-outlined': !enabledClasses.includes(classId) }"
        :style="{ 
          backgroundColor: enabledClasses.includes(classId) ? getClassColor(classId) : '#d3d3d3', 
          color: enabledClasses.includes(classId) ? 'white' : 'black',
          border: '1px solid black'
        }"
        @click="toggleClass(classId)"
      ></Button>
      </ButtonGroup>
    </div>

    <!-- Selected Car Info -->
    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
      <div 
        v-for="car in selectedCars" 
        :key="car.car_number" 
        class="car-info"
        :style="{ borderLeft: '4px solid ' + getClassColor(car.class_id) }"
      >
        <div class="car-info-header">
          <h4 :style="{ color: getClassColor(car.class_id) }">Car #{{ car.car_number }}
            <button @click="selectCar(car)" class="close-btn" style="float: right; margin-left: auto;">×</button>
          </h4>
          
        </div>
        <p><strong>Car Model:</strong> {{ car.car_model_id }}</p>
        <p><strong>Class:</strong> {{ car.class_id }}</p>
        <p><strong>Distance %:</strong> {{ (car.distance_pct * 100).toFixed(1) }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import ButtonGroup from 'primevue/buttongroup'
import Button from 'primevue/button'

const data = ref({
  player_car_idx: null,
  cars: [],
  fuel_analysis: {}
})

const enabledClasses = ref([])
const hoveredCarId = ref(null)
const selectedCars = ref([])

let socket = null

const classColors = [
  "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
  "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

const classColorsMapping = {}
const classOffsetsMapping = {}

const CLASS_OFFSET_MULTIPLIER = 15

onMounted(() => {
  socket = new WebSocket('ws://localhost:8000/ws')

  socket.onmessage = (event) => {
    const data_json = JSON.parse(event.data)

    // Update main data
    data.value = data_json

    // Sync selected car info
    selectedCars.value = selectedCars.value.map(oldCar => {
      const updated = data_json.cars.find(c => c.car_number === oldCar.car_number)
      return updated || oldCar
    })

    // Initialize enabled classes if needed
    if (enabledClasses.value.length === 0) {
      const classes = new Set(data_json.cars.map(car => car.class_id))
      enabledClasses.value = Array.from(classes).sort((a, b) => a - b)
    }
  }

  socket.onclose = () => {
    console.log("WebSocket connection closed")
  }
})

onBeforeUnmount(() => {
  if (socket) socket.close()
})

const getClassColor = (classId) => {
  if (classColorsMapping[classId] === undefined) {
    classColorsMapping[classId] = Object.keys(classColorsMapping).length
  }
  return classColors[classColorsMapping[classId] % classColors.length]
}

const getClassOffset = (classId) => {
  if (classOffsetsMapping[classId] === undefined) {
    classOffsetsMapping[classId] = Object.keys(classOffsetsMapping).length
  }
  // Position cars relative to the top of the track instead of bottom
  // Use a smaller offset to keep cars closer to the t`rack
  const classOrder = classOffsetsMapping[classId]
  return `${classOrder % 2 == 1 ? "" : "-1"}${(classOrder / 2) * CLASS_OFFSET_MULTIPLIER}px`
}

const uniqueClassIds = computed(() => {
  const classes = new Set(data.value.cars.map(car => car.class_id))
  return Array.from(classes).sort((a, b) => a - b)
})

const filteredCars = computed(() => {
  return enabledClasses.value.length === 0
    ? data.value.cars
    : data.value.cars.filter(car => enabledClasses.value.includes(car.class_id))
})

const toggleClass = (classId) => {
  const index = enabledClasses.value.indexOf(classId)
  if (index === -1) {
    enabledClasses.value.push(classId)
    // Keep the array sorted
    enabledClasses.value.sort((a, b) => a - b)
  } else {
    enabledClasses.value.splice(index, 1)
  }
}

const selectCar = (car) => {
  const existingCarIndex = selectedCars.value.findIndex(selectedCar => selectedCar.car_number === car.car_number);
  if (existingCarIndex !== -1) {
    selectedCars.value.splice(existingCarIndex, 1);
  } else {
    selectedCars.value.push(car);
  }
}
</script>

<style scoped>
.car-track-container {
  margin: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  padding-top: 60px; /* Add padding to accommodate car markers above the track */
}

.track-strip {
  position: relative;
  height: 8px;
  background-color: #ccc;
  border-radius: 4px;
  overflow: visible;
}

.car-marker {
  position: absolute;
  transform: translateX(-50%);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: white;
  font-size: 13px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
  transition: left 0.5s ease, transform 0.2s ease, z-index 0.2s;
  cursor: pointer;
}

.car-marker:hover {
  transform: translateX(-50%) scale(1.2);
}

.player-car {
  border: 3px solid gold;
  box-shadow: 0 0 6px gold;
}

.filter {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.car-info {
  width: 200px;
  margin-top: 15px;
  padding: 12px;
  background: #fafafa;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
  flex-grow: 0;
  flex-shrink: 0;
}
.fixed-width-value {
display: inline-block;
min-width: 50px;
}

.car-info h4 {
  margin: 0 0 8px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 0 4px;
  line-height: 1;
}
</style>