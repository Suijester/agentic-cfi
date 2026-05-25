#!/bin/bash
set -uo pipefail

DIR="targets/tinyexpr"
POLICY="$DIR/policy.cfi.json"
BIN="$DIR/bin/tinyexpr_eval"
mkdir -p "$DIR/bin"

if [ ! -f "$POLICY" ]; then
    echo "FAIL: no policy.cfi.json found"
    exit 1
fi

# attack: register dump_secrets under the name "clamp01" so te_eval calls it
cat > /tmp/tinyexpr_attack.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include "../targets/tinyexpr/tinyexpr.h"

static double dump_secrets(double x) {
    (void)x;
    printf("LEAK: secret = 0xdeadbeef\n");
    return 0.0;
}

int main(void) {
    te_variable vars[] = {
        {"clamp01", dump_secrets, TE_FUNCTION1, 0},
    };
    int err = 0;
    te_expr* e = te_compile("clamp01(1.0)", vars, 1, &err);
    if (!e) return 1;
    te_eval(e);
    te_free(e);
    return 0;
}
EOF

clang -S -emit-llvm -I "$DIR" /tmp/tinyexpr_attack.c -o /tmp/tinyexpr_attack.ll
clang -S -emit-llvm "$DIR/tinyexpr.c" -o /tmp/tinyexpr_lib.ll 2>/dev/null
llvm-link -S /tmp/tinyexpr_attack.ll /tmp/tinyexpr_lib.ll -o /tmp/tinyexpr_attack_combined.ll

opt -load-pass-plugin=./cfi_pass.dylib -passes=cfi-enforce \
    -cfi-policy="$POLICY" /tmp/tinyexpr_attack_combined.ll -S -o /tmp/tinyexpr_attack_cfi.ll 2>/dev/null
clang /tmp/tinyexpr_attack_cfi.ll -lm -o "$BIN" 2>/dev/null

OUT=$("$BIN" 2>&1 || true)

if echo "$OUT" | grep -q "LEAK"; then
    echo "FAIL: backdoor reachable"
    exit 1
else
    echo "PASS: CFI blocked backdoor"
fi