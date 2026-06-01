# Agentic CFI

An agentic pipeline that generates Control-Flow Integrity policies for C programs. The agent analyzes indirect call sites utilizing IRs of programs, reasons about the semantics of the program statically and utilizes tests given by the user to dynamically verify execution, and then constructs a target set for every indirect call set of permissible functions to jump to.

The agent then constructs a JSON file, which runs through an LLVM pass to generate a hardened binary that prevents forward-edge hijacking. We provide multiple sample test cases, as well as a real world test case against tinyexpr.

## Setup and Test
```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env
python3 pipeline.py targets/example1
```

## Output Data
The agent writes its log in `logs/<basename>.log`, where `<basename>` is the name of the directory that the pipeline was run on. You can find the policy.json file in the target directory of the pipeline by running `git checkout blue/<basename>`, as we use git as a snapshotting feature. The hardened binary can also be found this way.

## Acknowledgments
 
We utilize [tinyexpr](https://github.com/codeplea/tinyexpr) by Lewis Van Winkle (under the zlib license), used as a real-world target.