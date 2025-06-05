import subprocess

subprocess.run(["pip", "install", "bandit"])
subprocess.run(["bandit", "-r", "."])


subprocess.run(["pip", "install", "pip-audit"])
subprocess.run(["pip-audit"])

