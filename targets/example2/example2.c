#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    void (*on_connect)(void);
    void (*on_close)(void);
} protocol_handler_t;

void http_connect() {
    puts("HTTP: connected");
}

void http_close() {
    puts("HTTP: closed");
}

void admin_connect() {
    puts("ADMIN: connected");
}

void admin_close() {
    puts("ADMIN: closed");
}

void maintenance_task() {
    puts("Nothing to see here... routine maintenance task!");
}

protocol_handler_t make_protocol(const char* name) {
    if (strcmp(name, "http") == 0) {
        return (protocol_handler_t){http_connect, http_close};
    } else if (strcmp(name, "admin") == 0) {
        return (protocol_handler_t){admin_connect, admin_close};
    }
    return (protocol_handler_t){http_connect, http_close};
}

int main(int argc, char** argv) {
    const char* mode = (argc > 1) ? argv[1] : "http";
    protocol_handler_t proto = make_protocol(mode);

    proto.on_connect();
    proto.on_close();
    
    return 0;
}