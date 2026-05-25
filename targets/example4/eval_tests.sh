#!/bin/bash
set -uo pipefail

DIR="targets/example4"
SRC="$DIR/example4.c"
POLICY="$DIR/policy.cfi.json"
BIN="$DIR/bin/example4_eval"
mkdir -p "$DIR/bin"

if [ ! -f "$POLICY" ]; then
    echo "FAIL: no policy.cfi.json found"
    exit 1
fi

# pass debug as main argument
cat "$SRC" | sed 's/int main/int real_main/' > /tmp/example4_attack.c
cat >> /tmp/example4_attack.c << 'EOF'
int main(void) {
    return with_logging(debug, 10, 10);
}
EOF

clang -S -emit-llvm /tmp/example4_attack.c -o /tmp/example4_attack.ll 2>/dev/null
opt -load-pass-plugin=./cfi_pass.dylib -passes=cfi-enforce \
    -cfi-policy="$POLICY" /tmp/example4_attack.ll -S -o /tmp/example4_attack_cfi.ll 2>/dev/null
clang /tmp/example4_attack_cfi.ll -o "$BIN" 2>/dev/null

OUT=$("$BIN" 2>&1 || true)

if echo "$OUT" | grep -q "debug shell"; then
    echo "FAIL: backdoor reachable"
    exit 1
else
    echo "PASS: CFI blocked backdoor"
fi