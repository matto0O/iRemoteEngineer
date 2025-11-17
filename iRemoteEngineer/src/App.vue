<template>
  <div id="app">
    <div class="header">
      <h1>iRacing Data Streams</h1>
      <p>Select a stream to access live telemetry data</p>
    </div>
    
    <div class="filters-section">
      <div class="search-bar">
        <span class="p-input-icon-left search-input">
          <i class="pi pi-search"></i>
          <InputText 
            v-model="searchQuery" 
            placeholder="Search lobby names..." 
            style="width: 100%"
          />
        </span>
        <Button 
          :label="showFilters ? 'Hide Filters' : 'Show Filters'" 
          icon="pi pi-filter"
          :severity="showFilters ? 'primary' : 'secondary'"
          @click="showFilters = !showFilters"
        />
      </div>
      
      <div v-if="showFilters" class="filter-grid">
        <div class="filter-group">
          <label class="filter-label">Track</label>
          <Dropdown 
            v-model="trackFilter" 
            :options="trackOptions" 
            optionLabel="label" 
            optionValue="value"
            placeholder="Select a track"
          />
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Max Last Active</label>
          <div v-for="option in lastActiveOptions" :key="option.value" class="radio-option">
            <RadioButton 
              v-model="maxLastActive" 
              :inputId="'active-' + option.value" 
              :value="option.value"
            />
            <label :for="'active-' + option.value">{{ option.label }}</label>
          </div>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Max Time Since Start</label>
          <div v-for="option in timeSinceStartOptions" :key="option.value" class="radio-option">
            <RadioButton 
              v-model="maxTimeSinceStart" 
              :inputId="'start-' + option.value" 
              :value="option.value"
            />
            <label :for="'start-' + option.value">{{ option.label }}</label>
          </div>
        </div>
      </div>
    </div>
    
    <div class="results-count">
      Showing {{ filteredStreams.length }} of {{ allStreams.length }} streams
    </div>
    
    <div class="streams-grid">
      <Card 
        v-for="stream in filteredStreams" 
        :key="stream.id" 
        class="stream-card"
        @click="selectedStream = stream"
      >
        <template #content>
          <div class="card-header">
            <h3 class="card-title">{{ stream.lobbyName }}</h3>
            <div class="last-active">
              <i class="pi pi-clock"></i>
              <span>{{ getTimeAgo(stream.lastActive) }}</span>
            </div>
          </div>
          
          <div class="card-info">
            <div class="info-row">
              <i class="pi pi-map-marker info-icon"></i>
              <span class="info-text bold">{{ stream.trackName }}</span>
            </div>
            <div class="info-row">
              <i class="pi pi-trophy info-icon"></i>
              <span class="info-text">{{ stream.seriesName }}</span>
            </div>
            <div class="info-row">
              <i class="pi pi-hashtag info-icon"></i>
              <span class="info-text">Session {{ stream.sessionNumber }}</span>
            </div>
            <div class="info-row">
              <i class="pi pi-calendar info-icon"></i>
              <span class="info-text">{{ stream.raceDate }}</span>
            </div>
            <div class="info-row">
              <i class="pi pi-users info-icon"></i>
              <span class="info-text">{{ stream.teamName }}</span>
            </div>
            <div class="info-row">
              <i class="pi pi-car info-icon"></i>
              <span class="info-text">{{ stream.carName }}</span>
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <div v-if="filteredStreams.length === 0" class="no-results">
      No streams match your filters
    </div>
    
    <Dialog 
      :visible="showModal" 
      @update:visible="closeModal"
      header="Enter Passcode" 
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div v-if="selectedStream" class="modal-info">
        <p class="modal-lobby">{{ selectedStream.lobbyName }}</p>
        <p class="modal-track">{{ selectedStream.trackName }}</p>
      </div>
      
      <div>
        <label for="passcode" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Passcode</label>
        <Password 
          id="passcode"
          v-model="passcode" 
          :feedback="false"
          placeholder="Enter passcode"
          style="width: 100%"
          @keyup.enter="handleSubmit"
        />
        <p v-if="error" class="error-text">{{ error }}</p>
        <p class="hint-text">Hint: The passcode is 1234</p>
      </div>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="closeModal" />
        <Button label="Submit" @click="handleSubmit" />
      </template>
    </Dialog>
  </div>
</template>

<script>
import Card from 'primevue/card';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import RadioButton from 'primevue/radiobutton';
import Dialog from 'primevue/dialog';
import Password from 'primevue/password';

