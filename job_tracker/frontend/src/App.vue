<script setup>

import { ref, shallowRef, computed, watch } from 'vue';

import { state, storedToken, loadJobs } from './state';

import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

import Menubar from 'primevue/menubar';
import Badge from 'primevue/badge';

import axios from 'axios';

import Toast from 'primevue/toast';
import { useToast } from "primevue/usetoast";
const toast = useToast();

import HomePage from './pages/Home.vue'
import NotificationsPage from './pages/Notifications.vue';
import StatusPage from './pages/Status.vue';
import Trackers from './pages/Trackers.vue';

//
const adminToken = 'admin-secret-token';
const currentToken = ref(storedToken.value);

// TODO: implement actual login logic
if (currentToken.value) {
    state.isLogin = true;
    if (currentToken.value == adminToken) {
        state.isAdmin = true;
    }
}

// 
const menuItemsBase = [
    {
        label: 'Home',
        icon: 'pi pi-home',
        href: '#home',
    }
];

const menuItemsLogin = menuItemsBase.concat([
    {
        label: 'Trackers',
        icon: 'pi pi-search',
        href: '#my-trackers',
    },
    {
        label: 'Notifications',
        icon: 'pi pi-bell', 
        href: '#notifications',
        badge: 999,
    }
]);

const menuItemsAdmin = menuItemsLogin.concat([
    {
        label: 'Service Status',
        icon: 'pi pi-desktop',
        href: '#status',
    },
    {
        label: 'Stats',
        icon: 'pi pi-cog',
        href: '#stats',
    },
]);


const menuItems = computed(() => {
    if (state.isAdmin) {
        return menuItemsAdmin;
    } else if (state.isLogin) {
        return menuItemsLogin;
    } else {
        return menuItemsBase;
    }
});


// routing

const currentView = shallowRef({
    component: HomePage,
    props: {},
});
const uniqueId = ref(0);

function processHash(hash) {
    const parts = hash.split('/'); 

    let props = {};
    let component = HomePage; 
    switch (parts[0]) {
        case '#login':
            if (parts.length == 2) {
                currentToken.value = decodeURIComponent(parts[1]);
                handleLogin();
            }
            break;
        case '#home':
            if (parts.length == 2) {
                props.keyword = decodeURIComponent(parts[1]);
            }
            props.isTracker = false;
            props.secret = '';
            component = HomePage;
            break;
        case '#tracker':
            if (parts.length == 2) {
                props.secret = decodeURIComponent(parts[1]);
            }
            props.isTracker = true;
            props.keyword = '';
            component = HomePage;
            break;
        case '#my-trackers':
            component = Trackers;
            break;
        case '#notifications':
            component = NotificationsPage;
            break;
        case '#status':
            component = StatusPage;
            break;
    }
    uniqueId.value++;
    currentView.value = { component, props };

}

window.addEventListener('hashchange', () => {
    processHash(window.location.hash);
});
processHash(window.location.hash);



// api setup
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
);

// load jobs
loadJobs(() => {
    toast.add({ severity: 'success', summary: 'Success', detail: 'Jobs loaded successfully', life: 3000 });
});


// button handlers
function handleSync() {
    state.isSyncing = true;
    setTimeout(() => {
        state.isSyncing = false;
        window.location.reload();
    }, 5000);

    axios.get('/sync')
        .then(response => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Sync request sent', life: 3000 });
        });
}

function generateToken() {
    const words = [
        "apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew",
        "ice", "jackfruit", "kiwi", "lemon", "mango", "nectarine", "orange", "papaya",
        "quince", "raspberry", "strawberry", "tangerine", "ugli", "vanilla", "watermelon",
        "xigua", "yellow", "zucchini", "apricot", "blackberry", "cantaloupe", "dragonfruit",
        "eggplant", "feijoa", "guava", "honeycrisp", "imbe", "jujube", "kumquat", "lime",
        "mulberry", "nashi", "olive", "pear", "quandong", "rambutan", "sapodilla", "tamarind"
    ];

    let token = "";

    // Generate two random words
    for (let i = 0; i < 2; i++) {
        const randomIndex = Math.floor(Math.random() * words.length);
        token += words[randomIndex] + "-";
    }

    // Generate a random number between 0 and 9
    const randomNumber = Math.floor(Math.random() * 10);
    token += randomNumber;

    return token;
}

function handleLogin() {
    // TODO: implement actual login logic
    if (!currentToken.value) {
        currentToken.value = generateToken();
    }
    state.isLogin = true;
    state.isAdmin = currentToken.value == adminToken;
    storedToken.value = currentToken.value;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Login successful', life: 3000 });
}

function handleAdmin() {
    currentToken.value = adminToken;
    handleLogin();
}

function handleLogout() {
    state.isLogin = false;
    state.isAdmin = false;
    currentToken.value = '';
    storedToken.value = '';
    toast.add({ severity: 'success', summary: 'Success', detail: 'Logout successful', life: 3000 });
}

function handleCopyToken() {
    const fullUrlWithoutHash = window.location.href.split('#')[0];
    const token = encodeURIComponent(currentToken.value);
    navigator.clipboard.writeText(`${fullUrlWithoutHash}#login/${token}`);
    toast.add({ severity: 'success', summary: 'Success', detail: 'Login link copied to clipboard', life: 3000 });
}

</script> 

<template>
    <Toast position="bottom-right" />
    <Menubar :model="menuItems">
        <template #start>
            <i v-if="state.isConnected" class="pi pi-circle-fill" style="color: lightgreen"></i>
            <i v-else class="pi pi-circle-fill" style="color: red"></i>
        </template>
        <template #item="{ item, props }">
            <a class="flex items-center" v-bind="props.action" :href="item.href">
                <span :class="item.icon" />
                <span class="ml-2">{{ item.label }}</span>
                <Badge v-if="item.badge" :value="item.badge" />
            </a>
        </template>

        <template #end>
            <span v-if="state.isLogin">
                <Button v-if="state.isSyncing" icon="pi pi-spin pi-sync" disabled label="Syncing"/>
                <Button v-else icon="pi pi-sync" label="Sync" @click="handleSync"/>

                <Button icon="pi pi-share-alt" @click="handleCopyToken" />
            </span>
            <Button v-else icon="pi pi-cog" label="Login as Admin" severity="help" @click="handleAdmin" />
            <InputText :disabled="state.isLogin" placeholder="Your secret token" type="text" style="margin-right: 8px" v-model="currentToken" />
            <Button v-if="state.isLogin" icon="pi pi-sign-out" label="Logout" @click="handleLogout" severity="warn" />
            <Button v-else icon="pi pi-sign-in" label="Login" @click="handleLogin" />
        </template>
    </Menubar>

    <component :is="currentView.component" v-bind="currentView.props" :key="uniqueId" />
</template>


<style>
    Button {
        margin-right: 8px;
    }
</style>
