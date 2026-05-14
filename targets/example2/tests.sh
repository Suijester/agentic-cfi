#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p build

echo "Building program."
clang -O0 -g -Wall -Wextra example2.c -o build/example2

echo "Testing http route."
out=$(./build/example2 http)
echo "$out"
grep -q "HTTP: connected" <<< "$out"
grep -q "HTTP: closed" <<< "$out"

echo "Testing admin route."
out=$(./build/example2 admin)
echo "$out"
grep -q "ADMIN: connected" <<< "$out"
grep -q "ADMIN: closed" <<< "$out"

echo
echo "Normal tests passed!"