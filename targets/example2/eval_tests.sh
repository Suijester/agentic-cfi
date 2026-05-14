#!/bin/bash
set -uo pipefail

SRC="targets/example2/example2.c"
BIN="targets/example2/bin/example2_eval"
mkdir -p targets/example2/bin

# compile program with new attack
cat "$SRC" | sed 's/int main/int real_main/' > /tmp/example2_patched.c
cat >> /tmp/example2_patched.c << 'EOF'
int main(void) {
    protocol_handler_t proto = make_protocol("http");
    proto.on_connect = maintenance_task;
    proto.on_connect();
    return 0;
}
EOF

clang -O0 /tmp/example2_patched.c -o "$BIN" 2>/dev/null

OUT=$("$BIN" 2>&1)

if echo "$OUT" | grep -q "maintenace"; then
    echo "FAIL: backdoor is reachable"
    exit 1
else
    echo "PASS: CFI blocked backdoor"
fi