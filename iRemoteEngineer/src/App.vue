<script setup>
import CarTracker from './components/CarTracker.vue';
import FuelAnalysis from './components/FuelAnalysis.vue';
import IncidentTracker from './components/IncidentTracker.vue';
import TyreDetails from './components/TyreDetails.vue';
import WeatherInfo from './components/WeatherInfo.vue';
import PitSettings from './components/PitSettings.vue';
</script>

<template>
  <main>
    <div class="component-container">
      <CarTracker />
      <FuelAnalysis />
      <TyreDetails />
      <WeatherInfo />
      <IncidentTracker />
      <PitSettings />
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
