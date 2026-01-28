import { ref } from 'vue'
import carCodesData from '@/assets/car_codes.json'

// Shared lookup maps (singleton pattern - built once, shared across all components)
const carModelMap = ref(new Map())
const classMap = ref(new Map())
const seriesMap = ref(new Map())
// Map: series_id -> Map(car_id -> class_name)
const seriesCarClassMap = ref(new Map())
let isInitialized = false

// Build lookup maps from car_codes.json
const initializeMaps = () => {
  if (isInitialized) return

  carCodesData.forEach(series => {
    // Build series map
    seriesMap.value.set(series.series_id, series.series_name)

    // Build car model map
    series.cars.forEach(car => {
      if (!carModelMap.value.has(car.car_id)) {
        carModelMap.value.set(car.car_id, car.car_name)
      }
    })

    // Build class map and series-car-class map
    const carToClassMap = new Map()
    series.classes.forEach(carClass => {
      if (!classMap.value.has(carClass.class_id)) {
        classMap.value.set(carClass.class_id, carClass.class_name)
      }
      // Map each car in this class to the class name
      carClass.cars_in_class.forEach(carId => {
        carToClassMap.set(carId, carClass.class_name)
      })
    })
    seriesCarClassMap.value.set(series.series_id, carToClassMap)
  })

  isInitialized = true
}

// Initialize on module load
initializeMaps()

export default function useCarData() {
  // Get car model name from ID
  const getCarModelName = (carModelId) => {
    return carModelMap.value.get(carModelId) || `Car ${carModelId}`
  }

  // Get class name from ID
  const getClassName = (classId) => {
    return classMap.value.get(classId) || `Class ${classId}`
  }

  // Get series name from ID
  const getSeriesName = (seriesId) => {
    return seriesMap.value.get(seriesId) || 'Unknown Series'
  }

  // Get class name for a car within a specific series
  const getClassNameForCar = (seriesId, carModelId) => {
    const carToClassMap = seriesCarClassMap.value.get(seriesId)
    if (carToClassMap) {
      return carToClassMap.get(carModelId) || null
    }
    return null
  }

  return {
    carModelMap,
    classMap,
    seriesMap,
    getCarModelName,
    getClassName,
    getSeriesName,
    getClassNameForCar
  }
}
