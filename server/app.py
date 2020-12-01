import argparse
import socketserver

def main():
    parser = argparse.ArgumentParser(description="Update a folder with changes received from a client application")
    parser.add_argument("path", type=str, help="Path to the folder which should be synchronised.\
                                                Can be relative to your current working directory or absolute.")
    parser.add_argument("--host", type=str, help="Address to bind the server to (default: 0.0.0.0)",
                        default="0.0.0.0")
    parser.add_argument("--port", type=int, help="Port to open the server on (default: 5000)",
                        default=5000)
    args = parser.parse_args()

def add_files(files):
    pass

def remove_files(filenames):
    pass

def update_files(files):
    pass

if __name__ == "__main__":
    main()