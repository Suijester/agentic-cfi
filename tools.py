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

def read_file(file: str, max_chars: int = 15000) -> str:
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

def find_indirect_calls(ll_file: str) -> list[dict]:
    text = Path(ll_file).read_text(errors = "ignore")
    indirect_calls = []

    current_function = None
    call_index = 0

    for i, line in enumerate(text.splitlines(), start = 1):
        line = line.strip()

        # entering function
        if line.startswith("define ") and "@" in line:
            at_pos = line.index("@")
            paren_pos = line.find("(", at_pos)

            if (paren_pos != -1):
                current_function = line[at_pos + 1 : paren_pos]
                call_index = 0
            continue

        # leaving function
        if current_function is not None and line == "}":
            current_function = None
            continue

        if current_function is None:
            continue

        if " call " in line or line.startswith("call "):
            call_type = line.split("call", 1)[1]
            if "@" not in call_type[:call_type.rfind("(")]:
                indirect_calls.append({
                    "caller": current_function,
                    "call_index": call_index,
                    "ir_snippet": line,
                    "location": f"{ll_file}:{i}",
                })
                call_index += 1

        elif " invoke " in line or line.startswith("invoke "):
            invoke_type = line.split("invoke", 1)[1]
            if "@" not in invoke_type[:invoke_type.rfind("(")]:
                indirect_calls.append({
                    "caller": current_function,
                    "call_index": call_index,
                    "ir_snippet": line,
                    "location": f"{ll_file}:{i}",
                })
                call_index += 1
    
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

    stack = [node]
    current_file = ""
    while stack:
        current_node = stack.pop()
        location = current_node.get("loc", {})
        if "file" in location:
            current_file = location["file"]

        # generator funct so we can parse all nodes in AST order
        yield current_node, current_file 

        children = current_node.get("inner", [])
        for child in reversed(children):
            stack.append(child)

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

def find_function_pointer_typedefs(c_file: str) -> list[str]:
    result = dump_clang_ast(c_file)

    if (result.get("ok") == False):
        return [f"ERROR: failed to dump clang ast; {result.get('stderr')}"]

    ast = result.get("ast")
    typedefs = []

    # only use the file name (strip path)
    target_file = Path(c_file).name

    for node, file_path in walk_clang_ast(ast):
        if node.get("kind") == "TypedefDecl" and node.get("name") is not None:
            if target_file == Path(file_path).name:
                qualType = node.get("type", {}).get("qualType", "")
                if ("(*)" in qualType) or ("(*" in qualType and ")" in qualType):
                    typedefs.append(node.get("name"))

    return typedefs

def find_function_pointer_declarations(c_file: str) -> list[str]:
    typedefs = find_function_pointer_typedefs(c_file)
    result = dump_clang_ast(c_file)

    if (result.get("ok") == False):
        return [f"ERROR: failed to dump clang ast; {result.get('stderr')}"]
    
    ast = result.get("ast")

    # only use the file name (strip path)
    target_file = Path(c_file).name

    variables = []
    for node, file_path in walk_clang_ast(ast):
        if node.get("kind") == "VarDecl" and node.get("name") is not None:
            if target_file == Path(file_path).name:
                name = node.get("name")
                var_type = node.get("type", {})
                qualType = var_type.get("qualType", "")
                if (any(typedef in qualType for typedef in typedefs) or ("(*)" in qualType)):
                    variables.append(name);
    
    return variables

def find_DeclRefExpr_helper(node: dict) -> dict | None:
    if node is None:
        return None

    if node.get("kind") == "DeclRefExpr":
        return node
    
    children = node.get("inner", [])
    for child in children:
        result = find_DeclRefExpr_helper(child)
        if result is not None:
            return result
    
    return None

def find_pointer_assignments(c_file: str) -> list[str]:
    variables = find_function_pointer_declarations(c_file)
    functions = find_function_declarations(c_file)

    result = dump_clang_ast(c_file)

    if (result.get("ok") == False):
        return [f"ERROR: failed to dump clang ast; {result.get('stderr')}"]
    
    ast = result.get("ast")

    # only use the file name (strip path)
    target_file = Path(c_file).name

    pointer_assignments = []
    current_function = None

    for node, file_path in walk_clang_ast(ast):
        if node.get("kind") == "FunctionDecl" and target_file == Path(file_path).name:
            current_function = node.get("name")

        if node.get("kind") == "BinaryOperator":
            if node.get("opcode") == "=" and target_file == Path(file_path).name:
                children = node.get("inner", [])
                if (len(children) < 2):
                    continue

                lhs_node = find_DeclRefExpr_helper(children[0])
                rhs_node = find_DeclRefExpr_helper(children[1])
                if (lhs_node is None or rhs_node is None):
                    continue

                lhs_name = lhs_node.get("name") or lhs_node.get("referencedDecl", {}).get("name")
                rhs_name = rhs_node.get("name") or rhs_node.get("referencedDecl", {}).get("name")

                if (lhs_name in variables and rhs_name in functions):
                    scope = f" (in {current_function})" if current_function else " (global)"
                    pointer_assignments.append(lhs_name + " = " + rhs_name + scope)

    return pointer_assignments

# def instrument_CFI_checks():
#     return

