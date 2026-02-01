<template>
  <div class="car-tracker-wrapper">
    <Card class="car-tracker-card">
      <template #title>
        <div class="card-header">
          <div class="card-header-left">
            <i class="pi pi-car"></i>
            <span>Car Tracker</span>
          </div>
          <div class="card-header-controls">
            <!-- Track Display Options Toggle Button -->
            <Button
              :label="showTrackOptions ? 'Hide Track Display' : 'Track Display Options'"
              :icon="showTrackOptions ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
              size="small"
              severity="secondary"
              @click="showTrackOptions = !showTrackOptions"
            />

            <!-- Column Options Toggle Button -->
            <Button
              :label="showColumnOptions ? 'Hide Columns' : 'Table Columns'"
              :icon="showColumnOptions ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
              size="small"
              severity="secondary"
              @click="showColumnOptions = !showColumnOptions"
            />

            <!-- Filters Toggle Button -->
            <Button
              :label="showFilters ? 'Hide Filters' : 'Show Filters'"
              :icon="showFilters ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
              size="small"
              severity="secondary"
              @click="showFilters = !showFilters"
            />
          </div>
        </div>
      </template>
      <template #content>
        <!-- Collapsible Track Display Options -->
        <div v-if="showTrackOptions" class="filters-section">
          <div class="filter-group">
            <label class="filter-label">Track Strip Display Mode:</label>
            <ButtonGroup class="filter-button-group">
              <Button
                v-for="mode in displayModes"
                :key="mode.value"
                :label="mode.label"
                size="small"
                :severity="displayMode === mode.value ? 'primary' : 'secondary'"
                :outlined="displayMode !== mode.value"
                @click="displayMode = mode.value"
              ></Button>
            </ButtonGroup>
          </div>
          <div class="filter-group filter-group-inline">
            <label class="filter-label">Animation:</label>
            <Button
              :label="animateCars ? 'On' : 'Off'"
              :icon="animateCars ? 'pi pi-play' : 'pi pi-pause'"
              size="small"
              :severity="animateCars ? 'success' : 'secondary'"
              :outlined="!animateCars"
              @click="animateCars = !animateCars"
            />
          </div>
        </div>

        <!-- Collapsible Column Options -->
        <div v-if="showColumnOptions" class="filters-section">
          <div class="filter-group">
            <label class="filter-label">Visible Columns:</label>
            <ButtonGroup class="filter-button-group">
              <Button
                v-for="column in columnDefinitions"
                :key="column.key"
                :label="column.label"
                size="small"
                :outlined="!visibleColumns[column.key]"
                :severity="visibleColumns[column.key] ? 'info' : 'secondary'"
                :style="{
                  opacity: !visibleColumns[column.key] ? '0.5' : '1'
                }"
                @click="visibleColumns[column.key] = !visibleColumns[column.key]"
              ></Button>
            </ButtonGroup>
          </div>
        </div>

        <!-- Collapsible Filters -->
        <div v-if="showFilters" class="filters-section">
          <!-- Car Class Filter -->
          <div class="filter-group">
            <label class="filter-label">Car Classes:</label>
            <ButtonGroup class="filter-button-group">
              <Button
                v-for="classId in uniqueClassIds"
                :key="classId"
                :label="getClassName(classId)"
                size="small"
                :outlined="disabledClasses.includes(classId)"
                :style="{
                  backgroundColor: !disabledClasses.includes(classId)
                    ? getClassColor(classId)
                    : 'transparent',
                  color: !disabledClasses.includes(classId) ? 'white' : 'var(--text-primary)',
                  borderColor: getClassColor(classId),
                  opacity: disabledClasses.includes(classId) ? '0.5' : '1'
                }"
                @click="toggleClass(classId)"
              ></Button>
            </ButtonGroup>
          </div>

          <!-- Car Model Filter -->
          <div class="filter-group">
            <label class="filter-label">Car Models:</label>
            <ButtonGroup class="filter-button-group">
              <Button
                v-for="carId in uniqueCarModelIds"
                :key="carId"
                :label="getCarModelName(carId)"
                size="small"
                :outlined="disabledCarModels.includes(carId)"
                :severity="!disabledCarModels.includes(carId) ? 'info' : 'secondary'"
                :style="{
                  opacity: disabledCarModels.includes(carId) ? '0.5' : '1'
                }"
                @click="toggleCarModel(carId)"
              ></Button>
            </ButtonGroup>
          </div>
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

      <div v-for="car in filteredCars" :key="car.id">
        <div
          v-if="isPlayerCar(car)"
          :class="['car-marker', 'player-car-marker', { 'no-animation': !animateCars }]"
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
          :class="['car-marker', { 'no-animation': !animateCars }]"
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

    <!-- Sortable Cars Table with PrimeVue DataTable -->
    <div class="car-table-container">
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
        :customSort="customSort"
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
        <Column v-if="visibleColumns.car_position" field="car_position" header="Overall Pos" sortable></Column>
        <Column v-if="visibleColumns.car_class_position" field="car_class_position" header="Class Pos" sortable></Column>
        <Column v-if="visibleColumns.car_number" header="Car #" sortable>
          <template #body="slotProps">
            <div
              class="car-number-cell"
              :style="{ backgroundColor: getClassColor(slotProps.data.class_id), color: 'white' }"
            >
              {{ slotProps.data.car_number }}
            </div>
          </template>
        </Column>
        <Column v-if="visibleColumns.team_name" field="team_name" header="Team" sortable></Column>
        <Column v-if="visibleColumns.user_name" field="user_name" header="Driver" sortable></Column>
        <Column v-if="visibleColumns.class" header="Class" sortable>
          <template #body="slotProps">
            <span :style="{ color: getClassColor(slotProps.data.class_id), fontWeight: 'bold' }">
              {{ getClassName(slotProps.data.class_id) }}
            </span>
          </template>
        </Column>
        <Column v-if="visibleColumns.car_model" header="Car Model" sortable>
          <template #body="slotProps">
            {{ getCarModelName(slotProps.data.car_model_id) }}
          </template>
        </Column>
        <Column v-if="visibleColumns.gap_leader" header="Gap Leader">
          <template #body="slotProps">
            <div class="time-cell">{{ formatTime(slotProps.data.gap_leader) }}</div>
          </template>
        </Column>
        <Column v-if="visibleColumns.gap_next" header="Gap Next">
          <template #body="slotProps">
            <div class="time-cell">
              {{ calculateGapToNext(slotProps.data, sortedFilteredCars.indexOf(slotProps.data)) }}
            </div>
          </template>
        </Column>
        <Column v-if="visibleColumns.gap_class_leader" header="Gap Class Leader">
          <template #body="slotProps">
            <div class="time-cell">{{ calculateGapToClassLeader(slotProps.data) }}</div>
          </template>
        </Column>
        <Column v-if="visibleColumns.gap_next_class" header="Gap Next in Class">
          <template #body="slotProps">
            <div class="time-cell">{{ calculateGapToNextInClass(slotProps.data) }}</div>
          </template>
        </Column>
        <Column v-if="visibleColumns.last_lap" header="Last Lap" field="car_lap_last_time" sortable>
          <template #body="slotProps">
            <div class="time-cell">{{ slotProps.data.car_lap_last_time || '--:--.---' }}</div>
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
        <p><strong>Class:</strong> {{ getClassName(car.class_id) }}</p>
        <p><strong>Car Model:</strong> {{ getCarModelName(car.car_model_id) }}</p>
        <p><strong>Lap:</strong> {{ car.lap }}</p>
        <p><strong>Last Lap Time:</strong> {{ car.car_lap_last_time || '--:--.---' }}</p>
        <p><strong>Distance %:</strong> {{ (car.distance_pct * 100).toFixed(1) }}%</p>
        <p><strong>Position:</strong> {{ car.car_position }}</p>
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
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps } from 'vue'
import Card from 'primevue/card'
import ButtonGroup from 'primevue/buttongroup'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import useRaceData from '@/composables/useRaceData'
import useCarData from '@/composables/useCarData'

