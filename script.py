import os
import json
import getpass
import argparse
import subprocess
from appdirs import AppDirs
from pathlib import Path

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
my_parser.add_argument("--upload", type=Path, help="Uploads this before connecting")
args = my_parser.parse_args()

# Connect to gate
tunnel_proc = subprocess.Popen(
        ["plink", "-pw", auth_data["password"],
         "-hostkey", "d4:98:42:6d:96:24:fa:ce:48:1a:ae:0a:20:15:ed:93",
         "-ssh", "-L", TUNNELING_PORT + ":nova.cs.tau.ac.il:22",
         auth_data["username"] + "@gate.tau.ac.il"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
tunnel_line = tunnel_proc.stdout.readline()
print("tunneling log:", tunnel_line)
while not tunnel_line.startswith(b"Welcome"):
    tunnel_line = tunnel_proc.stdout.readline()
    if len(tunnel_line) > 0:
        print("tunneling log:", tunnel_line)
print("Tunneling connected on port", TUNNELING_PORT)

if args.upload:
    # copy files to Nova
    print(subprocess.run(
            ["pscp", "-pw", auth_data['password'],
             "-hostkey", "b5:ee:e3:25:dd:35:94:c4:c1:98:f0:16:e9:3a:42:f8",
             "-scp", "-r", "-P", TUNNELING_PORT,
             args.upload, auth_data["username"] + "@localhost:" + args.upload.parts[-1]], check=True))
# connect to Nova
os.system(f"plink -pw {auth_data['password']} -hostkey b5:ee:e3:25:dd:35:94:c4:c1:98:f0:16:e9:3a:42:f8 -ssh -P {TUNNELING_PORT} {auth_data['username']}@localhost")
tunnel_proc.kill()
