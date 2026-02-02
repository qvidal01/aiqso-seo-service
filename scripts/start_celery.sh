#!/bin/bash
# Start Celery workers and beat scheduler for AIQSO SEO Service
#
# Usage:
#   ./scripts/start_celery.sh worker    - Start worker only
#   ./scripts/start_celery.sh beat      - Start beat scheduler only
#   ./scripts/start_celery.sh all       - Start both (default)
#   ./scripts/start_celery.sh stop      - Stop all Celery processes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/pids"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$PID_DIR"

# Activate virtual environment if it exists
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

cd "$PROJECT_DIR"

start_worker() {
    echo "Starting Celery worker..."
    celery -A app.celery_app worker \
        --loglevel=info \
        --concurrency=2 \
        --pidfile="$PID_DIR/celery-worker.pid" \
        --logfile="$LOG_DIR/celery-worker.log" \
        --detach

    echo "Celery worker started. PID: $(cat $PID_DIR/celery-worker.pid)"
}

start_beat() {
    echo "Starting Celery beat scheduler..."
    celery -A app.celery_app beat \
        --loglevel=info \
        --pidfile="$PID_DIR/celery-beat.pid" \
        --logfile="$LOG_DIR/celery-beat.log" \
        --detach

    echo "Celery beat started. PID: $(cat $PID_DIR/celery-beat.pid)"
}

stop_all() {
    echo "Stopping Celery processes..."

    if [ -f "$PID_DIR/celery-worker.pid" ]; then
        kill $(cat "$PID_DIR/celery-worker.pid") 2>/dev/null || true
        rm -f "$PID_DIR/celery-worker.pid"
        echo "Worker stopped"
    fi

    if [ -f "$PID_DIR/celery-beat.pid" ]; then
        kill $(cat "$PID_DIR/celery-beat.pid") 2>/dev/null || true
        rm -f "$PID_DIR/celery-beat.pid"
        echo "Beat stopped"
    fi

    echo "All Celery processes stopped"
}

status() {
    echo "Celery Status:"
    echo "=============="

    if [ -f "$PID_DIR/celery-worker.pid" ]; then
        PID=$(cat "$PID_DIR/celery-worker.pid")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Worker: Running (PID: $PID)"
        else
            echo "Worker: Stopped (stale PID file)"
        fi
    else
        echo "Worker: Stopped"
    fi

    if [ -f "$PID_DIR/celery-beat.pid" ]; then
        PID=$(cat "$PID_DIR/celery-beat.pid")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Beat: Running (PID: $PID)"
        else
            echo "Beat: Stopped (stale PID file)"
        fi
    else
        echo "Beat: Stopped"
    fi
}

case "${1:-all}" in
    worker)
        start_worker
        ;;
    beat)
        start_beat
        ;;
    all)
        start_worker
        start_beat
        ;;
    stop)
        stop_all
        ;;
    status)
        status
        ;;
    restart)
        stop_all
        sleep 2
        start_worker
        start_beat
        ;;
    *)
        echo "Usage: $0 {worker|beat|all|stop|status|restart}"
        exit 1
        ;;
esac