const props = defineProps({
  socket: {
    type: Object,
    required: true,
  },
})

// Get shared race data from composable
const { data } = useRaceData(props.socket)

// Get car data utilities from composable
const { getCarModelName, getClassName } = useCarData()

// Load settings from localStorage with defaults
const loadFromLocalStorage = (key, defaultValue) => {
  try {
    const stored = localStorage.getItem(key)
    return stored !== null ? JSON.parse(stored) : defaultValue
  } catch (e) {
    console.error(`Error loading ${key} from localStorage:`, e)
    return defaultValue
  }
}

// Save settings to localStorage
const saveToLocalStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (e) {
    console.error(`Error saving ${key} to localStorage:`, e)
  }
}

const disabledClasses = ref(loadFromLocalStorage('carTracker_disabledClasses', []))
const disabledCarModels = ref(loadFromLocalStorage('carTracker_disabledCarModels', []))
const showFilters = ref(false)
const showTrackOptions = ref(false)
const showColumnOptions = ref(false)
const animateCars = ref(loadFromLocalStorage('carTracker_animateCars', true))
const hoveredCarNumber = ref(null)
const selectedCars = ref([])
const highlightedCars = ref([])
const sectors = ref({})
const playerCar = ref(null)

// Column visibility
const visibleColumns = ref(loadFromLocalStorage('carTracker_visibleColumns', {
  car_position: true,
  car_class_position: true,
  car_number: true,
  team_name: true,
  user_name: true,
  class: true,
  car_model: true,
  gap_leader: true,
  gap_next: true,
  gap_class_leader: true,
  gap_next_class: true,
  last_lap: true,
}))

