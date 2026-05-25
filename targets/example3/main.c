void dispatch(const char* method, const char* req);

int main(int argc, char** argv) {
    dispatch(argv[1], argv[2]);
    return 0;
}