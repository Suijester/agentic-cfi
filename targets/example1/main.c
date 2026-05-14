#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void (*handler_t)(void);

void safe_handler(void) {
    puts("SAFE: safe_handler reached.");
}

void admin_handler(void) {
    puts("ADMIN: admin_handler reached.");
}

void debug_shell(void) {
    puts("UNSAFE: debug_shell reached.");
}

static handler_t handler = NULL;

void set_handler_from_mode(const char* mode) {
    if (strcmp(mode, "safe") == 0) {
        handler = safe_handler;
    } else if (strcmp(mode, "admin") == 0) {
        handler = admin_handler;
    } else {
        handler = safe_handler;
    }
}

// sim a memory vulnerability that lets us overwrite function pointer to point to smth else :)
void sim_hijack(void) {
    puts("SIMULATED HIJACK: overwrote handler");
    handler = debug_shell;
}

void dispatch(void) {
    if (handler == NULL) {
        puts("ERR: handler is NULL");
        exit(1);
    }

    handler();
}

int main(int argc, char** argv) {
    const char* mode = (argc > 1) ? argv[1] : "safe";

    if (strcmp(mode, "safe") == 0 || strcmp(mode, "admin") == 0) {
        set_handler_from_mode(mode);
    } else if (strcmp(mode, "attack") == 0) {
        set_handler_from_mode("safe");
        sim_hijack();
    } else {
        printf("Usage: %s [safe | attack | admin]\n", argv[0]);
        exit(1);
    }
    
    dispatch();
    return 0;
}