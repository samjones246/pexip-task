import sys
from pathlib import Path
import argparse
import poll_watcher as watcher
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
    args = parser.parse_args()
    target = Path(args.path)

    if not target.exists():
        raise ValueError(f"invalid path: {str(target)}")

    def sync(added, removed, changed):
        startTime = time.time()
        if added:
            print("Added:")
            print(added)
        if removed:
            print("Removed:")
            print(removed)
        if changed:
            print("Changed:")
            print(changed)
        print("Establishing connection to server...")
        with socket.create_connection((args.host, args.port)) as sock:
            print("Connection established.")
            print("Sending number of files...")
            numfiles = len(added) + len(changed) + len(removed)
            sock.sendall(numfiles.to_bytes(2, byteorder='big'))
            for fpath, ftype in added:
                relpath = os.path.relpath(fpath, target.absolute())
                filesize = os.stat(fpath).st_size
                data = f"A;{ftype};{relpath};{filesize}".encode("utf-8")
                print("Sending %i bytes" % len(data))
                sock.sendall(data)
                if ftype == "F":
                    with open(fpath, 'rb') as f:
                        print("Waiting for server...")
                        sock.recv(1)
                        print("Sending file...")
                        sock.sendfile(f)
                        print("File sent")
            for fpath, ftype in changed:
                relpath = os.path.relpath(fpath, target.absolute())
                sock.sendall(f"C;{ftype};{relpath.ljust(255, ' ')}".encode("utf-8"))
                print("Sent data")
                if ftype == "F":
                    with open(fpath, 'rb') as f:
                        sock.recv(1)
                        sock.sendfile(f)
            for fpath, ftype in removed:
                relpath = os.path.relpath(fpath, target.absolute())
                sock.sendall(f"R;{ftype};{relpath.ljust(255, ' ')}".encode("utf-8"))
                print("Sent data")
        totalTime = time.time() - startTime
        print(f"Update complete ({totalTime}s)")

    # TODO: Get initial contents of server folder at initialisation
    watcher.watch(target, sync)

if __name__ == "__main__":
    main()