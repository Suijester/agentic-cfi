#include <stdio.h>

void handle_get(const char* req) {
    puts("handled the GET request");
}

void handle_post(const char* req) {
    puts("handled the POST request");
}

void handle_put(const char* req) {
    puts("handled the PUT request");
}

void debug_dump(const char* req) {
    puts("DEBUG: control");
}