const columnDefinitions = [
  { key: 'car_position', label: 'Overall Position' },
  { key: 'car_class_position', label: 'Class Position' },
  { key: 'car_number', label: 'Car Number' },
  { key: 'team_name', label: 'Team Name' },
  { key: 'user_name', label: 'Driver Name' },
  { key: 'class', label: 'Class' },
  { key: 'car_model', label: 'Car Model' },
  { key: 'gap_leader', label: 'Gap to Leader' },
  { key: 'gap_next', label: 'Gap to Next' },
  { key: 'gap_class_leader', label: 'Gap to Class Leader' },
  { key: 'gap_next_class', label: 'Gap to Next in Class' },
  { key: 'last_lap', label: 'Last Lap Time' },
]

// Display mode functionality
const displayMode = ref(loadFromLocalStorage('carTracker_displayMode', 'car_number'))
const displayModes = [
  { value: 'car_number', label: 'Show Car Numbers' },
  { value: 'car_class_position', label: 'Show Class Position' },
  { value: 'car_position', label: 'Show Overall Position' },
]

// Watch for changes and save to localStorage
watch(disabledClasses, (newVal) => {
  saveToLocalStorage('carTracker_disabledClasses', newVal)
}, { deep: true })

watch(disabledCarModels, (newVal) => {
  saveToLocalStorage('carTracker_disabledCarModels', newVal)
}, { deep: true })

watch(visibleColumns, (newVal) => {
  saveToLocalStorage('carTracker_visibleColumns', newVal)
}, { deep: true })

watch(displayMode, (newVal) => {
  saveToLocalStorage('carTracker_displayMode', newVal)
})

watch(animateCars, (newVal) => {
  saveToLocalStorage('carTracker_animateCars', newVal)
})


// Function to format time value as seconds
const formatTime = (timeValue) => {
  if (timeValue === null || timeValue === undefined || isNaN(timeValue)) {
    return '-'
  }

  if (typeof timeValue === 'string' && timeValue.includes(':')) {
    return timeValue
  }

  const totalSeconds = parseFloat(timeValue)
  return `${totalSeconds.toFixed(3).padStart(6, '0')}`
}

// Helper function to convert formatted lap time to seconds for sorting
const lapTimeToSeconds = (timeStr) => {
  if (!timeStr || typeof timeStr !== 'string' || timeStr.startsWith('--')) {
    return Infinity; // Invalid times sort to the end
  }

  const parts = timeStr.split(':');
  if (parts.length !== 2) return Infinity;

  const minutes = parseInt(parts[0]);
  const seconds = parseFloat(parts[1]);

  if (isNaN(minutes) || isNaN(seconds)) return Infinity;

  return minutes * 60 + seconds;
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

  if (car.car_class_position === 1) return '-'

  const class_ = car.class_id

  const carAhead = castCars.find(
    (c) => c.class_id === class_ && c.car_class_position === car.car_class_position - 1
  )

  if (!carAhead) return '-'

  const gapDiff = car.gap_leader - carAhead.gap_leader
  return formatTime(gapDiff)
}

// Function to get the display value based on current mode
const getCarDisplayValue = (car) => {
  switch (displayMode.value) {
    case 'car_class_position':
      return car.car_class_position || '-'
    case 'car_position':
      return car.car_position || '-'
    case 'car_number':
    default:
      return car.car_number
  }
}

// Watch for sectors data
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
    if (!newCars || Object.keys(newCars).length === 0) return

    selectedCars.value = selectedCars.value.map((oldCar) => {
      const updated = Object.values(newCars).find((c) => c.car_number === oldCar.car_number)
      return updated || oldCar
    })

    // Initialize disabled classes and models as empty (all enabled by default)
    // No initialization needed - empty arrays mean all are enabled

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
  if (!playerCar.value) return 0

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

