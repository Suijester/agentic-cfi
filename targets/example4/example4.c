#include <stdio.h>
#include <string.h>

typedef int (*op_t)(int, int);

int add(int a, int b) {
    return a + b;
}

int mul(int a, int b) {
    return a * b;
}

int sub(int a, int b) {
    return a - b;
}

int debug(int a, int b) {
    printf("debug shell accessed\n");
}

int with_logging(op_t op, int a, int b) {
    int result = op(a, b);
    printf("op(%d, %d) = %d\n", a, b, result);
    return result;
}

int main(int argc, char** argv) {
    const char* mode = (argc > 1) ? argv[1] : "add";
    int a = 10;
    int b = 10;

    if (strcmp(mode, "add") == 0) return with_logging(add, a, b);
    if (strcmp(mode, "sub") == 0) return with_logging(sub, a, b);
    if (strcmp(mode, "mul") == 0) return with_logging(mul, a, b);

    puts("unknown operation");
    return 1;
}