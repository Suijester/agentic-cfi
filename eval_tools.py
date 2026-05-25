from pathlib import Path
import subprocess
from tools import run_tests

'''
MAY NOT BE UTILIZED BY AGENT
Evaluator Tools:
- run concealed hijacking tests on some directories
- compare protected vs unprotected behavior on tests
- measure false positives from excessively restrictive CFI target sets
- scoring policy qualities, e.g. # of normal and hijacking tests passed, false positives, unsafe call sites that aren't fixed
'''

def evaluate(target_dir: str) -> dict:
    eval_script = Path(target_dir) / "eval_tests.sh"
    result = subprocess.run(["bash", str(eval_script)], capture_output = True, text = True)

    return {
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

def score_all(targets: list[str]) -> dict:
    results = {}
    for target in targets:
        results[target] = {
            "functional_tests": run_tests(target), # no false positives
            "eval_tests": evaluate(target)
        }
    
    return results