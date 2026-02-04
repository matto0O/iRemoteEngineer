<template>
  <div class="landing-container">
    <!-- Compact header -->
    <div class="compact-header">
      <h1>iRacing Data Streams</h1>
      <div class="controls">
        <PrimeButton
          :icon="isDarkMode ? 'pi pi-sun' : 'pi pi-moon'"
          @click="toggleDarkMode"
          :label="isDarkMode ? 'Light' : 'Dark'"
          severity="secondary"
          size="small"
          class="dark-mode-toggle"
        />
        <label class="mock-toggle">
          <input type="checkbox" :checked="useMockMode" @change="$emit('update:useMockMode', $event.target.checked)" />
          Use Mock Data
        </label>
        <div class="results-count">
          Showing {{ filteredStreams.length }} of {{ allStreams.length }} streams
        </div>
      </div>
    </div>

    <!-- Search and filters in a more compact layout -->
    <div class="search-filters-compact">
      <div class="search-bar">
        <span class="p-input-icon-left search-input">
          <i class="pi pi-search"></i>
          <InputText
            v-model="searchQuery"
            placeholder="Search lobby names..."
            style="width: 100%"
            @keyup.enter="applyFilters"
          />
        </span>
        <PrimeButton
          label="Search"
          icon="pi pi-search"
          @click="applyFilters"
          size="small"
          :loading="isLoading"
        />
        <PrimeButton
          :label="showFilters ? 'Hide' : 'Filters'"
          icon="pi pi-filter"
          :severity="showFilters ? 'primary' : 'secondary'"
          @click="showFilters = !showFilters"
          size="small"
        />
        <div class="sort-group">
          <Dropdown
            v-model="sortField"
            :options="sortFieldOptions"
            optionLabel="label"
            optionValue="value"
            class="sort-dropdown"
          />
          <PrimeButton
            :icon="sortOrder === 'asc' ? 'pi pi-sort-amount-up' : 'pi pi-sort-amount-down'"
            severity="secondary"
            size="small"
            @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
          />
        </div>
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
          <div v-for="option in last_activeOptions" :key="option.value" class="radio-option">
            <RadioButton
              v-model="maxLastActive"
              :inputId="'active-' + option.value"
              :value="option.value"
            />
            <label :for="'active-' + option.value">{{ option.label }}</label>
          </div>
        </div>

        <div class="filter-group">
          <label class="filter-label">Max Time Since Lobby Creation</label>
          <div v-for="option in lobbyCreationOptions" :key="option.value" class="radio-option">
            <RadioButton
              v-model="maxTimeSinceCreation"
              :inputId="'creation-' + option.value"
              :value="option.value"
            />
            <label :for="'creation-' + option.value">{{ option.label }}</label>
          </div>
        </div>
      </div>
    </div>

    <!-- Lobby panels (streams) displayed prominently -->
    <div class="streams-grid">
      <Card
        v-for="stream in filteredStreams"
        :key="stream.id"
        class="stream-card"
        @click="selectStream(stream)"
      >
        <template #content>
          <div class="card-header">
            <h3 class="card-title">{{ stream.lobby_name }}</h3>
            <div class="time-indicators">
              <div class="last-active">
                <i class="pi pi-clock"></i>
                <span>{{ getTimeAgoFromTimestamp(stream.last_active) }}</span>
              </div>
              <div class="created-at">
                <i class="pi pi-calendar-plus"></i>
                <span>{{ getTimeAgoFromTimestamp(stream.created_at) }}</span>
              </div>
            </div>
          </div>

          <div class="card-info">
            <div class="info-row">
              <i class="pi pi-map-marker info-icon"></i>
              <span class="info-text bold">
                {{ stream.track_name }}
                <template v-if="stream.track_config"> - {{ stream.track_config }}</template>
              </span>
            </div>
            <div class="info-row">
              <i class="pi pi-trophy info-icon"></i>
              <span class="info-text">{{ getSeriesName(stream.series_id) }}</span>
            </div>
            <div class="info-row">
              <i class="pi pi-hashtag info-icon"></i>
              <span class="info-text">Session {{ stream.session_id }} ({{ stream.subsession_id }})</span>
            </div>
            <div class="info-row">
              <i class="pi pi-users info-icon"></i>
              <span class="info-text">{{ stream.team_name }}<template v-if="stream.player_car_number"> (#{{ stream.player_car_number }})</template></span>
            </div>
            <div class="info-row" v-if="getClassForStream(stream)">
              <i class="pi pi-flag info-icon"></i>
              <span class="info-text">{{ getClassForStream(stream) }}</span>
            </div>
            <div class="info-row">
              <i class="pi pi-car info-icon"></i>
              <span class="info-text">{{ getCarModelName(stream.car_model_id) }}</span>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <div v-if="filteredStreams.length === 0" class="no-results">
      No streams match your filters
    </div>

    <div class="load-more-container">
      <PrimeButton
        label="Load More"
        icon="pi pi-chevron-down"
        @click="loadMore"
        :loading="isLoading"
        :disabled="!hasNextPage"
        severity="secondary"
      />
    </div>

    <PrimeDialog
      :visible="showModal"
      @update:visible="closeModal"
      header="Enter Passcode"
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div v-if="selectedStream" class="modal-info">
        <p class="modal-lobby">{{ selectedStream.lobby_name }}</p>
        <p class="modal-track">{{ selectedStream.track_name }}</p>
      </div>

      <div>
        <label for="passcode" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Passcode</label>
        <Password
          id="passcode"
          v-model="passcode"
          :feedback="false"
          placeholder="Enter passcode"
          style="width: 100%"
          :disabled="isAuthenticating"
          @keyup.enter="handleSubmit"
        />
        <p v-if="error" class="error-text">{{ error }}</p>
      </div>

      <template #footer>
        <PrimeButton label="Cancel" severity="secondary" @click="closeModal" :disabled="isAuthenticating" />
        <PrimeButton
          label="Submit"
          @click="handleSubmit"
          :loading="isAuthenticating"
          :disabled="isAuthenticating"
        />
      </template>
    </PrimeDialog>
  </div>
</template>

<script>
import Card from 'primevue/card';
import PrimeButton from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import RadioButton from 'primevue/radiobutton';
import PrimeDialog from 'primevue/dialog';
import Password from 'primevue/password';
import { useDarkMode } from '../composables/useDarkMode.js';
import useCarData from '../composables/useCarData.js';
import { fetchMockLobbies } from '../composables/mockDataService.js';

export default {
  name: 'LandingPage',
  components: {
    Card,
    PrimeButton,
    InputText,
    Dropdown,
    RadioButton,
    PrimeDialog,
    Password
  },
  props: {
    useMockMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['lobby-selected', 'update:useMockMode'],
  setup() {
    const { isDarkMode, toggleDarkMode } = useDarkMode();
    const { getSeriesName, getCarModelName, getClassNameForCar } = useCarData();
    return {
      isDarkMode,
      toggleDarkMode,
      getSeriesName,
      getCarModelName,
      getClassNameForCar
    };
  },
  data() {
    return {
      // UI-bound filter values (pending — not applied until Search is pressed)
      searchQuery: '',
      showFilters: false,
      trackFilter: 'all',
      maxLastActive: 'all',
      maxTimeSinceCreation: 'all',

      // Applied filter values (active after Search is pressed)
      appliedSearchQuery: '',
      appliedTrackFilter: 'all',
      appliedMaxLastActive: 'all',
      appliedMaxTimeSinceCreation: 'all',

      // Sort state (applied immediately, no Search button needed)
      sortField: 'last_active',
      sortOrder: 'asc',
      sortFieldOptions: [
        { label: 'Last Active', value: 'last_active' },
        { label: 'Created', value: 'created_at' },
        { label: 'Name', value: 'lobby_name' },
      ],

      // Pagination state
      currentPage: 1,
      hasNextPage: false,
      isLoading: false,

      selectedStream: null,
      passcode: '',
      error: '',
      isAuthenticating: false,
      allStreams: [],
      last_activeOptions: [
        { label: 'All', value: 'all' },
        { label: 'Last 5 min', value: 5 },
        { label: 'Last 15 min', value: 15 },
        { label: 'Last 30 min', value: 30 },
        { label: 'Last 1 hour', value: 60 },
        { label: 'Last 3 hours', value: 180 },
        { label: 'Last 12 hours', value: 720 },
        { label: 'Today', value: 1440 }
      ],
      lobbyCreationOptions: [
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
    if (this.useMockMode) {
      await this.fetchMockStreams();
    } else {
      await this.fetchStreams();
    }
  },
  computed: {
    showModal() {
      return this.selectedStream !== null && !this.useMockMode;
    },
    trackOptions() {
      const tracks = [...new Set(this.allStreams.map(s => s.track_name))].sort();
      return [
        { label: 'All Tracks', value: 'all' },
        ...tracks.map(track => ({ label: track, value: track }))
      ];
    },
    filteredStreams() {
      // Search and time-based filters are applied server-side via the API.
      // Only track filter is applied client-side.
      const filtered = this.allStreams.filter(stream => {
        if (this.appliedTrackFilter !== 'all' && stream.track_name !== this.appliedTrackFilter) {
          return false;
        }

        return true;
      });

      const field = this.sortField;
      const dir = this.sortOrder === 'asc' ? 1 : -1;

      return filtered.sort((a, b) => {
        const aVal = a[field];
        const bVal = b[field];
        if (typeof aVal === 'string') {
          return dir * aVal.localeCompare(bVal);
        }
        return dir * (aVal - bVal);
      });
    }
  },
  methods: {
    async fetchMockStreams(page = 1, append = false) {
      this.isLoading = true;
      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 400));

        const filters = {};
        if (this.appliedSearchQuery) filters.search = this.appliedSearchQuery;
        const lastActive = this.minutesToTimeString(this.appliedMaxLastActive);
        if (lastActive) filters.lastactivetime = lastActive;
        const creation = this.minutesToTimeString(this.appliedMaxTimeSinceCreation);
        if (creation) filters.timefromcreation = creation;

        const data = fetchMockLobbies(page, filters);

        if (append) {
          this.allStreams = [...this.allStreams, ...data.items];
        } else {
          this.allStreams = data.items;
        }
        this.currentPage = page;
        this.hasNextPage = data.pagination.hasNextPage;
      } finally {
        this.isLoading = false;
      }
    },
    getClassForStream(stream) {
      return this.getClassNameForCar(stream.series_id, stream.car_model_id);
    },
    minutesToTimeString(minutes) {
      if (minutes === 'all') return null;
      if (minutes >= 1440) return `${Math.floor(minutes / 1440)}d`;
      if (minutes >= 60) return `${Math.floor(minutes / 60)}h`;
      return `${minutes}m`;
    },
    buildFetchUrl(page) {
      const url = new URL(import.meta.env.VITE_LOBBIES_URL);
      url.searchParams.set('page', page);

      if (this.appliedSearchQuery) url.searchParams.set('search', this.appliedSearchQuery);

      const lastActive = this.minutesToTimeString(this.appliedMaxLastActive);
      if (lastActive) url.searchParams.set('lastactivetime', lastActive);

      const creation = this.minutesToTimeString(this.appliedMaxTimeSinceCreation);
      if (creation) url.searchParams.set('timefromcreation', creation);

      return url.toString();
    },
    async fetchStreams(page = 1, append = false) {
      this.isLoading = true;
      try {
        const url = this.buildFetchUrl(page);
        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        const requiredFields = {
          id: '',
          lobby_name: '',
          track_name: '',
          track_config: '',
          series_name: '',
          session_id: '',
          subsession_id: '',
          session_start_time: '',
          team_name: '',
          car_name: '',
          timestamp: '',
          last_active: 0,
          time_since_start: 0,
          created_at: 0
        };

        const items = (data.items || []).map(stream => ({
          ...requiredFields,
          ...stream
        }));

        if (append) {
          this.allStreams = [...this.allStreams, ...items];
        } else {
          this.allStreams = items;
        }

        this.currentPage = page;
        this.hasNextPage = data.pagination?.hasNextPage ?? false;
      } catch (error) {
        console.error('Error fetching streams:', error);
        if (!append) {
          this.allStreams = [];
        }
        this.hasNextPage = false;
      } finally {
        this.isLoading = false;
      }
    },
    applyFilters() {
      // Copy pending filter values to applied
      this.appliedSearchQuery = this.searchQuery;
      this.appliedTrackFilter = this.trackFilter;
      this.appliedMaxLastActive = this.maxLastActive;
      this.appliedMaxTimeSinceCreation = this.maxTimeSinceCreation;

      // Reset and fetch fresh from page 1
      if (this.useMockMode) {
        this.fetchMockStreams(1, false);
      } else {
        this.fetchStreams(1, false);
      }
    },
    loadMore() {
      if (this.hasNextPage && !this.isLoading) {
        const nextPage = this.currentPage + 1;
        if (this.useMockMode) {
          this.fetchMockStreams(nextPage, true);
        } else {
          this.fetchStreams(nextPage, true);
        }
      }
    },
    getMinutesFromTimestamp(timestamp) {
      // Handle Unix epoch seconds (float) - convert to milliseconds
      const ts = typeof timestamp === 'string'
        ? new Date(timestamp).getTime()
        : timestamp * 1000;
      return Math.ceil((Date.now() - ts) / 60000);
    },
    getTimeAgoFromTimestamp(timestamp) {
      const minutes = this.getMinutesFromTimestamp(timestamp);
      if (minutes < 1) return 'Just now';
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.ceil(minutes / 60);
      return `${hours}h ago`;
    },
    selectStream(stream) {
      if (this.useMockMode) {
        // In mock mode, skip authentication
        this.$emit('lobby-selected', { lobby_name: stream.lobby_name, auth_token: 'mock-token' });
      } else {
        this.selectedStream = stream;
      }
    },
    async handleSubmit() {
      if (!this.selectedStream) return;

      this.error = '';

      if (this.passcode.length < 4 || this.passcode.length > 20) {
        this.error = 'Passcode must be between 4 and 20 characters';
        return;
      }

      try {
        const authEndpoint = import.meta.env.VITE_LOBBY_AUTH_URL;

        const response = await fetch(authEndpoint, {
          method: 'POST',
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            lobby_name: this.selectedStream.lobby_name,
            passcode: this.passcode
          })
        });

        const data = await response.json();

        if (!response.ok) {
          this.error = data.error || 'Authentication failed. Please try again.';
          this.passcode = '';
          return;
        }

        this.$emit('lobby-selected', { lobby_name: data.lobby_name, auth_token: data.token });
        this.closeModal();

      } catch (error) {
        console.error('Authentication error:', error);
        this.error = 'Failed to connect to authentication server. Please try again.';
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
    useMockMode(newVal) {
      if (newVal) {
        this.fetchMockStreams(1, false);
      } else {
        this.fetchStreams(1, false);
      }
    }
  }
};
</script>

<style scoped>
.landing-container {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--app-bg-gradient-start) 0%, var(--app-bg-gradient-end) 100%);
  min-height: 100vh;
  max-width: 100%;
  box-sizing: border-box;
}

