# tool schemas for OpenAI

TOOL_SCHEMAS_LIST = [
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

    # WRITE_LOG
    {
        "type": "function",
        "function" : {
            "name": "write_log",
            "description": "Write a log file with the final report",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "New .log file content with report"},
                    "log_filename": {"type": "string", "description": ".log file name to write into"}
                },
                "required": ["content", "log_filename"]
            }
        }
    },

    # WRITE_POLICY
    {
        "type": "function",
        "function" : {
            "name": "write_policy",
            "description": "Write a CFI policy JSON file for the target.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_dir": {"type": "string", "description": "Path to target directory"},
                    "policy": {
                        "type": "array",
                        "description": "List of CFI rules",
                        "items": {
                            "type": "object",
                            "properties": {
                                "caller": {"type": "string", "description": "Function containing the indirect call"},
                                "call_index": {"type": "integer", "description": "0-based index of indirect call within the overall function"},
                                "allowed_targets": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Function names that are allowed to be called at this site"
                                }
                            },
                            "required": ["caller", "call_index", "allowed_targets"]
                        }
                    }
                },
                "required": ["target_dir", "policy"]
            }
        }
    },

    # COMPILE_LLVM_PASS
    {
        "type": "function",
        "function" : {
            "name": "compile_llvm_pass",
            "description": "Compile the CFI LLVM pass into a shared library, only needs to be called once",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # POLICY_TO_LLVM_PASS
    {
        "type": "function",
        "function" : {
            "name": "policy_to_llvm_pass",
            "description": "Apply the CFI LLVM pass to a C file using a policy. Compiles C to IR, executes the CFI policy, and links into a binary. Returns path to hardened binary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "c_file": {"type": "string", "description": "Path to C source file"},
                    "policy_file": {"type": "string", "description": "Path to policy.json file"}
                },
                "required": ["c_file", "policy_file"]
            }
        }
    },
]

TOOL_SCHEMAS = {
    tool["function"]["name"]: tool
    for tool in TOOL_SCHEMAS_LIST
}