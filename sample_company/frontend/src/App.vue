<script setup>

import { ref } from 'vue';
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Panel from 'primevue/panel';
import InputText from 'primevue/inputtext';

import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';


import axios from 'axios';

import Toast from 'primevue/toast';
import { useToast } from "primevue/usetoast";
const toast = useToast();

const company_name = import.meta.env.VITE_COMPANY_NAME || 'Sample Company';

axios.defaults.baseURL = import.meta.env.VITE_API_URL || '/api';
axios.interceptors.response.use(
    (response) => response.data,
    (error) => {
        // Check for specific error types or statuses
        if (error.response) {
            // if service reponse in format
            if (error.response.data.message) {
                toast.add({ severity: 'error', summary: error.response.data.error, detail: error.response.data.message, life: 3000 });
            } else {
                toast.add({ severity: 'error', summary: 'Error', detail: error.response.data, life: 3000 });
            }
        } else if (error.request) {
            toast.add({ severity: 'error', summary: 'Error', detail: 'No response received', life: 3000 });
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: error.message, life: 3000 });
        }

        // Optionally, return a custom error object or throw the error
        return Promise.reject(error);
    }
)

// Define reactive form data
const form = ref({
    title: '',
    description: '',
    location: ''
});

// load jobs
const jobs = ref([]); 
axios.get('/jobs')
    .then(response => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Jobs loaded successfully', life: 3000 });
        jobs.value = response.data;
    });

// get job id from url parameter + rowStyle
const urlParams = new URLSearchParams(window.location.search);
const jobId = parseInt(urlParams.get('id'));

function rowStyle(job) {
    if (jobId && job.id === jobId) {
        return { 'background-color': '#ABEBC6' };
    }
}


// button handlers

function addRandomJob() {
    axios.post('/jobs/random')
        .then(response => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Random job added successfully', life: 3000 });
            // insert to the beginning of the array
            jobs.value.unshift(response.data);
        });
}

function removeRandomJob() {
    axios.delete(`/jobs/random`)
        .then(response => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Random job removed successfully', life: 3000 });
            // remove jobs with the same id
            jobs.value.splice(jobs.value.findIndex(job => job.id === response.data.id), 1);
        });
}

function removeJob(job) {
    axios.delete(`/jobs/${job.id}`)
        .then(response => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Job removed successfully', life: 3000 });
            // remove jobs with the same id
            jobs.value.splice(jobs.value.findIndex(j => j.id === job.id), 1);
        });
}

const handleSubmit = () => {
    axios.post('/jobs', form.value)
        .then(response => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Job added successfully', life: 3000 });
            // insert to the beginning of the array
            jobs.value.unshift(response.data);
            // reset form
            form.value.title = form.value.desc = form.value.loc = '';
        });

};

</script>

<template>
    <Toast />
    <h1>{{ company_name }} Career Page</h1>

    <Toolbar>
        <template #start>
            <Button @click="addRandomJob" icon="pi pi-plus" style="margin-right: 8px" label="Add random job" />
            <Button @click="removeRandomJob" icon="pi pi-times" class="p-button-danger" label="Remove random job" />
        </template>
    </Toolbar><br/>

    <Panel header="Add new job">
        <form @submit.prevent="handleSubmit">
            <InputGroup>
                <InputGroupAddon><i class="pi pi-id-card"></i></InputGroupAddon>
                <InputText placeholder="Title" v-model="form.title" />
            </InputGroup><br/>
            <InputGroup>
                <InputGroupAddon><i class="pi pi-file"></i></InputGroupAddon>
                <InputText placeholder="Description" v-model="form.description" />
            </InputGroup><br/>
            <InputGroup>
                <InputGroupAddon><i class="pi pi-map-marker"></i></InputGroupAddon>
                <InputText placeholder="Location" v-model="form.location" />
            </InputGroup><br/>
            <Button label="Submit" type="submit" />
        </form>
    </Panel><br/>

    <DataTable :value="jobs" 
        :rowStyle="rowStyle" showGridlines tableStyle="min-width: 50rem"
        resizableColumns columnResizeMode="fit"
        sortField="date_posted" :sortOrder="-1" 
    >
        <Column field="id" header="ID" style="width: 0" sortable />
        <Column field="title" header="Title" sortable />
        <Column field="description" header="Description" sortable />
        <Column field="location" header="Location" sortable />
        <Column field="date_posted" header="Date" sortable />
        <Column style="width: 0">
            <template #body="{ data }">
                <Button icon="pi pi-trash" severity="danger" @click="removeJob(data)"/>
            </template>
        </Column>
                
    </DataTable>

</template>
