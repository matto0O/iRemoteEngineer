<template>
  <div class="car-track-container">
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

      <div v-for="car in filteredCars" :key="car.id">
        <div
          v-if="isPlayerCar(car)"
          class="car-marker player-car-marker"
          :style="{
            left: car.distance_pct * 100 + '%',
            backgroundColor: 'white',
            color: getClassColor(car.class_id),
            top: getClassOffset(car.class_id),
            border: `2px solid ${getClassColor(car.class_id)}`,
            transform: `translateX(-50%) ${
              hoveredCarNumber === car.car_number
                ? 'scale(1.2)'
                : highlightedCars.includes(car.car_number)
                ? 'scale(1.2)'
                : 'scale(1)'
            }`,
            opacity: car.in_pit ? '0.5' : '1',
            zIndex:
              hoveredCarNumber === car.car_number
                ? 10
                : highlightedCars.includes(car.car_number)
                ? 9
                : 7,
          }"
          @mouseenter="hoveredCarNumber = car.car_number"
          @mouseleave="hoveredCarNumber = null"
          @click="selectCar(car)"
        >
          {{ getCarDisplayValue(car) }}
        </div>
        <div
          v-else-if="!isPaceCar(car)"
          class="car-marker"
          :style="{
            left: car.distance_pct * 100 + '%',
            backgroundColor: getClassColor(car.class_id),
            top: getClassOffset(car.class_id),
            border: (() => {
              const lapStatus = isOnSameLap(car)
              const color = lapStatus === 1 ? '#8B0000' : lapStatus === -1 ? '#00008B' : '#ffffff'
              const borderStyle = highlightedCars.includes(car.car_number)
                ? `3px solid ${getClassColor(car.class_id)}`
                : `2px solid ${color}`
              return borderStyle
            })(),
            transform: `translateX(-50%) ${
              hoveredCarNumber === car.car_number
                ? 'scale(1.2)'
                : highlightedCars.includes(car.car_number)
                ? 'scale(1.2)'
                : 'scale(1)'
            }`,
            opacity: car.in_pit ? '0.5' : '1',
            zIndex:
              hoveredCarNumber === car.car_number
                ? 10
                : highlightedCars.includes(car.car_number)
                ? 9
                : 5,
          }"
          @mouseenter="hoveredCarNumber = car.car_number"
          @mouseleave="hoveredCarNumber = null"
          @click="selectCar(car)"
        >
          {{ getCarDisplayValue(car) }}
        </div>
      </div>
    </div>
    <div style="height: 50px"></div>

    <!-- Class Filter -->
    <div class="filters-container">
      <div class="filter">
        <label>Show class:</label>
        <ButtonGroup>
          <Button
            v-for="classId in uniqueClassIds"
            :key="classId"
            :label="'Class ' + classId"
            :class="{ 'p-button-outlined': !enabledClasses.includes(classId) }"
            :style="{
              backgroundColor: enabledClasses.includes(classId)
                ? getClassColor(classId)
                : '#d3d3d3',
              color: enabledClasses.includes(classId) ? 'white' : 'black',
              border: '1px solid black',
            }"
            @click="toggleClass(classId)"
          ></Button>
        </ButtonGroup>
      </div>

      <!-- Display Mode Toggle -->
      <div class="display-mode">
        <label>Display mode:</label>
        <ButtonGroup>
          <Button
            v-for="mode in displayModes"
            :key="mode.value"
            :label="mode.label"
            :class="{ 'p-button-outlined': displayMode !== mode.value }"
            :style="{
              backgroundColor: displayMode === mode.value ? '#3498db' : '#f0f0f0',
              color: displayMode === mode.value ? 'white' : 'black',
            }"
            @click="displayMode = mode.value"
          ></Button>
        </ButtonGroup>
      </div>
    </div>

    <!-- Sortable Cars Table with PrimeVue DataTable -->
    <div class="car-table-container">
      <!-- PrimeVue DataTable -->
      <DataTable
        :value="sortedFilteredCars"
        :scrollable="true"
        scrollHeight="400px"
        :removableSort="true"
        striped-rows
        :sortField="'car_position'"
        :sortOrder="1"
        class="p-datatable-sm"
        sortMode="single"
        @row-click="(e) => selectCar(e.data)"
        :rowClass="
          (data) => {
            return {
              'highlighted-row': highlightedCars.includes(data.car_number),
              'player-row': isPlayerCar(data),
            }
          }
        "
      >
        <Column field="car_position" header="Overall Pos" sortable style="width: 80px"></Column>
        <Column field="car_class_position" header="Class Pos" sortable style="width: 80px"></Column>
        <Column header="Car #" sortable style="width: 70px">
          <template #body="slotProps">
            <div
              class="car-number-cell"
              :style="{ backgroundColor: getClassColor(slotProps.data.class_id), color: 'white' }"
            >
              {{ slotProps.data.car_number }}
            </div>
          </template>
        </Column>
        <Column field="team_name" header="Team" sortable style="min-width: 120px"></Column>
        <Column field="user_name" header="Driver" sortable style="min-width: 120px"></Column>
        <Column header="Gap Leader" style="width: 100px">
          <template #body="slotProps">
            <div class="time-cell">{{ formatTime(slotProps.data.gap_leader) }}</div>
          </template>
        </Column>
        <Column header="Gap Next" style="width: 100px">
          <template #body="slotProps">
            <div class="time-cell">
              {{ calculateGapToNext(slotProps.data, sortedFilteredCars.indexOf(slotProps.data)) }}
            </div>
          </template>
        </Column>
        <Column header="Gap Class Leader" style="width: 100px">
          <template #body="slotProps">
            <div class="time-cell">{{ calculateGapToClassLeader(slotProps.data) }}</div>
          </template>
        </Column>
        <Column header="Gap Next in Class" style="width: 100px">
          <template #body="slotProps">
            <div class="time-cell">{{ calculateGapToNextInClass(slotProps.data) }}</div>
          </template>
        </Column>
        <Column header="Last Lap" field="last_lap" style="width: 100px" sortable>
          <template #body="slotProps">
            <div class="time-cell">{{ slotProps.data.last_lap }}</div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Selected Car Info -->
    <div style="display: flex; gap: 10px; flex-wrap: wrap">
      <div
        v-for="car in selectedCars"
        :key="car.car_number"
        class="car-info"
        :style="{ borderLeft: '4px solid ' + getClassColor(car.class_id) }"
      >
        <div class="car-info-header">
          <h4 :style="{ color: getClassColor(car.class_id) }">
            Car #{{ car.car_number }}
            <button
              @click="selectCar(car)"
              class="close-btn"
              style="float: right; margin-left: auto"
            >
              ×
            </button>
          </h4>
        </div>
        <p><strong>Username:</strong> {{ car.user_name }}</p>
        <p><strong>Teamname:</strong> {{ car.team_name }}</p>
        <p><strong>Class:</strong> {{ car.class_id }}</p>
        <p><strong>Car Model:</strong> {{ car.car_model_id }}</p>
        <p><strong>lap:</strong> {{ car.lap }}</p>
        <p><strong>Distance %:</strong> {{ (car.distance_pct * 100).toFixed(1) }}%</p>
        <p><strong>Position:</strong> {{ car.position }}</p>
        <p><strong>Class Position:</strong> {{ car.car_class_position }}</p>
        <p><strong>Gap to Class Leader:</strong> {{ calculateGapToClassLeader(car) }}</p>
        <p><strong>Gap to Next in Class:</strong> {{ calculateGapToNextInClass(car) }}</p>
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
import { ref, computed, watch, defineProps } from 'vue'
import ButtonGroup from 'primevue/buttongroup'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import useRaceData from '@/composables/useRaceData'

