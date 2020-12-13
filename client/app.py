import sys
from pathlib import Path
import argparse
import inotify_watcher as watcher
import json
import socket
import os
import time

def main():
    parser = argparse.ArgumentParser(description="Keep the contents of a folder synchronised with a server.")
    parser.add_argument("path", type=str, help="Path to the folder which should be synchronised.\
                                                Can be relative to your current working directory or absolute.")
    parser.add_argument("--host", type=str, help="Location of the server to synchronise to (default: localhost)",
                        default="localhost")
    parser.add_argument("--port", type=int, help="Port to connect to the server through (default: 5000)",
                        default=5000)
    parser.add_argument("--ignore-hidden", type=bool, 
                        help="Ignore any file or directory whose name starts with a '.' (default: true)",
                        default=True)
    args = parser.parse_args()
    target = Path(args.path)

    if not target.exists():
        raise ValueError(f"invalid path: {str(target)}")

    def sync(updates):
        startTime = time.time()
        print("Establishing connection to server...")
        with socket.create_connection((args.host, args.port)) as sock:
            print("Connection established.")
            print("Sending number of files...")
            numfiles = len(updates)
            sock.sendall(numfiles.to_bytes(2, byteorder='big'))
            for utype, fpath, ftype in updates:
                if utype == "M":
                    relpath = ",".join([os.path.relpath(fpath[0], target.absolute()), 
                                        os.path.relpath(fpath[1], target.absolute())])
                else:
                    relpath = os.path.relpath(fpath, target.absolute())
                if utype in ['R', 'M']:
                    filesize = 0
                else:
                    filesize = os.stat(fpath).st_size
                data = f"{utype};{ftype};{relpath};{filesize}".encode("utf-8")
                print("Sending %i bytes" % len(data))
                sock.sendall(data)
                if utype in ['A', 'C'] and ftype == "F":
                    with open(fpath, 'rb') as f:
                        print("Waiting for server...")
                        sock.recv(1)
                        print("Sending file...")
                        sock.sendfile(f)
                        print("File sent")
        totalTime = time.time() - startTime
        print(f"Update complete ({totalTime}s)")

    # TODO: Get initial contents of server folder at initialisation
    watcher.watch(target, sync, args.ignore_hidden)

if __name__ == "__main__":
    main()