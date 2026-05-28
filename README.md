# Agentic CFI

An agentic pipeline that generates Control-Flow Integrity policies for C programs. The agent analyzes indirect call sites utilizing IRs of programs, reasons about the semantics of the program statically and utilizes tests given by the user to dynamically verify execution, and then constructs a target set for every indirect call set of permissible functions to jump to.

The agent then constructs a JSON file, which runs through an LLVM pass to generate a hardened binary that prevents forward-edge hijacking. We provide multiple sample test cases, as well as a real world test case against tinyexpr.

## Quick Start
```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env
python3 pipeline.py targets/example1
```

## Acknowledgments
 
We utilize [tinyexpr](https://github.com/codeplea/tinyexpr) by Lewis Van Winkle (under the zlib license), used as a real-world target.