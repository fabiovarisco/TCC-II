import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("message")
args = parser.parse_args()

subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f'"{args.message}"'])
subprocess.run(["git", "push", "origin", "master"])