def write_file(c_file: str, content: str) -> dict:
    try: 
        Path(c_file).parent.mkdir(parents = True, exist_ok = True)
        Path(c_file).write_text(content)
        return {
            "ok": True,
            "c_file": c_file
        }
    except Exception as err:
        return {
            "ok": False,
            "error": str(err)
        }

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

def write_log(content: str, log_filename: str) -> dict:
    try:
        Path("logs").mkdir(exist_ok = True)
        log_path = Path("logs") / log_filename
        log_path.write_text(content)
        return {
            "ok": True,
            "log_file": str(log_path)
        }
    except Exception as err:
        return {
            "ok": False,
            "error": str(err)
        }

def restore_file(file: str) -> dict:
    try:
        result = subprocess.run(
            ["git", "restore", file],
            capture_output = True, text = True
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as err:
        return {
            "ok": False,
            "stderr": f"ERROR: {err}"
        }

# policy generation
def write_policy(target_dir: str, policy: list) -> dict:
    if policy is None:
        return {
            "ok": False,
            "error": "Missing 'policy' argument, must provide a list of CFI rules."
        }
    policy_path = Path(target_dir) / "policy.cfi.json"

    with open(policy_path, "w") as f:
        json.dump(policy, f, indent = 2)

    return {
        "ok": True,
        "path": str(policy_path),
    }

def compile_llvm_pass() -> dict:
    llvm_lib = Path("cfi_pass.dylib")
    if llvm_lib.exists():
        return {
            "ok": True, 
            "path": str(llvm_lib),
        }

    result = subprocess.run(
        "clang++ -shared -fPIC cfi_pass.cpp -o cfi_pass.dylib "
        "$(llvm-config --cxxflags --ldflags --libs core support passes) "
        " -undefined dynamic_lookup",
        shell = True, capture_output = True, text = True
    )

    return {
        "ok": result.returncode == 0,
        "path": str(llvm_lib)
    }

def policy_to_llvm_pass(c_files, policy_file: str) -> dict:
    if isinstance(c_files, str):
        c_files = [c_files]

    if not c_files:
        return {
            "ok": False,
            "error": "No C files were provided"
        }
    

    stem = Path(c_files[0]).parent.name
    target_dir = str(Path(c_files[0]).parent)
    bin_dir = Path(target_dir) / "bin"
    bin_dir.mkdir(exist_ok = True)

    linked_ll_file = bin_dir / f"{stem}_linked.ll"
    cfi_ll = bin_dir / f"{stem}_cfi.ll"
    binary = bin_dir / f"{stem}_cfi"

    ll_files = []
    for c_file in c_files:
        ll_file = bin_dir / f"{Path(c_file).stem}.ll"

        # convert c to the IR representation
        result = subprocess.run(["clang", "-S", "-emit-llvm", c_file, "-o", str(ll_file)], capture_output = True, text = True)
        if result.returncode != 0:
            return {
                "ok": False,
                "fail_stage": "compile_to_ir",
                "stderr": result.stderr,
            }
        ll_files.append(str(ll_file))

    # run the pass
    if (len(ll_files) > 1):
        result = subprocess.run(["llvm-link", "-S", *ll_files, "-o", str(linked_ll_file)], capture_output = True, text = True)
        if (result.returncode != 0):
            return {
                "ok": False,
                "fail_stage": "run_pass",
                "stderr": result.stderr,
            }
        input_ll = linked_ll_file
    else:
        input_ll = ll_files[0]

    result = subprocess.run(["opt", "-load-pass-plugin=./cfi_pass.dylib", "-passes=cfi-enforce", f"-cfi-policy={policy_file}", str(input_ll), "-S", "-o",str(cfi_ll)], capture_output = True, text = True)
    if result.returncode != 0:
        return {
            "ok": False,
            "fail_stage": "run_pass",
            "stderr": result.stderr,
        }

    # convert IR to binary
    result = subprocess.run(["clang", str(cfi_ll), "-o", str(binary), "-lm"], capture_output = True, text = True)
    if result.returncode != 0:
        return {
            "ok": False,
            "fail_stage": "convert_IR_to_binary",
            "stderr": result.stderr,
        }

    return {
        "ok": True,
        "binary": str(binary)
    }

# advanced tools 
def generate_cfg(c_file: str):
    return

def find_callers(c_file: str, function_name: str):
    return

def find_struct_field_accesses(c_file: str):
    return

def compile_and_run(c_file: str):
    return

def find_type_compatible_functions(c_file: str, signature: str):
    return

def run_command(cmd: str):
    return

'''
def main():
    print(configure_toolchain())

    print(list_c_files("targets/example1"))
    # print(read_c_file("targets/example1/example1.c"))

    compile_to_llvm("targets/example1/example1.c")
    print(find_indirect_calls("outputs/example1.ll"))

    result = dump_clang_ast("targets/example1/example1.c")
    print(result["ok"])
    print(result["stderr"])

    print(find_function_declarations("targets/example1/example1.c"))
    print(find_function_pointer_typedefs("targets/example1/example1.c"))
    print(find_function_pointer_declarations("targets/example1/example1.c"))
    print(find_pointer_assignments("targets/example1/example1.c"))

if __name__ == "__main__":
    main()
'''