import json
from openai import OpenAI
from tools import (
    compile_llvm_pass, configure_toolchain, list_c_files, policy_to_llvm_pass, read_file, 
    compile_to_llvm, find_indirect_calls,
    find_function_declarations, find_function_pointer_typedefs,
    find_function_pointer_declarations, find_pointer_assignments,
    write_file, run_tests, dump_clang_ast, write_log
)
from prompts import BLUE_PROMPT
from dotenv import load_dotenv
import argparse
from schemas import TOOL_SCHEMAS

load_dotenv()

# mapping tool names to functions and their schemas
TOOLS = {
    "list_c_files": list_c_files,
    "read_file": read_file,
    "compile_to_llvm": compile_to_llvm,
    "find_indirect_calls": find_indirect_calls,
    "find_function_declarations": find_function_declarations,
    "find_function_pointer_typedefs": find_function_pointer_typedefs,
    "find_function_pointer_declarations": find_function_pointer_declarations,
    "find_pointer_assignments": find_pointer_assignments,
    "write_file": write_file,
    "run_tests": run_tests,
    "write_log": write_log,
    "write_policy": write_policy,
    "compile_llvm_pass": compile_llvm_pass,
    "policy_to_llvm_pass": policy_to_llvm_pass,
}

BLUE_SCHEMAS = [TOOL_SCHEMAS[t] for t in [
    "list_c_files", "read_file", "compile_to_llvm",
    "find_indirect_calls", "find_function_declarations", 
    "find_function_pointer_typedefs", "find_function_pointer_declarations",
    "find_pointer_assignments", "write_file", "run_tests", "write_log",
    "write_policy", "compile_llvm_pass", "policy_to_llvm_pass"
]]

def run_blue_agent(target_dir: str, max_steps: int = 20, feedback: str = None):
    res = configure_toolchain();
    if not res["ok"]:
        print("ERR: toolchain not configured properly")
        return

    client = OpenAI()

    messages = [
        {"role": "system", "content": BLUE_PROMPT},
        {"role": "user", "content": f"Analyze the C project in '{target_dir}' for forward-edge CFI."
        "Find all indirect call sites, determine valid target sets, "
        "instrument CFI checks, and validate with tests."}
    ]

    if feedback:
        messages.append({
            "role": "user",
            "content": feedback,
        })

    for step in range(max_steps):
        response = client.chat.completions.create(
            model = "gpt-4o",
            messages = messages,
            tools = BLUE_SCHEMAS,
        )

        msg = response.choices[0].message
        messages.append(msg)

        # agent wants to call some tool
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"[Step {step}], agent calls {name}()")
                result = TOOLS[name](**args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default = str)
                })
        
        # agent is done this step :)
        else:
            print(f"[Agent done]")
            print(f"{msg.content}")
            return msg.content
    
    print("Agent hit max step count :(")
    return messages

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help = "Path to target directory")
    args = parser.parse_args()
    
    run_blue_agent(args.path)