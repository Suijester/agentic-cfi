#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p build

echo "Building program."
clang -O0 -g -Wall -Wextra example1.c -o build/example1

echo "Testing safe route."
out=$(./build/example1 safe)
echo "$out"
grep -q "SAFE: safe_handler reached." <<< "$out"

echo "Testing admin route."
out=$(./build/example1 admin)
echo "$out"
grep -q "ADMIN: admin_handler reached." <<< "$out"

if out=$(./build/example1 attack 2>&1); then
    echo "FAIL: attack should have been blocked"
    exit 1
fi
echo "$out"
echo "Attack was blocked as expected."

echo
echo "Normal tests passed!"