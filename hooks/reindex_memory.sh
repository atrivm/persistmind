#!/usr/bin/env bash
# No-op kept for sessions opened before 0.6.0: their hook list still runs this
# script after each Write/Edit and at session start. basic-memory is gone, so
# there is nothing to reindex. Remove once no session older than 0.6.0 runs.
cat >/dev/null 2>&1
exit 0
