from pathlib import Path
import subprocess
import json

# region
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
# endregion

def configure_toolchain() -> dict:
    commands = [
        ["clang", "--version"]
    ]

    results = []
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output = True, text = True)
            results.append({
                "cmd": " ".join(cmd),
                "ok": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            })
        except FileNotFoundError as err:
            results.append({
                "cmd": " ".join(cmd),
                "ok": False,
                "stdout": "",
                "stderr": f"command probably not found from configure_toolchain, {err}",
            })
    
    return {
        "ok": all(result["ok"] for result in results),
        "results": results,
    }

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
    
    # standard compilation command
    compile_command = [
        "clang",
        "-O0",
        "-g",
        "-Wall",
        "-Wextra",
        c_file,
        "-o",
        str(bin_file)
    ]

    result = subprocess.run(compile_command, capture_output = True, text = True)
    return {
        "ok": result.returncode == 0,
        "cmd": " ".join(compile_command),
        "bin_file": str(bin_file),
        "stdout": result.stdout,
        "stderr": result.stderr
    }

def find_indirect_calls(ll_file: str) -> list[str]:
    text = Path(ll_file).read_text(errors = "ignore")
    indirect_calls = []

    for i, line in enumerate(text.splitlines(), start = 1):
        line = line.strip()

        if " call " in line or line.startswith("call "):
            call_type = line.split("call", 1)[1].split("(", 1)[0]
            if "@" not in call_type:
                indirect_calls.append(f"{ll_file}:{i}: {line}")

        elif " invoke " in line or line.startswith("invoke "):
            invoke_type = line.split("invoke", 1)[1].split("(", 1)[0]
            if "@" not in invoke_type:
                indirect_calls.append(f"{ll_file}:{i}: {line}")
    
    return indirect_calls

def dump_clang_ast(c_file: str) -> dict:
    ast_command = [
        "clang",
        "-Xclang",
        "-ast-dump=json",
        "-fsyntax-only",
        c_file
    ]

    result = subprocess.run(ast_command, capture_output = True, text = True)
    if (result.returncode != 0):
        return {
            "ok": False,
            "cmd": " ".join(ast_command),
            "ast": None,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    
    try:
        ast = json.loads(result.stdout)
    except json.JSONDecodeError as err:
        return {
            "ok": False,
            "cmd": " ".join(ast_command),
            "ast": None,
            "stdout": "",
            "stderr": f"couldn't parse AST, {err}",
        }
    
    return {
        "ok": True,
        "cmd": " ".join(ast_command),
        "ast": ast,
        "stdout": "",
        "stderr": result.stderr,
    }

def walk_clang_ast(node: dict):
    if node is None:
        return

    stack = [(node, "")]
    while (stack):
        current_node, current_file = stack.pop()
        location = current_node.get("loc", {})
        if "file" in location:
            current_file = location["file"]

        # generator funct so we can parse all nodes in AST order
        yield current_node, current_file 

        children = current_node.get("inner", [])
        for child in reversed(children):
            stack.append((child, current_file))

def find_function_declarations(c_file: str) -> list[str]:
    result = dump_clang_ast(c_file)

    if (result.get("ok") == False):
        return [f"ERROR: failed to dump clang ast; {result.get('stderr')}"]

    ast = result.get("ast")
    functions = []

    # only use the file name (strip path)
    target_file = Path(c_file).name

    for node, file_path in walk_clang_ast(ast):
        if node.get("kind") == "FunctionDecl" and node.get("name") is not None:
            if target_file == Path(file_path).name:
                children = node.get("inner", [])
                has_body = any(child.get("kind") == "CompoundStmt" for child in children)

                if (has_body):
                    functions.append(node.get("name"))

    return functions


def find_function_pointer_declarations():
    return

def find_pointer_assignments(c_file: str) -> list[str]:
    return



def infer_target_sets():
    return

def instrument_CFI_checks():
    return

def run_tests(folder: str) -> dict:
    scripts = Path(folder) / "tests.sh"

    if not scripts.exists():
        return {
            "ok": False,
            "stdout": "",
            "stderr": "No tests.sh file found",
        }
    
    results = subprocess.run(
        ["bash", "tests.sh"],
        cwd = folder,
        capture_output = True,
        text = True,
    )

    return {
        "ok": results.returncode == 0,
        "stdout": results.stdout,
        "stderr": results.stderr,
    }

def log_steps():
    return

'''
def main():
    list_c_files("targets/example1")
    read_c_file("targets/example1/main.c")
    compile_to_llvm("targets/example1/main.c")

if __name__ == "__main__":
    main()
'''