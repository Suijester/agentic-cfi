#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

BIN="bin/example2_cfi"

if [ ! -f "$BIN" ]; then
    echo "ERROR: hardened binary not found at $BIN"
    echo "Run the agent to produce a policy and apply the LLVM pass first."
    exit 1
fi

echo "Testing http route."
out=$(./"$BIN" http)
echo "$out"
grep -q "HTTP: connected" <<< "$out"
grep -q "HTTP: closed" <<< "$out"

echo "Testing admin route."
out=$(./"$BIN" admin)
echo "$out"
grep -q "ADMIN: connected" <<< "$out"
grep -q "ADMIN: closed" <<< "$out"

echo
echo "Normal tests passed!"