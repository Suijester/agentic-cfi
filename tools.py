from pathlib import Path
import subprocess

'''
Agent needs access to the following tools to properly evaluate CFI integrity in files:
Configuration:
- configure clang/LLVM toolchain (compiler path, version, flags)

Parsing & File Management:
- list C files in a directory
- parse and read C files
- write modified C files
- restore original C file and ensure functionality with git-based snapshotting
- apply structured diffs/patches to C files

IR Tools:
- compile multiple C files to LLVM IR
- compile C files to binaries
- extract function type signatures from LLVM IR for type-based target set matching
- construct partial static call graph from IR
- read LLVM files and parse indirect function calls (forward-edge CFI)
- map IR lines to C source code lines

Static Analysis Tools:
- find function pointer declarations
- find function pointer assignments
- find indirect call sites in source (works with mapping IR lines to C source code lines)
- infer target sets for indirect call sites via type-signature matching and call graph reading
- create CFI policy file (.cfi) mapping each indirect call site to its target set of functions
- validate .cfi policy (check target functions exist and signatures match call sites)

Dynamic Analysis Tools:
- run normal tests on directories
- run visible toy hijacking examples for validation on some directories, to identify which CFI policies work
- compare before and after CFI check behavior

CFI Solution Tools:
- instrument C source files with CFI checks based on .cfi policy file
- compile and validate instrumented files pass normal and toy hijacking tests for validation

Report Methodology Tools:
- log each agent step and result of tools
- save all interaction transcripts
- write final findings report, containing solutions, CFI limitations / issues that can't be solved by forward edge CFI, etc.
    - some issues may not be solvable with only CFI checks (e.g. need shadow stacks), which agent must identify :)
'''

def list_c_files(folder: str) -> list[str]:
    return [str(file) for file in Path(folder).glob("*.c") if file.is_file()]

def read_c_file(file: str, max_chars: int = 15000) -> str:
    text = Path(file).read_text(errors = "ignore")
    return text[:max_chars]

def compile_to_llvm(c_file: str, out_dir: str = "outputs") -> dict:
    out = Path(out_dir)
    out.mkdir(exist_ok = True)

    ll_file = out / (Path(c_file).stem + ".ll")

    # command for compilation
    compile_command = [
        "clang",
        "-O0",
        "-g",
        "-S",
        "-emit-llvm",
        c_file,
        "-o",
        str(ll_file)
    ]

    result = subprocess.run(compile_command, capture_output = True, text = True)
    return {
        "ok": result.returncode == 0,
        "cmd": " ".join(compile_command),
        "ll_file": str(ll_file),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

def compile_to_binary(c_file: str, out_dir: str = "outputs") -> dict:
    out = Path(out_dir)
    out.mkdir(exist_ok = True)

    bin_file = out / (Path(c_file).stem)
    return {}



def main():
    list_c_files("targets/example1")
    read_c_file("targets/example1/main.c")
    compile_to_llvm("targets/example1/main.c")

if __name__ == "__main__":
    main()