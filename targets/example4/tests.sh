#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

BIN="bin/example3_cfi"

if [ ! -f "$BIN" ]; then
    echo "ERROR: hardened binary not found at $BIN"
    echo "Run the agent to produce a policy and apply the LLVM pass first."
    exit 1
fi

echo "Testing add"
out=$(./"$BIN" add)
echo "$out"
grep -q "op(10, 10) = 20" <<< "$out"

echo "Testing sub"
out=$(./"$BIN" sub)
echo "$out"
grep -q "op(10, 10) = 0" <<< "$out"

echo "Testing mul"
out=$(./"$BIN" mul)
echo "$out"
grep -q "op(10, 10) = 100" <<< "$out"

echo
echo "Normal tests passed!"