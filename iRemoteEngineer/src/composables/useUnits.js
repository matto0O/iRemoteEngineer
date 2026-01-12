import { ref, watch } from 'vue'

// Load saved preferences from localStorage
const loadPreferences = () => {
  const savedTemp = localStorage.getItem('useFahrenheit')
  const savedSpeed = localStorage.getItem('useMph')
  const savedFuel = localStorage.getItem('useGallons')

  return {
    useFahrenheit: savedTemp !== null ? savedTemp === 'true' : false,
    useMph: savedSpeed !== null ? savedSpeed === 'true' : false,
    useGallons: savedFuel !== null ? savedFuel === 'true' : false
  }
}

const preferences = loadPreferences()

// Shared state across all components - separate for each unit type
const useFahrenheit = ref(preferences.useFahrenheit)
const useMph = ref(preferences.useMph)
const useGallons = ref(preferences.useGallons)

// Save preferences to localStorage whenever they change
watch(useFahrenheit, (value) => {
  localStorage.setItem('useFahrenheit', value ? 'true' : 'false')
})

watch(useMph, (value) => {
  localStorage.setItem('useMph', value ? 'true' : 'false')
})

watch(useGallons, (value) => {
  localStorage.setItem('useGallons', value ? 'true' : 'false')
})

export function useUnits() {
  const toggleTemp = () => {
    useFahrenheit.value = !useFahrenheit.value
  }

  const toggleSpeed = () => {
    useMph.value = !useMph.value
  }

  const toggleFuel = () => {
    useGallons.value = !useGallons.value
  }

  // Temperature conversions
  const convertTemp = (celsius) => {
    if (typeof celsius !== 'number') return celsius
    return useFahrenheit.value ? (celsius * 9/5) + 32 : celsius
  }

  const getTempUnit = () => {
    return useFahrenheit.value ? '°F' : '°C'
  }

  // Speed conversions (kph to mph)
  const convertSpeed = (kph) => {
    if (typeof kph !== 'number') return kph
    return useMph.value ? kph * 0.621371 : kph
  }

  const getSpeedUnit = () => {
    return useMph.value ? 'mph' : 'kph'
  }

  // Fuel conversions (liters to gallons)
  const convertFuel = (liters) => {
    if (typeof liters !== 'number') return liters
    return useGallons.value ? liters * 0.264172 : liters
  }

  const getFuelUnit = () => {
    return useGallons.value ? 'gal' : 'L'
  }

  const getFuelCommandSuffix = () => {
    return useGallons.value ? 'g' : 'l'
  }

  return {
    useFahrenheit,
    useMph,
    useGallons,
    toggleTemp,
    toggleSpeed,
    toggleFuel,
    convertTemp,
    getTempUnit,
    convertSpeed,
    getSpeedUnit,
    convertFuel,
    getFuelUnit,
    getFuelCommandSuffix
  }
}
