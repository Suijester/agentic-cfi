from blue_agent import run_blue_agent
from red_agent import run_red_agent
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
    git("commit", "-m", f"blue agent: {target_name}")

    git("checkout", "-B", f"red/{target_name}")
    run_red_agent(target_dir)
    
    git("add", "-A")
    git("commit", "-m", f"red agent: {target_name}")

    # git merge red -> blue so blue has red's attacks and logs
    git("checkout", f"blue/{target_name}")
    git("merge", f"red/{target_name}", "-m", "merge red attacks")

    # round 2: blue uses adversarial red data to improve itself
    run_blue_agent(target_dir, feedback = "Red-team attack harnesses are added. Review attacks/, the new .c source files, and the logs of those attacks. Using that, improve your CFI to block those attacks, and re-run tests.")
    git("add", "-A")
    git("commit", "-m", f"blue agent: {target_name}")

    git("checkout", "main")

def clean_branches():
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help = "Path to target directory")
    args = parser.parse_args()
    run_pipeline(args.path)

