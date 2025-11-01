#!/usr/bin/env bash
# USAGE: ./run_pipeline.sh /path/to/access.log
LOG=${1:-tests/sample_access.log}
source .venv/bin/activate
python3 -u src/tui.py --logfile "$LOG" --window 60 --poll 1
