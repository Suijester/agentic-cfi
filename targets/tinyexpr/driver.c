#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tinyexpr.h"

static double clamp01(double x) {
    if (x < 0.0) return 0.0;
    if (x > 1.0) return 1.0;
    return x;
}

static double square(double x) {
    return x * x;
}

static double dump(double x) {
    (void)x;
    printf("reached dump shell\n");
    return 0.0;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <expression>\n", argv[0]);
        return 1;
    }

    te_variable vars[] = {
        {"clamp01", clamp01, TE_FUNCTION1, 0},
        {"square", square, TE_FUNCTION1, 0},
    };

    int err = 0;
    te_expr* compiled = te_compile(argv[1], vars, sizeof(vars)/sizeof(vars[0]), &err);
    if (!compiled) {
        fprintf(stderr, "parse error at position %d in: %s\n", err, argv[1]);
        return 1;
    }

    double result = te_eval(compiled);
    printf("result = %g\n", result);
    te_free(compiled);
    return 0;
}