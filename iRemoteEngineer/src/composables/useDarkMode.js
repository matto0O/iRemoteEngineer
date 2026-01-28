import { ref, watch, onMounted } from 'vue';

const isDarkMode = ref(false);

export function useDarkMode() {
  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value;
    updateDOM();
    savePreference();
  };

  const setDarkMode = (value) => {
    isDarkMode.value = value;
    updateDOM();
    savePreference();
  };

  const updateDOM = () => {
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
  };

  const savePreference = () => {
    localStorage.setItem('darkMode', isDarkMode.value ? 'true' : 'false');
  };

  const loadPreference = () => {
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) {
      isDarkMode.value = saved === 'true';
    } else {
      // Default to system preference
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    updateDOM();
  };

  onMounted(() => {
    loadPreference();
  });

  // Watch for changes and update DOM
  watch(isDarkMode, () => {
    updateDOM();
  });

  return {
    isDarkMode,
    toggleDarkMode,
    setDarkMode
  };
}