export default {
  name: 'App',
  components: {
    Card,
    Button,
    InputText,
    Dropdown,
    RadioButton,
    Dialog,
    Password
  },
  data() {
    return {
      searchQuery: '',
      showFilters: false,
      trackFilter: 'all',
      maxLastActive: 'all',
      maxTimeSinceStart: 'all',
      selectedStream: null,
      passcode: '',
      error: '',
      allStreams: [],
      lastActiveOptions: [
        { label: 'All', value: 'all' },
        { label: 'Last 5 min', value: 5 },
        { label: 'Last 15 min', value: 15 },
        { label: 'Last 30 min', value: 30 },
        { label: 'Last 1 hour', value: 60 },
        { label: 'Last 3 hours', value: 180 },
        { label: 'Last 12 hours', value: 720 },
        { label: 'Today', value: 1440 }
      ],
      timeSinceStartOptions: [
        { label: 'All', value: 'all' },
        { label: 'Last 5 min', value: 5 },
        { label: 'Last 15 min', value: 15 },
        { label: 'Last 30 min', value: 30 },
        { label: 'Last 1 hour', value: 60 },
        { label: 'Last 3 hours', value: 180 },
        { label: 'Last 12 hours', value: 720 },
        { label: 'Today', value: 1440 }
      ]
    };
  },
  async created() {
    await this.fetchStreams();
  },
  computed: {
    showModal() {
      return this.selectedStream !== null;
    },
    trackOptions() {
      const tracks = [...new Set(this.allStreams.map(s => s.trackName))].sort();
      return [
        { label: 'All Tracks', value: 'all' },
        ...tracks.map(track => ({ label: track, value: track }))
      ];
    },
    filteredStreams() {
      return this.allStreams.filter(stream => {
        if (this.searchQuery && !stream.lobbyName.toLowerCase().includes(this.searchQuery.toLowerCase())) {
          return false;
        }
        
        if (this.trackFilter !== 'all' && stream.trackName !== this.trackFilter) {
          return false;
        }
        
        if (this.maxLastActive !== 'all' && stream.lastActive > this.maxLastActive) {
          return false;
        }
        
        if (this.maxTimeSinceStart !== 'all' && stream.timeSinceStart > this.maxTimeSinceStart) {
          return false;
        }
        
        return true;
      });
    }
  },
  methods: {
    async fetchStreams() {
      try {
        const response = await fetch('https://rbp6s7lzj7shsh2oytpredade40lszob.lambda-url.eu-north-1.on.aws');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Normalize data to ensure all required fields exist
        const requiredFields = {
          id: '',
          lobbyName: '',
          trackName: '',
          seriesName: '',
          sessionNumber: '',
          raceDate: '',
          teamName: '',
          carName: '',
          lastActive: 0,
          timeSinceStart: 0
        };
        
        this.allStreams = data.map(stream => ({
          ...requiredFields,
          ...stream
        }));
      } catch (error) {
        console.error('Error fetching streams:', error);
        this.allStreams = [];
      }
    },
    getTimeAgo(minutes) {
      if (minutes < 1) return 'Just now';
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      const days = Math.floor(hours / 24);
      return `${days}d ago`;
    },
    handleSubmit() {
      if (this.passcode === '1234') {
        window.location.href = 'https://google.com';
      } else {
        this.error = 'Incorrect passcode. Please try again.';
        this.passcode = '';
      }
    },
    closeModal() {
      this.selectedStream = null;
      this.passcode = '';
      this.error = '';
    }
  },
  watch: {
    selectedStream(newVal) {
      console.log('Selected stream changed:', newVal);
    }
  }
};
</script>

<style scoped>
#app {
  padding: 2rem;
  background: linear-gradient(135deg, #e3f2fd 0%, #f5f5f5 100%);
  min-height: 100vh;
  max-width: 100%;
  box-sizing: border-box;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2.5rem;
  color: #1976d2;
  margin: 0 0 0.5rem 0;
}

.header p {
  color: #666;
  margin: 0;
}

.filters-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-label {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.results-count {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.streams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.stream-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stream-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1976d2;
  margin: 0;
}

.last-active {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #666;
  font-size: 0.85rem;
  white-space: nowrap;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  align-items: start;
  gap: 0.5rem;
}

.info-icon {
  color: #1976d2;
  margin-top: 2px;
  flex-shrink: 0;
}

.info-text {
  color: #333;
  font-size: 0.9rem;
  line-height: 1.4;
}

.info-text.bold {
  font-weight: 600;
}

.no-results {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 1.1rem;
}

.modal-info {
  background: #e3f2fd;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.modal-info p {
  margin: 0.25rem 0;
}

.modal-lobby {
  font-weight: 600;
  color: #1976d2;
}

.modal-track {
  color: #666;
  font-size: 0.9rem;
}

.hint-text {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.error-text {
  color: #d32f2f;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>