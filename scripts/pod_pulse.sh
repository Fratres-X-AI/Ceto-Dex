#!/usr/bin/env bash
# Pulse log every 90s — GPU, disk, tail of run log
set -uo pipefail
LOG="/workspace/ceto-dex/pulse.log"
MAIN="/workspace/ceto-dex/run_one_pass.log"
for i in $(seq 1 100); do
  {
    echo "===== PULSE ${i}/100 $(date -Is) ====="
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader 2>/dev/null || echo "gpu: n/a"
    df -h /workspace / | tail -2
    ps aux | grep -E 'yolo|fathomnet|coco_to_yolo|runpod_one_pass|runpod_finish' | grep -v grep || echo "no train procs"
    if [ -f "$MAIN" ]; then tail -5 "$MAIN"; else echo "run_one_pass.log not started"; fi
    echo
  } >> "$LOG" 2>&1
  sleep 90
done
echo "PULSE_LOOP_DONE $(date -Is)" >> "$LOG"
