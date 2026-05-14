import json
from openai import OpenAI
from tools import (
    configure_toolchain, list_c_files, read_file, 
    compile_to_llvm, compile_to_binary, find_indirect_calls,
    find_function_declarations, find_function_pointer_typedefs,
    find_function_pointer_declarations, find_pointer_assignments,
    write_file, run_tests, dump_clang_ast
)
from prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

# mapping tool names to functions and their schemas
TOOLS = {
    "configure_toolchain": configure_toolchain,
    "list_c_files": list_c_files,
    "read_file": read_file,
    "compile_to_llvm": compile_to_llvm,
    "compile_to_binary": compile_to_binary,
    "find_indirect_calls": find_indirect_calls,
    "find_function_declarations": find_function_declarations,
    "find_function_pointer_typedefs": find_function_pointer_typedefs,
    "find_function_pointer_declarations": find_function_pointer_declarations,
    "find_pointer_assignments": find_pointer_assignments,
    "write_file": write_file,
    "run_tests": run_tests,
    "dump_clang_ast": dump_clang_ast,
}

# tool schemas for OpenAI
# region
TOOL_SCHEMAS = [
    # CONFIGURE_TOOLCHAIN
    {
        "type": "function",
        "function" : {
            "name": "configure_toolchain",
            "description": "Ensure clang is downloaded",
            "parameters": {"type": "object", "properties": {}}
        }
    },

    # LIST_C_FILES
    {
        "type": "function",
        "function" : {
            "name": "list_c_files",
            "description": "List all .c files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "Path to the directory"}
                },
                "required": ["folder"]
            }
        }
    },

    # READ_FILE
    {
        "type": "function",
        "function" : {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Path to the file"},
                    "max_chars": {"type": "integer", "description": "Maximum file length to display."},
                },
                "required": ["file"]
            }
        }
    },

    # COMPILE_TO_LLVM
    {
        "type": "function",
        "function" : {
            "name": "compile_to_llvm",
            "description": "Compile .c source file to its LLVM output",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to the .c source file"},
                    "out_dir": {"type": "string", "description": "Path to output LL file directory"},
                },
                "required": ["c_file"]
            }
        }
    },

    # COMPILE_TO_BINARY
    {
        "type": "function",
        "function" : {
            "name": "compile_to_binary",
            "description": "Compile .c source file to binary file",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to the .c source file"},
                    "out_dir": {"type": "string", "description": "Path to output binary file directory"},
                },
                "required": ["c_file"]
            }
        }
    },

    # FIND_INDIRECT_CALLS
    {
        "type": "function",
        "function" : {
            "name": "find_indirect_calls",
            "description": "Find indirect function call sites in .ll files",
            "parameters": {
                "type": "object",
                "properties": {
                    "ll_file": {"type": "string", "description": "Path to the .ll file"},
                },
                "required": ["ll_file"]
            }
        }
    },

    # DUMP_CLANG_AST
    {
        "type": "function",
        "function" : {
            "name": "dump_clang_ast",
            "description": "Output AST .json file from .c source file",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to the .c source file"},
                },
                "required": ["c_file"]
            }
        }
    },

    # FIND_FUNCTION_DECLARATIONS
    {
        "type": "function",
        "function" : {
            "name": "find_function_declarations",
            "description": "Find in-file function declarations via the AST of a .c file",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to .c source file"},
                },
                "required": ["c_file"]
            }
        }
    },

    # FIND_FUNCTION_POINTER_TYPEDEFS
    {
        "type": "function",
        "function" : {
            "name": "find_function_pointer_typedefs",
            "description": "Find in-file new function pointer types",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to .c source file"},
                },
                "required": ["c_file"]
            }
        }
    },

    # FIND_FUNCTION_POINTER_DECLARATIONS
    {
        "type": "function",
        "function" : {
            "name": "find_function_pointer_declarations",
            "description": "Find in-file declarations of function pointers",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to .c source file"},
                },
                "required": ["c_file"]
            }
        }
    },

    # FIND_POINTER_ASSIGNMENTS
    {
        "type": "function",
        "function" : {
            "name": "find_pointer_assignments",
            "description": "Find in-file function pointer assignments",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to .c source file"},
                },
                "required": ["c_file"]
            }
        }
    },

    # WRITE_FILE
    {
        "type": "function",
        "function" : {
            "name": "write_file",
            "description": "Add CFI checks to a .c source file by writing the entire source file, but it must have the same functionality",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to .c source file"},
                    "content": {"type": "string", "description": "New .c file content"},
                },
                "required": ["c_file", "content"]
            }
        }
    },

    # RUN_TESTS
    {
        "type": "function",
        "function" : {
            "name": "run_tests",
            "description": "Run test scripts in target directories",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "Path to target folder"},
                },
                "required": ["folder"]
            }
        }
    },
]
# endregion

def run_agent(target_dir: str, max_steps: int = 20):
    client = OpenAI()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze the C project in '{target_dir}' for forward-edge CFI."
        "Find all indirect call sites, determine valid target sets, "
        "instrument CFI checks, and validate with tests."}
    ]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model = "gpt-4o",
            messages = messages,
            tools = TOOL_SCHEMAS,
        )

        msg = response.choices[0].message
        messages.append(msg)

        # agent wants to call some tool
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"[Step {step}], agent calls {name}({args})")
                result = TOOLS[name](**args)
                log_steps(step, name, args, result)

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
    run_agent("targets/example1")