<script setup>
import CarTracker from './components/CarTracker.vue';
import FuelAnalysis from './components/FuelAnalysis.vue';
</script>

<template>
  <main>
    <div class="component-container">
      <CarTracker />
      <FuelAnalysis />
    </div>
  </main>
</template>

<style scoped>
main {
  display: flex;
  justify-content: center;
}

header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