const props = defineProps({
  socket: {
    type: Object,
    required: true,
  },
})

// Get shared race data from composable
const { data } = useRaceData(props.socket)

const enabledClasses = ref([])
const hoveredCarNumber = ref(null)
const selectedCars = ref([])
const highlightedCars = ref([]) // Track highlighted cars
const sectors = ref({}) // Store sector information
const playerCar = ref(null) // Store player car information

// Display mode functionality
const displayMode = ref('car_number') // Default display mode
const displayModes = [
  { value: 'car_number', label: 'Car #' },
  { value: 'class_position', label: 'Class Pos' },
  { value: 'position', label: 'Overall Pos' },
]

// Function to format time value as seconds in mm:ss.xxx format
const formatTime = (timeValue) => {
  if (timeValue === null || timeValue === undefined || isNaN(timeValue)) {
    return '-'
  }

  // Check if the time is already formatted
  if (typeof timeValue === 'string' && timeValue.includes(':')) {
    return timeValue
  }

  const totalSeconds = parseFloat(timeValue)

  // Format with 3 decimal places for milliseconds
  return `${totalSeconds.toFixed(3).padStart(6, '0')}`
}

// Calculate gap to next car
const calculateGapToNext = (car) => {
  if (!car || car.car_position == 1) return '-'
  const castCars = Object.values(data.value.cars)
  const carInFront = castCars.find((c) => c.car_position === car.car_position - 1)

  if (!carInFront) return '-'

  const gapDiff = car.gap_leader - carInFront.gap_leader
  return formatTime(gapDiff)
}

