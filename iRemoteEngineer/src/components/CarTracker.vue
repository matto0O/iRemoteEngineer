<template>
  <div class="car-track-container">
    <!-- Connection Status (optional) -->
    <div v-if="!isConnected" class="connection-error">
      Connection lost - {{ connectionError || 'Attempting to reconnect...' }}
    </div>
    
    <!-- Track Strip -->
    <div class="track-strip">
      <!-- Sector markers -->
      <div 
        v-for="(startPct, sectorNum) in sectors" 
        :key="'sector-' + sectorNum"
        class="sector-marker"
        :style="{ left: startPct + '%', zIndex: 2 }"
      >
        <div class="sector-line"></div>
        <div class="sector-label">S{{ sectorNum }}</div>
      </div>
      
      <div
        v-for="car in filteredCars"
        :key="car.id"
        class="car-marker"
        :style="{
          left: car.distance_pct * 100 + '%',
          backgroundColor: getClassColor(car.class_id),
          top: getClassOffset(car.class_id),
          border: highlightedCars.includes(car.car_number) ? `3px solid ${getClassColor(car.class_id)}` : '2px solid #fff',
          transform: `translateX(-50%) ${hoveredCarNumber === car.car_number ? 'scale(1.2)' : highlightedCars.includes(car.car_number) ? 'scale(1.2)' : 'scale(1)'}`,
          opacity: car.in_pit ? '0.5' : '1',
          zIndex: hoveredCarNumber === car.car_number ? 10 : highlightedCars.includes(car.car_number) ? 9 : 5
        }"
        @mouseenter="hoveredCarNumber = car.car_number"
        @mouseleave="hoveredCarNumber = null"
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
        <p><strong>Username:</strong> {{ car.user_name }}</p>
        <p><strong>Teamname:</strong> {{ car.team_name }}</p>
        <p><strong>Class:</strong> {{ car.class_id }}</p>
        <p><strong>Car Model:</strong> {{ car.car_model_id }}</p>
        <p><strong>lap:</strong> {{ car.lap }}</p>
        <p><strong>Distance %:</strong> {{ (car.distance_pct * 100).toFixed(1) }}%</p>
        <button 
          @click="toggleHighlight(car)" 
          class="highlight-btn"
          :class="{ 'highlight-active': highlightedCars.includes(car.car_number) }"
        >
          {{ highlightedCars.includes(car.car_number) ? 'Remove Highlight' : 'Highlight Car' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import ButtonGroup from 'primevue/buttongroup'
import Button from 'primevue/button'
import useRaceData from '@/composables/useRaceData'

// Get shared race data from composable
const { data, isConnected, connectionError } = useRaceData()

const enabledClasses = ref([])
const hoveredCarNumber = ref(null)
const selectedCars = ref([])
const highlightedCars = ref([]) // Track highlighted cars
const sectors = ref({}) // Store sector information

// Watch for sectors data in the shared race data
watch(() => data.value.sectors, (newSectors) => {
  if (newSectors && Object.keys(newSectors).length > 0) {
    sectors.value = newSectors
  }
}, { immediate: true, deep: true })

const classColors = [
  "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
  "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

const classColorsMapping = {}
const classOffsetsMapping = {}

const CLASS_OFFSET_MULTIPLIER = 10

// Sync selected car info when data updates
watch(() => data.value.cars, (newCars) => {
  if (!newCars || newCars.length === 0) return
  
  selectedCars.value = selectedCars.value.map(oldCar => {
    const updated = newCars.find(c => c.car_number === oldCar.car_number)
    return updated || oldCar
  })

  // Initialize enabled classes if needed
  if (enabledClasses.value.length === 0) {
    const classes = new Set(newCars.map(car => car.class_id))
    enabledClasses.value = Array.from(classes).sort((a, b) => a - b)
  }
}, { deep: true })

const isOnSameLap = (car) => {
  // TODO: Implement logic to check if the car is on the same lap as the player car
  // Use tri-state logic to determine if the car is on the same lap as the player car
  // 1: Lap ahead, 0: Same lap, -1: Lap down
  return 0
}

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
  return `${20 - classOrder * CLASS_OFFSET_MULTIPLIER}px`
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

const toggleHighlight = (car) => {
  const index = highlightedCars.value.indexOf(car.car_number);
  if (index === -1) {
    highlightedCars.value.push(car.car_number);
  } else {
    highlightedCars.value.splice(index, 1);
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
  /* padding-top: 60px; Add padding to accommodate car markers above the track */
}

.track-strip {
  position: relative;
  height: 8px;
  background-color: #ccc;
  border-radius: 4px;
  overflow: visible;
}

/* Sector markers styling */
.sector-marker {
  position: absolute;
  transform: translateX(-50%);
  pointer-events: none;
  z-index: 5;
}

.sector-line {
  width: 2px;
  height: 12px;
  background-color: #333;
  margin: 0 auto;
}

.sector-label {
  font-size: 10px;
  color: #333;
  font-weight: bold;
  text-align: center;
  margin-top: 2px;
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
  transition: left 0.5s ease, transform 0.2s ease, z-index 0.2s, border 0.2s ease;
  cursor: pointer;
}

.car-marker:hover {
  transform: translateX(-50%) scale(1.2);
}

.filter {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.car-info {
  width: 300px;
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

.highlight-btn {
  margin-top: 8px;
  padding: 5px 10px;
  border-radius: 4px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  cursor: pointer;
  transition: all 0.2s ease;
}

.highlight-btn:hover {
  background-color: #e0e0e0;
}

.highlight-active {
  background-color: #e0e0e0;
  border-color: #aaa;
  font-weight: bold;
}

.connection-error {
  background-color: #ffdddd;
  color: #ff0000;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 10px;
}
</style>