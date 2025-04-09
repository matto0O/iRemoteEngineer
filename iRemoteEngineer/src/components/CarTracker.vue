<template>
    <div class="track-bar">
      <div 
        v-for="car in cars" 
        :key="car.id" 
        class="car-marker"
        :style="{ left: car.position + '%' }"
      >
        🚗
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  
  // Example reactive car data
  const cars = ref([
    { id: 1, position: 10 },
    { id: 2, position: 40 },
    { id: 3, position: 85 },
  ])
  
  // Optional: Fetch live data from your backend
  onMounted(() => {
    // You can use setInterval to fetch updates every X seconds
  })
  </script>
  
  <style scoped>
  .track-bar {
    position: relative;
    height: 30px;
    background: #ddd;
    border-radius: 15px;
    margin: 20px;
    overflow: hidden;
  }
  
  .car-marker {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    font-size: 24px;
    transition: left 0.5s ease;
  }
  </style>
  