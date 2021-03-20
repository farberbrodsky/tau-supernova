from sys import exit
from pathlib import Path
import subprocess

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[m"

real_dir = None
for homefile in Path(".").iterdir():
    name = homefile.resolve().parts[-1]
    if name.startswith("hw2-") and homefile.is_dir():
        real_dir = homefile.resolve()

if real_dir is None:
    print("Can't find an uploaded folder with a name that starts with hw2-")
    exit(1)


print("Compiling all files...")
java_files = real_dir.glob("**/*.java")
for java_file in java_files:
    compiler_proc = subprocess.Popen(
        ["javac", java_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    compiler_proc.wait()
    if compiler_proc.returncode != 0:
        print(RED + "Couldn't compile", java_file + RESET)
        exit(1)
        pass
    else:
        print("Compiled", java_file)
print(GREEN + "Compiled successfuly!" + RESET)


def assert_eq(test_name, output, expected):
    if output != expected:
        print(
            RED + "FAILED", test_name, "expected",
            str(expected), "got", str(output) + "." + RESET)
        exit(1)
    else:
        print(GREEN + "Passed", test_name + "." + RESET)


src_dir = real_dir / "src"
# Real tests start here
print("Running Assigment02Q01 tests...")

assert_eq(
    "official example",
    subprocess.check_output(
        ["java", "il.ac.tau.cs.sw1.ex2.Assignment02Q01",
         "Before", "a", "E", "f"],
        cwd=src_dir),
    b"B\nf\n"
)

print("Running Assignment02Q02 tests...")

assert_eq(
    "official example 100",
    subprocess.check_output(
        ["java", "il.ac.tau.cs.sw1.ex2.Assignment02Q02",
         "100"],
        cwd=src_dir),
    b"3.1315929035585537 3.141592653589793\n"
)

assert_eq(
    "official example 4",
    subprocess.check_output(
        ["java", "il.ac.tau.cs.sw1.ex2.Assignment02Q02",
         "4"],
        cwd=src_dir),
    b"2.8952380952380956 3.141592653589793\n"
)

assert_eq(
    "test 1",
    subprocess.check_output(
        ["java", "il.ac.tau.cs.sw1.ex2.Assignment02Q02",
         "1"],
        cwd=src_dir),
    b"4.0 3.141592653589793\n"
)

print("Running Assigment02Q03 tests...")

assert_eq(
    "official example 20",
    subprocess.check_output(
        ["java", "il.ac.tau.cs.sw1.ex2.Assignment02Q03",
         "20"],
        cwd=src_dir),
    b"The first 20 Fibonacci numbers are:\n1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987 1597 2584 4181 6765\nThe number of even numbers is: 6\n"
)

assert_eq(
    "official example 10",
    subprocess.check_output(
        ["java", "il.ac.tau.cs.sw1.ex2.Assignment02Q03",
         "10"],
        cwd=src_dir),
    b"The first 10 Fibonacci numbers are:\n1 1 2 3 5 8 13 21 34 55\nThe number of even numbers is: 3\n"
)

print("Running Assigment02Q04 tests...")
print("Running Assigment02Q05 tests...")
