from subprocess import Popen
import sys

filename = sys.argv[1]
while True:
    print("\nStarting " + filename)
    p = Popen("poetry install && poetry run python " + filename, shell=True)
    p.wait()