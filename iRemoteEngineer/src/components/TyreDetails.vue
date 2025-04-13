<template>
    <div class="tire-data-container">
      <h3>Tire Data Dashboard</h3>
        <DataTable :value="tireData" :rowHover="true" stripedRows responsiveLayout="scroll">
            <Column field="position" header="Position"></Column>
            <Column field="leftCarcassTemp" header="Left Carcass Temp">
                <template #body="slotProps">
                    {{ formatValue(slotProps.data.leftCarcassTemp) }}°C
                </template>
            </Column>
            <Column field="middleCarcassTemp" header="Middle Carcass Temp">
                <template #body="slotProps">
                    {{ formatValue(slotProps.data.middleCarcassTemp) }}°C
                </template>
            </Column>
            <Column field="rightCarcassTemp" header="Right Carcass Temp">
                <template #body="slotProps">
                    {{ formatValue(slotProps.data.rightCarcassTemp) }}°C
                </template>
            </Column>
            <Column field="leftTreadRemaining" header="Left Tread Remaining">
                <template #body="slotProps">
                    {{ formatValue(slotProps.data.leftTreadRemaining) }}%
                </template>
            </Column>
            <Column field="middleTreadRemaining" header="Middle Tread Remaining">
                <template #body="slotProps">
                    {{ formatValue(slotProps.data.middleTreadRemaining) }}%
                </template>
            </Column>
            <Column field="rightTreadRemaining" header="Right Tread Remaining">
                <template #body="slotProps">
                    {{ formatValue(slotProps.data.rightTreadRemaining) }}%
                </template>
            </Column>
        </DataTable>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import DataTable from 'primevue/datatable';
  import Column from 'primevue/column';
  import useRaceData from '@/composables/useRaceData';
  
  const props = defineProps({
  socket: {
    type: Object,
    required: true
  }
})

  // Get shared race data from composable
  const { data } = useRaceData(props.socket);
  
  // Watch race data for tire information
  const tireDataSource = computed(() => {
    return data.value?.tyres || {
      front_left: {},
      front_right: {},
      rear_left: {},
      rear_right: {}
    };
  });
  
  // Transform tire data into table format
  const tireData = computed(() => {
    const tyres = tireDataSource.value;
    
    return [
      {
        position: "Front Left",
        leftCarcassTemp: tyres.front_left.left_carcass_temp || 0,
        middleCarcassTemp: tyres.front_left.middle_carcass_temp || 0,
        rightCarcassTemp: tyres.front_left.right_carcass_temp || 0,
        leftTreadRemaining: tyres.front_left.left_tread_remaning || 0,
        middleTreadRemaining: tyres.front_left.middle_tread_remaning || 0,
        rightTreadRemaining: tyres.front_left.right_tread_remaning || 0
      },
      {
        position: "Front Right",
        leftCarcassTemp: tyres.front_right.left_carcass_temp || 0,
        middleCarcassTemp: tyres.front_right.middle_carcass_temp || 0,
        rightCarcassTemp: tyres.front_right.right_carcass_temp || 0,
        leftTreadRemaining: tyres.front_right.left_tread_remaning || 0,
        middleTreadRemaining: tyres.front_right.middle_tread_remaning || 0,
        rightTreadRemaining: tyres.front_right.right_tread_remaning || 0
      },
      {
        position: "Rear Left",
        leftCarcassTemp: tyres.rear_left.left_carcass_temp || 0,
        middleCarcassTemp: tyres.rear_left.middle_carcass_temp || 0,
        rightCarcassTemp: tyres.rear_left.right_carcass_temp || 0,
        leftTreadRemaining: tyres.rear_left.left_tread_remaning || 0,
        middleTreadRemaining: tyres.rear_left.middle_tread_remaning || 0,
        rightTreadRemaining: tyres.rear_left.right_tread_remaning || 0
      },
      {
        position: "Rear Right",
        leftCarcassTemp: tyres.rear_right.left_carcass_temp || 0,
        middleCarcassTemp: tyres.rear_right.middle_carcass_temp || 0,
        rightCarcassTemp: tyres.rear_right.right_carcass_temp || 0,
        leftTreadRemaining: tyres.rear_right.left_tread_remaning || 0,
        middleTreadRemaining: tyres.rear_right.middle_tread_remaning || 0,
        rightTreadRemaining: tyres.rear_right.right_tread_remaning || 0
      }
    ];
  });
  
  // Format numeric values with 2 decimal places
  const formatValue = (value) => {
    return typeof value === 'number' 
      ? value.toFixed(2) 
      : value;
  };
  </script>
  
  <style scoped>
  .tire-data-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
    border-radius: 8px;
    background-color: #f8f8f8;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  h3 {
    margin-top: 0;
    color: #333;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .connection-error {
    background-color: #fff3f3;
    color: #ff3333;
    padding: 0.5rem;
    margin-bottom: 1rem;
    border-radius: 4px;
    text-align: center;
  }
  
  :deep(.p-datatable) {
    font-size: 0.9rem;
  }
  
  :deep(.p-datatable .p-datatable-thead > tr > th) {
    background-color: #f1f1f1;
    padding: 0.5rem 0.75rem;
  }
  
  :deep(.p-datatable .p-datatable-tbody > tr > td) {
    padding: 0.5rem 0.75rem;
  }
  </style>