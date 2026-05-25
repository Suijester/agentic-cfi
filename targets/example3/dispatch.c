#include <string.h>
#include <stdio.h>

typedef void (*handler)(const char*);

// forward decls
void handle_get(const char*);
void handle_post(const char*);
void handle_put(const char*);
void debug_dump(const char*);

typedef struct {
    const char* method;
    handler handler_function;
} router_t;

static router_t routes[] = {
    {"GET", handle_get},
    {"POST", handle_post},
    {"PUT", handle_put},
};

void dispatch(const char* method, const char* req) {
    for (int i = 0; i < 3; i++) {
        if (strcmp(routes[i].method, method) == 0) {
            routes[i].handler_function(req);
            return;
        }
    }
    puts("error: 404!");
}