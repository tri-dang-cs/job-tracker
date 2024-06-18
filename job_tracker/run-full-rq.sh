#!/bin/sh

cd $(dirname $0)

NO_WORKERS=2
if [ ! -z "$1" ]; then
    NO_WORKERS=$1
fi

echo "[+] Starting $NO_WORKERS workers"
for i in $(seq 1 $NO_WORKERS); do
    ./run-worker.sh &
    pid=$!
    # save to global variable
    WORKER_PIDS="$WORKER_PIDS $pid" 
done

echo "[+] Staring service"
./run-service.sh &
SERVICE_PID=$!

echo "[+] Starting dashboard"
rq-dashboard

echo "[+] Killing service"
kill $SERVICE_PID

echo "[+] Killing workers"
for pid in $WORKER_PIDS; do
    kill $pid
done