// Calculate gap to class leader
const calculateGapToClassLeader = (car) => {
  if (!car || car.car_class_position == 1) return '-'

  const class_ = car.class_id
  const castCars = Object.values(data.value.cars)
  const carLeader = castCars.find((c) => c.class_id === class_ && c.car_class_position === 1)

  if (!carLeader) return '-'

  const gapDiff = car.gap_leader - carLeader.gap_leader
  return formatTime(gapDiff)
}

// Calculate gap to next car in the same class
const calculateGapToNextInClass = (car) => {
  const castCars = Object.values(data.value.cars)
  if (!car || !castCars) return '-'

  // If car is in 1st position in its class, there's no car ahead in same class
  if (car.car_class_position === 1) return '-'

  const class_ = car.class_id

  // Find the car directly ahead in the same class
  const carAhead = castCars.find(
    (c) => c.class_id === class_ && c.car_class_position === car.car_class_position - 1
  )

  if (!carAhead) return '-'

  // Calculate the time gap
  const gapDiff = car.gap_leader - carAhead.gap_leader
  return formatTime(gapDiff)
}

// Function to get the display value based on current mode
const getCarDisplayValue = (car) => {
  switch (displayMode.value) {
    case 'class_position':
      return car.car_class_position || '-'
    case 'position':
      return car.car_position || '-'
    case 'car_number':
    default:
      return car.car_number
  }
}

// Watch for sectors data in the shared race data
watch(
  () => data.value.session_info.split_time_info,
  (newSectors) => {
    if (newSectors && Object.keys(newSectors).length > 0) {
      sectors.value = newSectors
    }
  },
  { immediate: true, deep: true }
)

const classColors = [
  '#1f77b4',
  '#ff7f0e',
  '#2ca02c',
  '#d62728',
  '#9467bd',
  '#8c564b',
  '#e377c2',
  '#7f7f7f',
  '#bcbd22',
  '#17becf',
]

const classColorsMapping = {}
const classOffsetsMapping = {}

const CLASS_OFFSET_MULTIPLIER = 10

// Sync selected car info when data updates
watch(
  () => data.value.cars,
  (newCars) => {
    if (!newCars || newCars.length === 0) return

    selectedCars.value = selectedCars.value.map((oldCar) => {
      const updated = newCars.find((c) => c.car_number === oldCar.car_number)
      return updated || oldCar
    })

    // Initialize enabled classes if needed
    if (enabledClasses.value.length === 0) {
      const classes = new Set(Object.values(newCars).map((car) => car.class_id))
      enabledClasses.value = Array.from(classes).sort((a, b) => a - b)
    }

    // Update playerCar
    const playerCarData = newCars[data.value.player_car_number] || null
    if (playerCarData) {
      playerCar.value = playerCarData
    }
  },
  { deep: true }
)

const isPlayerCar = (car) => {
  return car.car_number === data.value.player_car_number
}

const isPaceCar = (car) => {
  return car.car_number == 0
}

