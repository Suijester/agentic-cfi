#!/bin/bash
set -uo pipefail

DIR="targets/example2"
SRC="$DIR/example2.c"
POLICY="$DIR/policy.cfi.json"
BIN="$DIR/bin/example2_eval"
mkdir -p "$DIR/bin"

if [ ! -f "$POLICY" ]; then
    echo "FAIL: no policy.cfi.json found"
    exit 1
fi

# Create attack: reassign on_connect to maintenance_task
cat "$SRC" | sed 's/int main/int real_main/' > /tmp/example2_patched.c
cat >> /tmp/example2_patched.c << 'EOF'
int main(void) {
    protocol_handler_t proto = make_protocol("http");
    proto.on_connect = maintenance_task;
    proto.on_connect();
    return 0;
}
EOF

# Compile through the CFI pass
clang -S -emit-llvm /tmp/example2_patched.c -o /tmp/example2_patched.ll 2>/dev/null
opt -load-pass-plugin=./cfi_pass.dylib -passes=cfi-enforce \
    -cfi-policy="$POLICY" /tmp/example2_patched.ll -S -o /tmp/example2_patched_cfi.ll 2>/dev/null
clang /tmp/example2_patched_cfi.ll -o "$BIN" 2>/dev/null

OUT=$("$BIN" 2>&1 || true)

if echo "$OUT" | grep -q "maintenance"; then
    echo "FAIL: backdoor is reachable"
    exit 1
else
    echo "PASS: CFI blocked backdoor"
fi