const uniqueCarModelIds = computed(() => {
  const castCars = Object.values(data.value.cars)
  if (!castCars) return []
  const models = new Set(
    castCars.filter((car) => car.car_number != 0).map((car) => car.car_model_id)
  )
  return Array.from(models).sort((a, b) => a - b)
})

const filteredCars = computed(() => {
  const castCars = Object.values(data.value.cars)
  if (!castCars) return []

  return castCars.filter((car) => {
    if (car.car_number == 0) return false // Filter out pace car

    const classMatch = !disabledClasses.value.includes(car.class_id)
    const modelMatch = !disabledCarModels.value.includes(car.car_model_id)

    return classMatch && modelMatch
  })
})

const sortedFilteredCars = computed(() => {
  return [...filteredCars.value].sort((a, b) => {
    const posA = a.car_position === 0 || a.car_position == null ? Infinity : a.car_position
    const posB = b.car_position === 0 || b.car_position == null ? Infinity : b.car_position
    return posA - posB
  })
})

const toggleClass = (classId) => {
  const index = disabledClasses.value.indexOf(classId)
  if (index === -1) {
    // Class is currently enabled, so disable it
    disabledClasses.value.push(classId)

    // Also disable all car models of this class
    const allCars = Object.values(data.value.cars)
    const modelsInClass = [...new Set(
      allCars
        .filter(car => car.class_id === classId)
        .map(car => car.car_model_id)
    )]

    modelsInClass.forEach(modelId => {
      if (!disabledCarModels.value.includes(modelId)) {
        disabledCarModels.value.push(modelId)
      }
    })
  } else {
    // Class is currently disabled, so enable it
    disabledClasses.value.splice(index, 1)

    // Also re-enable all car models of this class
    const allCars = Object.values(data.value.cars)
    const modelsInClass = [...new Set(
      allCars
        .filter(car => car.class_id === classId)
        .map(car => car.car_model_id)
    )]

    modelsInClass.forEach(modelId => {
      const modelIndex = disabledCarModels.value.indexOf(modelId)
      if (modelIndex !== -1) {
        disabledCarModels.value.splice(modelIndex, 1)
      }
    })
  }
}