.compact-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
}

.compact-header h1 {
  font-size: 1.8rem;
  color: var(--primary-blue);
  margin: 0;
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.dark-mode-toggle {
  flex-shrink: 0;
}

.mock-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
}

.mock-toggle input[type="checkbox"] {
  cursor: pointer;
}

.results-count {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.search-filters-compact {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px var(--card-shadow);
}

.search-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  flex: 1;
}

.sort-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

.sort-dropdown {
  min-width: 140px;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-label {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.streams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  width: 100%;
  margin-bottom: 2rem;
}

.stream-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stream-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px var(--card-shadow-hover) !important;
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
  color: var(--primary-blue);
  margin: 0;
  flex: 1;
}

.time-indicators {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-end;
}

.last-active,
.created-at {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
  white-space: nowrap;
}

.created-at {
  color: var(--text-muted);
  font-size: 0.75rem;
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
  color: var(--primary-blue);
  margin-top: 2px;
  flex-shrink: 0;
}

.info-text {
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.info-text.bold {
  font-weight: 600;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 1.1rem;
}

.load-more-container {
  display: flex;
  justify-content: center;
  padding: 0.5rem 0 2rem;
}

.modal-info {
  background: var(--primary-blue-light);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.modal-info p {
  margin: 0.25rem 0;
}

.modal-lobby {
  font-weight: 600;
  color: var(--primary-blue);
}

.modal-track {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.error-text {
  color: #d32f2f;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .landing-container {
    padding: 0.5rem 1rem;
  }

  .compact-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .compact-header h1 {
    font-size: 1.5rem;
  }

  .search-bar {
    flex-direction: column;
    gap: 0.75rem;
  }

  .sort-group {
    margin-left: 0;
  }

  .streams-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 1600px) {
  .streams-grid {
    grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  }
}
</style>
