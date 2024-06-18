<script setup>

const props = defineProps(['keyword', 'isTracker', 'secret']);

import { state, storedToken } from '../state';

import { ref } from 'vue';
import Button from 'primevue/button';
import Panel from 'primevue/panel';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from '@primevue/core/api';

import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';
import InputNumber from 'primevue/inputnumber';
import axios from 'axios';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

import { useToast } from "primevue/usetoast";
const toast = useToast();


// reactive things
const filters = ref({ global: { value: null, matchMode: FilterMatchMode.CONTAINS } });
const form = ref({});
const newIDs = ref([]);
const pageName = props.isTracker ? `Tracker - ${props.secret}` : 'Home';
const pageNameSuffix = ref('');
const isTracking = ref(false);
const isError = ref(false);


// get companies data
const companyLinks = ref({});
axios.get('/company-links')
    .then(response => {
        companyLinks.value = response.data;
});


// load tracker data if it is a tracker
if (props.isTracker) {
    axios.get(`/tracker/${props.secret}`)
        .then(response => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Tracker loaded successfully', life: 3000 });
            form.value.email = response.data.email;
            form.value.duration = response.data.duration;
            filters.value.global.value = response.data.keyword;
            if (response.data.new_ids) {
                // split and parseInt it
                newIDs.value = response.data.new_ids.split(',').map(id => parseInt(id));
            }
            if (response.data.is_removed) {
                pageNameSuffix.value = '(unsubscribed)';
            } else if (response.data.is_expired) {
                pageNameSuffix.value = '(expired)';
            } else {
                isTracking.value = true;
            }
        }, error => {
            pageNameSuffix.value = `(Error ${error.response.status})`;
            isError.value = true;
        });
} else {
    filters.value.global.value = props.keyword;
}


function rowStyle(job) {
    if (newIDs.value.includes(job.id)) {
        return { 'background-color': '#f0f0f0' };
    }
}


// button handlers
function handleSubscribe() {
    const keyword = filters.value.global.value;
    const email = form.value.email;
    const duration = parseInt(form.value.duration);

    if (!keyword) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Keyword is required', life: 3000 });
        return;
    }

    if (!email) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Email is required', life: 3000 });
        return;
    }
    
    if (duration <= 0) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Duration must be greater than 0', life: 3000 });
        return;
    }
   
    axios.post('/tracker', { 
            token: storedToken.value,
            keyword: keyword,
            email: email,
            duration: duration,
        })
        .then((response) => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Subscribed', life: 3000 });
            const secret = response.data.secret;
            // window.open(`#tracker/${secret}`, '_blank')
            window.location.hash = `#tracker/${secret}`;
        });
};

function handleUnsubscribe() {
    axios.delete(`/tracker/${props.secret}`)
        .then(() => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Unsubscribed', life: 3000 });
            window.location.reload();
        });
};

function handleCopyLink() {
    let keyword = filters.value.global.value;
    if (!keyword) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Keyword is required', life: 3000 });
        return;
    }

    const fullUrlWithoutHash = window.location.href.split('#')[0];
    keyword = encodeURIComponent(keyword);
    navigator.clipboard.writeText(`${fullUrlWithoutHash}#home/${keyword}`);
    toast.add({ severity: 'success', summary: 'Success', detail: 'Link copied to clipboard', life: 3000 });
}


</script>

<template>
    <h1>{{ pageName }} {{ pageNameSuffix }}</h1>

    <Panel header="Search box">
        <InputGroup>
            <InputGroupAddon><i class="pi pi-search"></i></InputGroupAddon>
            <InputText placeholder="Keyword" :disabled="props.isTracker" v-model="filters['global'].value" />
            <Button v-if="!props.isTracker" icon="pi pi-clipboard" label="Copy link" @click="handleCopyLink" />
        </InputGroup><br/>

        <InputGroup v-if="state.isLogin">
            <InputGroupAddon><i class="pi pi-envelope"></i></InputGroupAddon>
            <InputText v-model="form.email" :disabled="props.isTracker" placeholder="Email to subscribe"/>
            <InputGroupAddon><i class="pi pi-clock"></i></InputGroupAddon>
            <InputNumber suffix=" sec" v-model="form.duration" :disabled="props.isTracker" placeholder="0 (for a time window in seconds)"/>
            <Button v-if="!props.isTracker" icon="pi pi-bell" label="Subscribe" @click="handleSubscribe" />
            <span v-else-if="!isError">
                <Button v-if="isTracking" icon="pi pi-bell-slash" label="UnSubscribe" severity="danger" @click="handleUnsubscribe" />
                <Button v-else label="ReSubscribe" icon="pi pi-bell" severity="info" @click="handleSubscribe" />
            </span>
        </InputGroup><br/>
    </Panel><br/>

    <DataTable :value="state.jobs" 
        :rowStyle="rowStyle" showGridlines tableStyle="min-width: 50rem"
        resizableColumns columnResizeMode="fit"
        sortField="date_posted" :sortOrder="-1" 
        v-model:filters="filters" :globalFilterFields="['company', 'title', 'description', 'location']"
    >
        <Column style="width: 0">
            <template #body="{ data }">
                <div class="flex items-center gap-2">
                    <span :class="data.icon" />
                </div>
            </template>
        </Column>
        <Column field="company" header="Company" sortable>
            <template #body="{ data }">
                <div class="flex items-center gap-2">
                    <a :href="companyLinks[data.company]" target="_blank">
                        {{ data.company }}
                    </a>
                </div>
            </template>
        </Column>
        <Column field="title" header="Title" sortable>
            <template #body="{ data }">
                <div class="flex items-center gap-2">
                    <a :href="data.link" target="_blank">{{ data.title }}</a>
                </div>
            </template>
        </Column>
        <Column field="description" header="Description" sortable ></Column>
        <Column field="location" header="Location" sortable></Column>
        <Column field="date_posted" header="Date" sortable></Column>
    </DataTable>

</template>
