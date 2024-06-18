
import { ref, reactive, watch } from "vue";
import axios from 'axios';


export const state = reactive({
    isConnected: false,
    isSyncing: false,
    isLogin: false,
    isAdmin: false,
    jobs: [],
});

function usePersistentVariable(key, initialValue) {
    const variable = ref(initialValue);
    const item = localStorage.getItem(key);
    if (item) {
        try {
            variable.value = JSON.parse(item);
        } catch (e) {
            console.error(e);
        }
    }
    watch(variable, (newValue) => {
        localStorage.setItem(key, JSON.stringify(newValue));
    });

    return variable;
}

export const storedToken = usePersistentVariable('token', '');

const companyIcons = {
    'google': 'pi pi-google',
    'facebook': 'pi pi-facebook',
    'microsoft': 'pi pi-microsoft',
    'amazon': 'pi pi-amazon',
    'apple': 'pi pi-apple',
}

function convertJob(job) {
    const company = job.company.toLowerCase();
    if (company in companyIcons) {
        job.icon = companyIcons[company];
    } else {
        job.icon = 'pi pi-question';
    }
    return job;
}

export function loadJobs(callback) {
    axios.get('/jobs')
        .then(response => {
            state.jobs = response.data.map(convertJob);
            callback();
        });
}

