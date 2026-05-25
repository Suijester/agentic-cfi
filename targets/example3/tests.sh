#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

BIN="bin/example3_cfi"

if [ ! -f "$BIN" ]; then
    echo "ERROR: hardened binary not found at $BIN"
    echo "Run the agent to produce a policy and apply the LLVM pass first."
    exit 1
fi

echo "Testing GET route."
out=$(./"$BIN" GET /index)
echo "$out"
grep -q "handled the GET request" <<< "$out"

echo "Testing POST route."
out=$(./"$BIN" POST /submit)
echo "$out"
grep -q "handled the POST request" <<< "$out"

echo "Testing PUT route."
out=$(./"$BIN" PUT /update)
echo "$out"
grep -q "handled the PUT request" <<< "$out"

echo
echo "Normal tests passed!"