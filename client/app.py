import sys
from pathlib import Path
import argparse
import poll_watcher as watcher
import json
import socket

def main():
    parser = argparse.ArgumentParser(description="Keep the contents of a folder synchronised with a server.")
    parser.add_argument("path", type=str, help="Path to the folder which should be synchronised.\
                                                Can be relative to your current working directory or absolute.")
    parser.add_argument("--host", type=str, help="Location of the server to synchronise to (default: localhost)",
                        default="localhost")
    parser.add_argument("--port", type=int, help="Port to connect to the server through (default: 5000",
                        default=5000)
    args = parser.parse_args()
    target = Path(args.path)

    if not target.exists():
        raise ValueError(f"invalid path: {str(target)}")

    def sync(added, removed, changed):
        if added:
            print("Added:")
            print(added)
        if removed:
            print("Removed:")
            print(removed)
        if changed:
            print("Changed:")
            print(changed)

    watcher.watch(target, sync)

if __name__ == "__main__":
    main()