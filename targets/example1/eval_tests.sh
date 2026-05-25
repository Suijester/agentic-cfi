#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

BIN="bin/example1_cfi"

if [ ! -f "$BIN" ]; then
    echo "ERROR: hardened binary not found at $BIN"
    echo "Run the agent to produce a policy and apply the LLVM pass first."
    exit 1
fi

echo "Testing safe route."
out=$(./"$BIN" safe)
echo "$out"
grep -q "SAFE: safe_handler reached." <<< "$out"

echo "Testing admin route."
out=$(./"$BIN" admin)
echo "$out"
grep -q "ADMIN: admin_handler reached." <<< "$out"

if out=$(./"$BIN" attack 2>&1); then
    echo "FAIL: attack should have been blocked"
    exit 1
fi
echo "$out"
echo "Attack was blocked as expected."

echo
echo "Normal tests passed!"