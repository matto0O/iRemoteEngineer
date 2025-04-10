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

    <!-- Class Filter -->
    <div class="filter">
      <label for="classFilter">Show class:</label>
      <select id="classFilter" v-model="selectedClass">
        <option value="">All</option>
        <option
          v-for="classId in uniqueClassIds"
          :key="classId"
          :value="classId"
        >
          Class {{ classId }}
        </option>
      </select>
    </div>

    <!-- Selected Car Info -->
    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
      <div v-for="selectedCar in selectedCars" :key="selectedCar.id" class="car-info">
      <h4>Car Info</h4>
      <p><strong>Car Number:</strong> {{ selectedCar.car_number }}</p>
      <p><strong>Car ID:</strong> {{ selectedCar.id }}</p>
      <p><strong>Class:</strong> {{ selectedCar.class_id }}</p>
      <p><strong>Distance %:</strong> {{ (selectedCar.distance_pct * 100).toFixed(1) }}%</p>
      <button @click="selectedCars.splice(selectedCars.indexOf(selectedCar), 1)">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const data = ref({
  player_car_idx: null,
  cars: [],
  fuel_analysis: {}
})

const selectedClass = ref('')
const hoveredCarId = ref(null)
const selectedCars = ref([])

let socket = null

const classColors = [
  "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
  "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

const classColorsMapping = {}
const classOffsetsMapping = {}

onMounted(() => {
  socket = new WebSocket('ws://localhost:8000/ws')

  socket.onmessage = (event) => {
    const data_json = JSON.parse(event.data)
    data.value = data_json
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
  // Use a smaller offset to keep cars closer to the track
  const classOrder = classOffsetsMapping[classId]
  return `${classOrder % 2 == 1 ? "" : "-1"}${(classOrder / 2) * 15}px`
}

const uniqueClassIds = computed(() => {
  const classes = new Set(data.value.cars.map(car => car.class_id))
  return Array.from(classes).sort((a, b) => a - b)
})

const filteredCars = computed(() => {
  return selectedClass.value === ''
    ? data.value.cars
    : data.value.cars.filter(car => car.class_id === Number(selectedClass.value))
})

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
  transition: transform 0.2s ease, z-index 0.2s;
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
  margin-top: 15px;
  padding: 12px;
  background: #fafafa;
  border: 1px solid #ccc;
  border-radius: 8px;
  max-width: 250px;
  font-size: 14px;
}

.car-info h4 {
  margin: 0 0 8px;
}
</style>