#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

BIN="bin/tinyexpr_cfi"

if [ ! -f "$BIN" ]; then
    echo "ERROR: hardened binary not found at $BIN"
    echo "Run the agent first."
    exit 1
fi

echo "Testing arithmetic."
out=$(./"$BIN" "2 + 3 * 4")
echo "$out"
grep -q "result = 14" <<< "$out"

echo "Testing built-in functions."
out=$(./"$BIN" "sqrt(16) + sin(0)")
echo "$out"
grep -q "result = 4" <<< "$out"

echo "Testing custom whitelisted function."
out=$(./"$BIN" "clamp01(1.5)")
echo "$out"
grep -q "result = 1" <<< "$out"

out=$(./"$BIN" "square(7)")
echo "$out"
grep -q "result = 49" <<< "$out"

echo
echo "Normal tests passed!"