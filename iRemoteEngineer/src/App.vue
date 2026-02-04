<template>
  <div class="app-container">
    <!-- Demo Mode Banner -->
    <div class="demo-mode-banner" v-if="useDemoMode">
      <span>🔧 DEMO MODE - Using simulated data</span>
    </div>

    <LandingPage
      v-if="!selectedLobbyName"
      :useDemoMode="useDemoMode"
      @update:useDemoMode="useDemoMode = $event"
      @lobby-selected="onLobbySelected"
    />
    <EngineerPanel
      v-else
      :lobby_name="selectedLobbyName"
      :auth_token="authToken || ''"
      :use_demo_mode="useDemoMode"
      @back-to-lobby="backToLobby"
    />
  </div>
</template>

<script>
import LandingPage from './components/LandingPage.vue';
import EngineerPanel from './components/EngineerPanel.vue';

export default {
  name: 'App',
  components: {
    LandingPage,
    EngineerPanel
  },
  data() {
    return {
      useDemoMode: false,
      selectedLobbyName: null,
      authToken: null
    };
  },
  methods: {
    onLobbySelected({ lobby_name, auth_token }) {
      this.selectedLobbyName = lobby_name;
      this.authToken = auth_token;
    },
    backToLobby() {
      this.selectedLobbyName = null;
      this.authToken = null;
    }
  }
};
</script>

<style scoped>
.app-container {
  position: relative;
  width: 100%;
  min-width: 100%;
}

.demo-mode-banner {
  background: var(--demo-banner-bg);
  color: var(--demo-banner-text);
  text-align: center;
  padding: 0.5rem;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 1000;
}
</style>
