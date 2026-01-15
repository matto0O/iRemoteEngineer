<template>
  <div class="tyre-container">
    <Card class="tyre-card">
      <template #title>
        <div class="card-header">
          <div class="card-header-left">
            <i class="pi pi-circle"></i>
            <span>Tyre Data Dashboard</span>
          </div>
          <Button
            :icon="viewMode === 'graphical' ? 'pi pi-table' : 'pi pi-chart-bar'"
            @click="toggleViewMode"
            size="small"
            severity="secondary"
            :label="viewMode === 'graphical' ? 'Table' : 'Graphical'"
            class="view-toggle-btn"
          />
        </div>
      </template>
      <template #content>
        <!-- Tyre Grid Visual (Graphical View) -->
        <div v-if="viewMode === 'graphical'" class="tyre-visual-grid">
          <div v-for="tyre in tyreData" :key="tyre.position" class="tyre-visual-item">
            <div class="tyre-position-label">
              <i class="pi pi-circle-fill"></i>
              {{ tyre.position }}
            </div>
            <div class="tyre-metrics">
              <div class="metric-row">
                <span class="metric-label">
                  <i class="pi pi-sun"></i> Temperatures
                </span>
                <div class="temp-bars">
                  <div class="temp-bar-wrapper">
                    <span class="bar-label">Left</span>
                    <div class="temp-bar" :style="{ height: getTempBarHeight(tyre.leftCarcassTemp), backgroundColor: getTempBarColor(tyre.leftCarcassTemp) }"></div>
                    <span class="temp-value">{{ formatValue(convertTemp(tyre.leftCarcassTemp)) }}{{ getTempUnit() }}</span>
                  </div>
                  <div class="temp-bar-wrapper">
                    <span class="bar-label">Middle</span>
                    <div class="temp-bar" :style="{ height: getTempBarHeight(tyre.middleCarcassTemp), backgroundColor: getTempBarColor(tyre.middleCarcassTemp) }"></div>
                    <span class="temp-value">{{ formatValue(convertTemp(tyre.middleCarcassTemp)) }}{{ getTempUnit() }}</span>
                  </div>
                  <div class="temp-bar-wrapper">
                    <span class="bar-label">Right</span>
                    <div class="temp-bar" :style="{ height: getTempBarHeight(tyre.rightCarcassTemp), backgroundColor: getTempBarColor(tyre.rightCarcassTemp) }"></div>
                    <span class="temp-value">{{ formatValue(convertTemp(tyre.rightCarcassTemp)) }}{{ getTempUnit() }}</span>
                  </div>
                </div>
              </div>
              <div class="metric-row">
                <span class="metric-label">
                  <i class="pi pi-chart-pie"></i> Tread Life Left
                </span>
                <div class="wear-bars">
                  <div class="wear-bar-wrapper">
                    <span class="bar-label">Left</span>
                    <div class="wear-bar" :style="{ height: getWearBarHeight(tyre.leftTreadRemaining), backgroundColor: getWearBarColor(tyre.leftTreadRemaining) }"></div>
                    <span class="wear-value">{{ formatValue(tyre.leftTreadRemaining) }}%</span>
                  </div>
                  <div class="wear-bar-wrapper">
                    <span class="bar-label">Middle</span>
                    <div class="wear-bar" :style="{ height: getWearBarHeight(tyre.middleTreadRemaining), backgroundColor: getWearBarColor(tyre.middleTreadRemaining) }"></div>
                    <span class="wear-value">{{ formatValue(tyre.middleTreadRemaining) }}%</span>
                  </div>
                  <div class="wear-bar-wrapper">
                    <span class="bar-label">Right</span>
                    <div class="wear-bar" :style="{ height: getWearBarHeight(tyre.rightTreadRemaining), backgroundColor: getWearBarColor(tyre.rightTreadRemaining) }"></div>
                    <span class="wear-value">{{ formatValue(tyre.rightTreadRemaining) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Detailed Data Table (Table View) -->
        <div v-if="viewMode === 'table'" class="table-section">
          <DataTable :value="tyreData" :rowHover="true" stripedRows class="tyre-table">
            <Column field="position" header="Tyre" style="min-width: 120px"></Column>
            <Column field="leftCarcassTemp" header="Left Temp" class="left-side-col">
              <template #body="slotProps">
                <span :style="{ color: getTempClass(slotProps.data.leftCarcassTemp), fontWeight: '600' }">
                  {{ formatValue(convertTemp(slotProps.data.leftCarcassTemp)) }}{{ getTempUnit() }}
                </span>
              </template>
            </Column>
            <Column field="leftTreadRemaining" header="Left Wear" class="left-side-col">
              <template #body="slotProps">
                <span :style="{ color: getWearClass(slotProps.data.leftTreadRemaining), fontWeight: '600' }">
                  {{ formatValue(slotProps.data.leftTreadRemaining) }}%
                </span>
              </template>
            </Column>
            <Column field="middleCarcassTemp" header="Middle Temp" class="middle-side-col">
              <template #body="slotProps">
                <span :style="{ color: getTempClass(slotProps.data.middleCarcassTemp), fontWeight: '600' }">
                  {{ formatValue(convertTemp(slotProps.data.middleCarcassTemp)) }}{{ getTempUnit() }}
                </span>
              </template>
            </Column>
            <Column field="middleTreadRemaining" header="Middle Wear" class="middle-side-col">
              <template #body="slotProps">
                <span :style="{ color: getWearClass(slotProps.data.middleTreadRemaining), fontWeight: '600' }">
                  {{ formatValue(slotProps.data.middleTreadRemaining) }}%
                </span>
              </template>
            </Column>
            <Column field="rightCarcassTemp" header="Right Temp" class="right-side-col">
              <template #body="slotProps">
                <span :style="{ color: getTempClass(slotProps.data.rightCarcassTemp), fontWeight: '600' }">
                  {{ formatValue(convertTemp(slotProps.data.rightCarcassTemp)) }}{{ getTempUnit() }}
                </span>
              </template>
            </Column>
            <Column field="rightTreadRemaining" header="Right Wear" class="right-side-col">
              <template #body="slotProps">
                <span :style="{ color: getWearClass(slotProps.data.rightTreadRemaining), fontWeight: '600' }">
                  {{ formatValue(slotProps.data.rightTreadRemaining) }}%
                </span>
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import useRaceData from '@/composables/useRaceData';
import { useUnits } from '@/composables/useUnits';

const props = defineProps({
  socket: {
    type: Object,
    required: true
  }
})

const { data } = useRaceData(props.socket);
const { convertTemp, getTempUnit } = useUnits();

// Load saved preference from localStorage
const loadViewMode = () => {
  const saved = localStorage.getItem('tyreDetailsViewMode')
  return saved !== null ? saved : 'graphical'
}

const viewMode = ref(loadViewMode()); // 'graphical' or 'table'

// Save preference to localStorage whenever it changes
watch(viewMode, (value) => {
  localStorage.setItem('tyreDetailsViewMode', value)
})

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'graphical' ? 'table' : 'graphical';
};

const tyreDataSource = computed(() => {
  return data.value?.tyres || {
    front_left: {},
    front_right: {},
    rear_left: {},
    rear_right: {}
  };
});

const tyreData = computed(() => {
  const tyres = tyreDataSource.value;

  return [
    {
      position: "Front Left",
      leftCarcassTemp: tyres.front_left?.left_carcass_temp ?? 0,
      middleCarcassTemp: tyres.front_left?.middle_carcass_temp ?? 0,
      rightCarcassTemp: tyres.front_left?.right_carcass_temp ?? 0,
      leftTreadRemaining: tyres.front_left?.left_tread_remaning ?? 0,
      middleTreadRemaining: tyres.front_left?.middle_tread_remaning ?? 0,
      rightTreadRemaining: tyres.front_left?.right_tread_remaning ?? 0
    },
    {
      position: "Front Right",
      leftCarcassTemp: tyres.front_right?.left_carcass_temp ?? 0,
      middleCarcassTemp: tyres.front_right?.middle_carcass_temp ?? 0,
      rightCarcassTemp: tyres.front_right?.right_carcass_temp ?? 0,
      leftTreadRemaining: tyres.front_right?.left_tread_remaning ?? 0,
      middleTreadRemaining: tyres.front_right?.middle_tread_remaning ?? 0,
      rightTreadRemaining: tyres.front_right?.right_tread_remaning ?? 0
    },
    {
      position: "Rear Left",
      leftCarcassTemp: tyres.rear_left?.left_carcass_temp ?? 0,
      middleCarcassTemp: tyres.rear_left?.middle_carcass_temp ?? 0,
      rightCarcassTemp: tyres.rear_left?.right_carcass_temp ?? 0,
      leftTreadRemaining: tyres.rear_left?.left_tread_remaning ?? 0,
      middleTreadRemaining: tyres.rear_left?.middle_tread_remaning ?? 0,
      rightTreadRemaining: tyres.rear_left?.right_tread_remaning ?? 0
    },
    {
      position: "Rear Right",
      leftCarcassTemp: tyres.rear_right?.left_carcass_temp ?? 0,
      middleCarcassTemp: tyres.rear_right?.middle_carcass_temp ?? 0,
      rightCarcassTemp: tyres.rear_right?.right_carcass_temp ?? 0,
      leftTreadRemaining: tyres.rear_right?.left_tread_remaning ?? 0,
      middleTreadRemaining: tyres.rear_right?.middle_tread_remaning ?? 0,
      rightTreadRemaining: tyres.rear_right?.right_tread_remaning ?? 0
    }
  ];
});

const formatValue = (value) => {
  return typeof value === 'number' ? Math.round(value) : value;
};

const getTempBarHeight = (temp) => {
  const maxTemp = 120;
  const percentage = Math.min((temp / maxTemp) * 100, 100);
  return `${Math.max(percentage, 15)}%`; // Minimum 15% for visibility
};

const getTempBarColor = (temp) => {
  // Color spectrum: blue (<60) -> light blue (60-75) -> green (75-90) -> orange (>90) -> red (>100)
  if (temp >= 100) return '#dc3545'; // Red for very hot
  if (temp >= 90) {
    // Orange range (90-100)
    const ratio = (temp - 90) / 10;
    return interpolateColor('#ff8c00', '#dc3545', ratio);
  }
  if (temp >= 75) {
    // Green to orange range (75-90)
    const ratio = (temp - 75) / 15;
    return interpolateColor('#32cd32', '#ff8c00', ratio);
  }
  if (temp >= 60) {
    // Light blue to green range (60-75)
    const ratio = (temp - 60) / 15;
    return interpolateColor('#4facfe', '#32cd32', ratio);
  }
  // Very cold: dark blue to light blue (0-60)
  const ratio = Math.max(0, temp / 60);
  return interpolateColor('#0066cc', '#4facfe', ratio);
};

const getWearBarHeight = (wear) => {
  const percentage = Math.min(wear, 100);
  return `${Math.max(percentage, 15)}%`; // Minimum 15% for visibility
};

const getWearBarColor = (wear) => {
  // Color spectrum: dark lime green (100%) -> yellow (80%) -> orange (70%) -> red (50%)
  if (wear >= 80) {
    // Dark lime green to yellow (80-100%)
    const ratio = (100 - wear) / 20;
    return interpolateColor('#4a7c17', '#9a9a0a', ratio);
  }
  if (wear >= 70) {
    // Yellow to orange (70-80%)
    const ratio = (80 - wear) / 10;
    return interpolateColor('#9a9a0a', '#d97706', ratio);
  }
  if (wear >= 50) {
    // Orange to red (50-70%)
    const ratio = (70 - wear) / 20;
    return interpolateColor('#d97706', '#dc3545', ratio);
  }
  // Very low wear: red
  return '#dc3545';
};

// Helper function to interpolate between two hex colors
const interpolateColor = (color1, color2, ratio) => {
  const hex = (color) => {
    const c = color.replace('#', '');
    return [
      parseInt(c.substring(0, 2), 16),
      parseInt(c.substring(2, 4), 16),
      parseInt(c.substring(4, 6), 16)
    ];
  };

  const [r1, g1, b1] = hex(color1);
  const [r2, g2, b2] = hex(color2);

  const r = Math.round(r1 + (r2 - r1) * ratio);
  const g = Math.round(g1 + (g2 - g1) * ratio);
  const b = Math.round(b1 + (b2 - b1) * ratio);

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
};

const getTempClass = (temp) => {
  // Return the color directly using the same logic as getTempBarColor
  return getTempBarColor(temp);
};

const getWearClass = (wear) => {
  // Return the color directly using the same logic as getWearBarColor
  return getWearBarColor(wear);
};
</script>

<style scoped>
.tyre-container {
  width: 100%;
  height: 100%;
  padding: 0;
}

.tyre-card {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.dark-mode .tyre-card {
  background: linear-gradient(135deg, #3a7fb0 0%, #00a8b0 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.tyre-card :deep(.p-card-body) {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0;
}

.tyre-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  padding: 1rem;
  border-radius: 16px 16px 0 0;
  margin: 0;
}

.dark-mode .tyre-card :deep(.p-card-title) {
  background: linear-gradient(135deg, #3a7fb0 0%, #00a8b0 100%);
}

.tyre-card :deep(.p-card-content) {
  padding: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-header i {
  font-size: 1.25rem;
}

.view-toggle-btn {
  flex-shrink: 0;
}

.tyre-visual-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.tyre-visual-item {
  background: var(--filter-content-bg, #f8f9fa);
  border-radius: 10px;
  padding: 0.75rem;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.tyre-visual-item:hover {
  border-color: #4facfe;
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.2);
  transform: translateY(-2px);
}

.tyre-position-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e9ecef;
}

.tyre-position-label i {
  color: #4facfe;
  font-size: 0.9rem;
}

.tyre-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #495057;
}

.metric-label i {
  color: #00f2fe;
  font-size: 1rem;
}

.temp-bars,
.wear-bars {
  display: flex;
  gap: 0.75rem;
  height: 120px;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  align-items: flex-end;
}

.temp-bar-wrapper,
.wear-bar-wrapper {
  flex: 1 1 0;
  min-width: 0;
  max-width: 33.33%;
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  gap: 0.5rem;
  height: 100%;
  justify-content: flex-start;
  position: relative;
}

.temp-bar,
.wear-bar {
  width: 24px;
  border-radius: 6px;
  min-height: 15%;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
}

.temp-bar:hover,
.wear-bar:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.temp-value,
.wear-value {
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  background: rgba(0, 0, 0, 0.4);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  position: absolute;
  left: 50%;
  bottom: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
}

.bar-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.table-section {
  margin-top: 0;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e9ecef;
}

.table-title i {
  color: #4facfe;
}

.tyre-table {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.p-datatable) {
  font-size: 0.95rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 0.875rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #dee2e6;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.875rem;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8f9fa !important;
}

/* Visual distinction between tyre sides */
/* Border after Tyre column */
:deep(.tyre-table .p-datatable-tbody > tr > td:first-child),
:deep(.tyre-table .p-datatable-thead > tr > th:first-child) {
  border-right: 2px solid var(--table-border);
}

/* Border after left wear (last column of left side) */
:deep(.tyre-table .p-datatable-tbody > tr > td:nth-child(3)),
:deep(.tyre-table .p-datatable-thead > tr > th:nth-child(3)) {
  border-right: 2px solid var(--table-border);
}

/* Border after middle wear (last column of middle side) */
:deep(.tyre-table .p-datatable-tbody > tr > td:nth-child(5)),
:deep(.tyre-table .p-datatable-thead > tr > th:nth-child(5)) {
  border-right: 2px solid var(--table-border);
}

@media (max-width: 768px) {
  .tyre-visual-grid {
    grid-template-columns: 1fr;
  }
}

/* Dark mode overrides */
.dark-mode .tyre-visual-item {
  background: var(--card-bg);
  border-color: var(--border-color);
}

.dark-mode .tyre-visual-item:hover {
  border-color: #4facfe;
}

.dark-mode .tyre-position-label {
  color: var(--text-primary);
  border-bottom-color: var(--border-color);
}

.dark-mode .metric-label {
  color: var(--text-secondary);
}

.dark-mode .bar-label {
  color: var(--text-secondary);
}

.dark-mode .temp-bars,
.dark-mode .wear-bars {
  background: rgba(255, 255, 255, 0.02);
}
</style>
