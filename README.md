# tau-supernova
A simple script for connecting and uploading files to Nova. Requries PuTTY to be installed.

On the first run, it asks for your username and password, and saves it locally.
Usage:

```
# Connect to Nova
python3 script.py
# Connect to Nova and upload
python3 script.py --upload /path/to/folder
# Connect to Nova and upload current folder. It uploads to a folder of the same name.
python3 script.py --upload .
# Connect to Nova and upload multiple folders.
python3 script.py --upload /path/to/thing /path/to/other/thing
```
