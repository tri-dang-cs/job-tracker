<script setup>

import { state, storedToken } from '../state';

import { ref } from 'vue';
import Panel from 'primevue/panel';
import axios from 'axios';


// get all email
const emails = ref([]);
axios.post('/emails', { token: storedToken.value })
    .then(response => {
        emails.value = response.data;
    });


</script>
<template>
    <h1>All emails sent</h1>

    <div v-for="email in emails">
        <span v-if="state.isAdmin">
            <Panel :header="`[User:${email.token}] ${email.date_created} - ${email.email}`">
                <span v-html="email.content"/>
            </Panel><br/>
        </span>
        <span v-else>
            <Panel :header="`${email.date_created} - ${email.email}`">
                <span v-html="email.content"/>
            </Panel><br/>
        </span>
    </div>

</template>