import os
import sys
import json
import shlex
import getpass
import argparse
import subprocess
from appdirs import AppDirs
from pathlib import Path
from _thread import interrupt_main
from threading import Timer

TUNNELING_PORT="48097"

auth_file = Path(AppDirs("tau-supernova").user_config_dir) / "auth"
auth_data = None
if not auth_file.is_file():
    print("No auth data found.")
    new_username = input("username: ")
    new_pass = getpass.getpass("password: ")
    auth_data = {"username": new_username, "password": new_pass}
    auth_file.parent.mkdir(parents=True)
    with open(auth_file, "w") as f:
        json.dump(auth_data, f)
    print("Saved to", auth_file)
else:
    with open(auth_file, "r") as f:
        auth_data = json.load(f)

my_parser = argparse.ArgumentParser(
        description="My CLI to upload folders and get shell in nova.cs.tau.ac.il"
)
my_parser.add_argument("--upload", type=Path, help="Uploads this before connecting", nargs="*")
my_parser.add_argument("--script", type=Path, help="Run this Python script instead of connecting")
my_parser.add_argument("--test",   type=str,  help="Run this test script instead of connecting")
args = my_parser.parse_args()

# Connect to gate
tunnel_proc = subprocess.Popen(
        ["plink", "-pw", auth_data["password"],
         "-hostkey", "d4:98:42:6d:96:24:fa:ce:48:1a:ae:0a:20:15:ed:93",
         "-ssh", "-L", TUNNELING_PORT + ":nova.cs.tau.ac.il:22",
         auth_data["username"] + "@gate.tau.ac.il"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# if it takes more than 5 seconds to reach Welcome, it's a failed attempt
timeout_timer = Timer(5, interrupt_main)

try:
    timeout_timer.start()
    tunnel_line = tunnel_proc.stdout.readline()
    while not tunnel_line.startswith(b"Welcome"):
        tunnel_line = tunnel_proc.stdout.readline()
    timeout_timer.cancel()
except:
    print("Couldn't connect to tunnel - either an incorrect password or no internet.")

print("Tunneling connected on port", TUNNELING_PORT)
conn_command = f"plink -pw {auth_data['password']} -hostkey b5:ee:e3:25:dd:35:94:c4:c1:98:f0:16:e9:3a:42:f8 -ssh -P {TUNNELING_PORT} {auth_data['username']}@localhost"

for upload in args.upload or []:
    upload = upload.resolve()  # if we say . it should get the real folder name
    # remove folder if exists
    rm_proc = subprocess.Popen(shlex.split(conn_command) + ["rm -rf", upload.parts[-1]])
    rm_proc.wait()
    # copy files to Nova
    print(subprocess.run(
            ["pscp", "-pw", auth_data['password'],
             "-hostkey", "b5:ee:e3:25:dd:35:94:c4:c1:98:f0:16:e9:3a:42:f8",
             "-scp", "-r", "-P", TUNNELING_PORT,
             upload, auth_data["username"] + "@localhost:" + upload.parts[-1]], check=True))

# connect to Nova
script_arg = args.script
if args.test:
    # shortcut for setting the test to something from the tests directory
    test_path = Path(__file__).parent / "tests" / (args.test + ".py")
    if not test_path.is_file():
        print("Not a valid test! Choose from", ", ".join(x.parts[-1].split(".")[0]
              for x in (Path(__file__).parent / "tests").iterdir()) + ".")
        sys.exit(1)
    script_arg = test_path
if script_arg:
    # copy script
    print(subprocess.run(
            ["pscp", "-pw", auth_data['password'],
             "-hostkey", "b5:ee:e3:25:dd:35:94:c4:c1:98:f0:16:e9:3a:42:f8",
             "-scp", "-r", "-P", TUNNELING_PORT,
             script_arg.resolve(), auth_data["username"] + "@localhost:script.py"], check=True))
    # run script
    script_proc = subprocess.Popen(shlex.split(conn_command) + ["python3 script.py && rm script.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    script_proc.wait()
    print(script_proc.stdout.read().decode("utf-8"))
    if script_proc.returncode == 0:
        print("\033[32mSuccess!\033[m", end="")
    else:
        print("\033[31mERROR!\033[m", end="")
        sys.exit(1)
else:
    os.system(conn_command)
tunnel_proc.kill()