const isOnSameLap = (car) => {
  // Tri-state logic to determine if the car is on the same lap as the player car
  // 1: Lap ahead, 0: Same lap, -1: Lap down
  if (!playerCar.value) return 0 // No player car data available

  const lapDiff = car.lap - playerCar.value.lap
  if (lapDiff > 1) return 1
  if (lapDiff < -1) return -1
  const posDiff = car.distance_pct - playerCar.value.distance_pct
  if (lapDiff === 1 && posDiff > -0.5) return 1
  if (lapDiff === -1 && posDiff < 0.5) return -1
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
  const castCars = Object.values(data.value.cars)
  if (!castCars) return []
  const classes = new Set(
    castCars.filter((car) => car.car_number != 0).map((car) => car.class_id)
  )
  return Array.from(classes).sort((a, b) => a - b)
})

const filteredCars = computed(() => {
  const castCars = Object.values(data.value.cars)
  if (!castCars) return []
  return enabledClasses.value.length === 0
    ? castCars.filter((car) => car.car_number != 0) // Filter out pace car
    : castCars.filter(
        (car) => enabledClasses.value.includes(car.class_id) && car.car_number != 0
      )
})

// Sort filtered cars by position for data table
const sortedFilteredCars = computed(() => {
  return [...filteredCars.value].sort((a, b) => {
    return (a.position || 999) - (b.position || 999)
  })
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
  const existingCarIndex = selectedCars.value.findIndex(
    (selectedCar) => selectedCar.car_number === car.car_number
  )
  if (existingCarIndex !== -1) {
    selectedCars.value.splice(existingCarIndex, 1)
  } else {
    selectedCars.value.push(car)
  }
}

const toggleHighlight = (car) => {
  const index = highlightedCars.value.indexOf(car.car_number)
  if (index === -1) {
    highlightedCars.value.push(car.car_number)
  } else {
    highlightedCars.value.splice(index, 1)
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
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
  transition: left 0.5s ease, transform 0.2s ease, z-index 0.2s, border 0.2s ease;
  cursor: pointer;
}

.car-marker:hover {
  transform: translateX(-50%) scale(1.2);
}

.filters-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 15px;
}

.filter,
.display-mode {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Car Table Styles */
.car-table-container {
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: relative;
}

/* Player Car Row (Pinned) */
.player-car-row {
  background-color: #e3f2fd;
  font-weight: bold;
  border-bottom: 2px solid #90caf9;
  padding: 8px 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.pinned-player-car {
  display: flex;
  align-items: center;
  width: 100%;
  pointer-events: all;
}

.player-info-cell {
  padding: 8px 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Make player cells match datatable columns */
.player-info-cell:nth-child(1),
.player-info-cell:nth-child(2) {
  width: 80px;
  text-align: center;
}

.player-info-cell.username,
.player-info-cell.teamname {
  min-width: 120px;
  flex: 1;
}

.player-info-cell.car-number {
  width: 70px;
  text-align: center;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-info-cell.gap-leader,
.player-info-cell.gap-next,
.player-info-cell.gap-class,
.player-info-cell.last-lap {
  width: 100px;
  text-align: right;
  font-family: monospace;
}

/* DataTable styling */
:deep(.p-datatable-wrapper) {
  overflow-y: auto;
  height: 400px; /* Match scrollHeight of DataTable */
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f5f5f5;
  position: sticky;
  top: 0;
  z-index: 5;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  cursor: pointer;
}

:deep(.p-datatable .p-datatable-tbody > tr.highlighted-row) {
  background-color: #fff8e1 !important;
}

:deep(.p-datatable .p-datatable-tbody > tr.player-row) {
  background-color: #e3f2fd !important;
  font-weight: bold;
}

/* Car number cell styling */
.car-number-cell {
  border-radius: 4px;
  padding: 4px 8px;
  text-align: center;
  font-weight: bold;
  width: 40px;
  margin: auto;
}

/* Time cell styling */
.time-cell {
  font-family: monospace;
  text-align: right;
}

/* Selected Car Info */
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

.car-info-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.car-info h4 {
  margin: 0;
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