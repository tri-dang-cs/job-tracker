<script setup>

import { socket } from '../socket';

function connect() {
    socket.connect();
}

function disconnect() {
    socket.disconnect();
}


</script>

<template>
  <button @click="connect()">Connect</button>
  <button @click="disconnect()">Disconnect</button>
</template>