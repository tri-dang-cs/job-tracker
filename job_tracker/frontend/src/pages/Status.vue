<script setup>

import axios from 'axios';
import { ref } from 'vue';

const rqDashboardURL = ref('http://127.0.0.1:9181');

axios.get('/rq-dashboard')
    .then(response => {
        rqDashboardURL.value = response.data;
    });

</script>

<template>
    <h1>Status</h1>
    <iframe :src="rqDashboardURL" style="width: 100%; height: 100vh; border: none;"></iframe>
</template>