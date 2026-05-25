from blue_agent import run_blue_agent
from eval_tools import evaluate
import argparse
import subprocess

def git(*args):
    subprocess.run(["git"] + list(args), check = True)

def run_pipeline(target_dir: str):
    target_name = target_dir.strip("/").split("/")[-1]

    git("checkout", "main")

    git("checkout", "-B", f"blue/{target_name}")
    run_blue_agent(target_dir)

    git("add", "-A")
    git("commit", "--allow-empty", "-m", f"blue agent: {target_name}")

    result = evaluate(target_dir)
    if (result.get("passed") == False):
        printf("Blue agent failed to properly analyze target directory.")

    git("checkout", "main")

def clean_branches():
    for i in range(4):
        git("branch", "-D", f"blue/example{i}")
    
    print("branches deleted :O")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help = "Path to target directory")
    args = parser.parse_args()
    run_pipeline(args.path)