const toggleCarModel = (carId) => {
  const index = disabledCarModels.value.indexOf(carId)
  if (index === -1) {
    // Model is currently enabled, so disable it
    disabledCarModels.value.push(carId)
  } else {
    // Model is currently disabled, so enable it
    disabledCarModels.value.splice(index, 1)
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

// Custom sort function for the DataTable
const customSort = (event) => {
  const data = [...event.data];
  const field = event.sortField;
  const order = event.sortOrder;

  // Special handling for lap time sorting
  if (field === 'car_lap_last_time') {
    data.sort((a, b) => {
      const timeA = lapTimeToSeconds(a[field]);
      const timeB = lapTimeToSeconds(b[field]);
      return order * (timeA - timeB);
    });
  }
  // Special handling for position fields - treat 0 as infinity
  else if (field === 'car_position' || field === 'car_class_position') {
    data.sort((a, b) => {
      let valueA = a[field];
      let valueB = b[field];

      // Treat 0 as infinity for position fields
      if (valueA === 0 || valueA == null) valueA = Infinity;
      if (valueB === 0 || valueB == null) valueB = Infinity;

      return order * (valueA - valueB);
    });
  }
  else {
    // Default sorting for other fields
    data.sort((a, b) => {
      const valueA = a[field];
      const valueB = b[field];

      if (valueA == null && valueB != null) return order;
      if (valueA != null && valueB == null) return -order;
      if (valueA == null && valueB == null) return 0;

      if (typeof valueA === 'string' && typeof valueB === 'string') {
        return order * valueA.localeCompare(valueB);
      }

      return order * (valueA - valueB);
    });
  }

  return data;
}
</script>

<style scoped>
.car-tracker-wrapper {
  width: 100%;
  padding: 0;
}

.car-tracker-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.dark-mode .car-tracker-card {
  background: linear-gradient(135deg, #4a5f9d 0%, #5a3a7a 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.car-tracker-card :deep(.p-card-body) {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0;
}

.car-tracker-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  border-radius: 16px 16px 0 0;
  margin: 0;
}

.dark-mode .car-tracker-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #4a5f9d 0%, #5a3a7a 100%);
}

.car-tracker-card :deep(.p-card-content) {
  padding: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-header-left i {
  font-size: 1.25rem;
}

.card-header-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Filters Section */
.filters-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--filter-content-bg);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-group-inline {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
}

.filter-button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.track-strip {
  position: relative;
  height: 8px;
  background-color: #ccc;
  border-radius: 4px;
  overflow: visible;
  margin-top: 25px;
}

.dark-mode .track-strip {
  background-color: #4a4a4a;
}

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

.dark-mode .sector-line {
  background-color: #ccc;
}

.sector-label {
  font-size: 10px;
  color: #333;
  font-weight: bold;
  text-align: center;
  margin-top: 2px;
}

.dark-mode .sector-label {
  color: #e0e0e0;
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

.car-marker.no-animation {
  transition: transform 0.2s ease, z-index 0.2s, border 0.2s ease;
}

.car-marker:hover {
  transform: translateX(-50%) scale(1.2);
}

.display-mode label {
  margin-right: 10px;
}

/* Car Table Styles */
.car-table-container {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px var(--card-shadow);
  position: relative;
  background: var(--table-bg);
  transition: box-shadow 0.3s ease;
}

.car-table-container:hover {
  box-shadow: 0 6px 20px var(--card-shadow-hover);
}

.player-car-row {
  background-color: #e3f2fd;
  font-weight: bold;
  border-bottom: 2px solid #90caf9;
  padding: 8px 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

:deep(.p-datatable-wrapper) {
  overflow-y: auto;
  height: 400px;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: linear-gradient(135deg, var(--table-header-bg-start) 0%, var(--table-header-bg-end) 100%);
  position: sticky;
  top: 0;
  z-index: 5;
  font-weight: 600;
  color: var(--table-header-text);
  border-bottom: 2px solid var(--table-border);
  padding: 1rem 0.75rem;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  cursor: pointer;
  transition: all 0.2s ease;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: var(--table-hover-bg) !important;
  transform: scale(1.01);
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.875rem 0.75rem;
  border-bottom: 1px solid var(--table-row-border);
}

:deep(.p-datatable .p-datatable-tbody > tr.highlighted-row) {
  background: linear-gradient(135deg, var(--highlighted-row-start) 0%, var(--highlighted-row-end) 100%) !important;
  box-shadow: inset 0 0 0 2px #ffc107;
}

:deep(.p-datatable .p-datatable-tbody > tr.player-row) {
  background: linear-gradient(135deg, var(--player-row-start) 0%, var(--player-row-end) 100%) !important;
  font-weight: bold;
  box-shadow: inset 0 0 0 2px #2196f3;
}

.car-number-cell {
  border-radius: 4px;
  padding: 4px 8px;
  text-align: center;
  font-weight: bold;
  width: 40px;
  margin: auto;
}

.time-cell {
  font-family: 'Courier New', monospace;
  text-align: right;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--time-cell-text);
}

/* Selected Car Info */
.car-info {
  width: 300px;
  margin-top: 15px;
  padding: 12px;
  background: var(--info-card-bg);
  border: 1px solid var(--info-card-border);
  border-radius: 8px;
  font-size: 14px;
  flex-grow: 0;
  flex-shrink: 0;
  color: var(--text-primary);
}

.car-info p {
  color: var(--text-primary);
}

.car-info-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.car-info h4 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--close-btn-color);
  padding: 0 4px;
  line-height: 1;
}

.close-btn:hover {
  color: var(--text-primary);
}

.highlight-btn {
  margin-top: 8px;
  padding: 5px 10px;
  border-radius: 4px;
  background-color: var(--button-secondary-bg);
  border: 1px solid var(--info-card-border);
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-primary);
}

.highlight-btn:hover {
  background-color: var(--button-secondary-hover);
}

.highlight-active {
  background-color: var(--button-secondary-hover);
  border-color: var(--border-color);
  font-weight: bold;
}

/* Responsive Design */
@media (max-width: 768px) {
  .car-tracker-wrapper {
    padding: 0;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .card-header-controls {
    flex-direction: column;
    gap: 0.5rem;
  }

  .display-mode-compact,
  .card-header-controls > button {
    width: 100%;
  }

  .filter-button-group {
    flex-direction: column;
  }

  .filter-button-group button {
    width: 100%;
  }

  .car-info {
    width: 100%;
    flex-shrink: 1;
  }

  .car-table-container {
    overflow-x: auto;
  }
}
</style>