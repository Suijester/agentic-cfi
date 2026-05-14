#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p build

echo "Building program."
clang -O0 -g -Wall -Wextra main.c -o build/example1

echo "Testing safe route."
out=$(./build/example1 safe)
echo "$out"
grep -q "SAFE: safe_handler reached." <<< "$out"

echo "Testing admin route."
out=$(./build/example1 admin)
echo "$out"
grep -q "ADMIN: admin_handler reached." <<< "$out"

echo "Testing hijacking route."
out=$(./build/example1 attack)
echo "$out"
grep -q "UNSAFE: debug_shell reached." <<< "$out"

echo
echo "Normal tests passed!"