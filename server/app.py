import argparse
import socketserver
import os

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            data = tuple(self.request.recv(512).decode('utf-8').split(";"))
            print(data)
            changetype, filetype, filepath = data
            self.request.sendall(b"1")
            if changetype in ["A", "C"]:
                if filetype == "D":
                    os.mkdir(os.path.join(self.server.path, filepath))
                elif filetype == "F":
                    with open(os.path.join(self.server.path, filepath), 'wb') as f:
                        f.write(self.rfile.read())
            elif changetype == "R":
                os.remove(os.path.join(self.server.path, filepath))
            print("Success")
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Update a folder with changes received from a client application")
    parser.add_argument("path", type=str, help="Path to the folder which should be synchronised.\
                                                Can be relative to your current working directory or absolute.")
    parser.add_argument("--host", type=str, help="Address to bind the server to (default: 0.0.0.0)",
                        default="0.0.0.0")
    parser.add_argument("--port", type=int, help="Port to open the server on (default: 5000)",
                        default=5000)
    args = parser.parse_args()
    print(f"Starting server at {args.host}:{args.port}, target folder {args.path}...")
    with socketserver.TCPServer((args.host, args.port), Handler) as server:
        server.path = args.path
        server.serve_forever()

if __name__ == "__main__":
    main()