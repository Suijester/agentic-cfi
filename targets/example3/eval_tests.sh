#!/bin/bash
set -uo pipefail

DIR="targets/example3"
POLICY="$DIR/policy.cfi.json"
BIN="$DIR/bin/example3_eval"
mkdir -p "$DIR/bin"

if [ ! -f "$POLICY" ]; then
    echo "FAIL: no policy.cfi.json found"
    exit 1
fi

# make routes struct table point to debug_dump, then call dispatch
cat > /tmp/example3_attack.c << 'EOF'
#include "handlers.c"
#include "dispatch.c"

int main(void) {
    routes[0].handler_function = debug_dump;  // backdoor swap
    dispatch("GET", "anything");
    return 0;
}
EOF

# compile with policy file and cfi pass
clang -S -emit-llvm -I "$DIR" /tmp/example3_attack.c -o /tmp/example3_attack.ll
opt -load-pass-plugin=./cfi_pass.dylib -passes=cfi-enforce \
    -cfi-policy="$POLICY" /tmp/example3_attack.ll -S -o /tmp/example3_attack_cfi.ll 2>/dev/null
clang /tmp/example3_attack_cfi.ll -o "$BIN" 2>/dev/null

OUT=$("$BIN" 2>&1 || true)

if echo "$OUT" | grep -q "DEBUG"; then
    echo "FAIL: backdoor is reachable"
    exit 1
else
    echo "PASS: CFI blocked backdoor"
fi