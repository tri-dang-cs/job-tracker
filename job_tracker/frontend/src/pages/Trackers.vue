<script setup>

import { state, storedToken } from '../state';

import { ref } from 'vue';
import Button from 'primevue/button';
import Panel from 'primevue/panel';
import InputText from 'primevue/inputtext';

import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';
import InputNumber from 'primevue/inputnumber';
import axios from 'axios';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';


// get all email
const trackers = ref([]);
axios.post('/trackers', { token: storedToken.value })
    .then(response => {
        trackers.value = response.data;
    });


</script>
<template>
    <h1 v-if="state.isAdmin">All Trackers</h1>
    <h1 v-else>My Trackers</h1>

   <DataTable :value="trackers" 
      showGridlines tableStyle="min-width: 50rem"
      resizableColumns columnResizeMode="fit"
      sortField="date_created" :sortOrder="-1" 
   >
      <Column field="date_created" header="Date" sortable></Column>
      <Column v-if="state.isAdmin" field="token" header="User" sortable ></Column>
      <Column field="secret" header="Link" sortable>
         <template #body="{ data }">
               <div class="flex items-center gap-2">
                  <a :href="`#tracker/${data.secret}`" target="_blank">
                     {{ data.secret }}
                  </a>
               </div>
         </template>
      </Column>

      
      <Column field="keyword" header="Keyword" sortable ></Column>
      <Column field="email" header="Email" sortable></Column>
      <Column field="duration" header="Duration" sortable></Column>
      <Column field="is_expired" header="Expired" sortable></Column>
      <Column field="is_removed" header="Unsubscribed" sortable></Column>
   </DataTable>


</template>