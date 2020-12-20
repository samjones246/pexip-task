# Pexip Homework
## Task
The code in this repository aims to accomplish the following task, set as part of the Pexip recruitment process:
> Build an application to synchronise a source folder and a destination folder over IP:
>
> 1.1 a simple command line client which takes one directory as argument and keeps monitoring changes in that directory and uploads any change to its server
>
> 1.2 a simple server which takes one empty directory as argument and receives any change
from its client

---
## Usage
**COMPATABILITY:** I have made use of the Linux Kernel's **inotify** feature (via the [inotify](https://pypi.org/project/inotify/) python library) for the client application, so the client is only compatible with Linux. The server, however, does not use any external libraries, and so should be platform independent. 

Before using the client, you will need to install its dependencies, which are listed in `client/requirements.txt`. For example, use the following commands (inside the `client` folder) to create a virtual environment and install dependencies:

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

After installing dependencies, you will first need to start the server application. Below is the usage information for the server (`server/app.py`):

    usage: app.py [-h] [--host HOST] [--port PORT] path

    Update a folder with changes received from a client application

    positional arguments:
    path         Path to the folder which should be synchronised. Can be relative to your current working directory or absolute.

    optional arguments:
    -h, --help   show this help message and exit
    --host HOST  Address to bind the server to (default: 0.0.0.0)
    --port PORT  Port to open the server on (default: 5000)
    --clean      If the destination folder is not empty, delete its contents on startup. If this option is not specified and a non-empty destination folder is given, the process will fail.

For example, to run the server with target folder *dest* and default address binding settings (0.0.0.0:5000):

    $ python app.py dest

The above example uses a relative path, so the application will look in your current working directory for the folder. You can instead use an absolute path, like so:

    $ python app.py /home/jsmith/dest

The default host option of 0.0.0.0 will allow the server to be externally visible given the correct network configuration. Both the host and port options can be changed with optional arguments:

    $ python app.py dest --host 127.0.0.1 --port 3333

By default, if the destination folder is not empty, the server will exit with an error. By specifying the optional flag `--clean`, the destination folder will instead be emptied. Use appropriate caution.

Once the server is up and running, you can start the client application to begin syncing files. Note that if you start the client before starting the server, it will crash with an error due to not being able to connect to the server. The same will happen if the server application is closed while the client is running, but not until the next time a change is made in the source folder. Below is the usage information for the client application (`client/app.py`):

    usage: app.py [-h] [--host HOST] [--port PORT] [--include-hidden] path

    Keep the contents of a folder synchronised with a server.

    positional arguments:
    path                  Path to the folder which should be synchronised. Can be relative to your current working directory or absolute.

    optional arguments:
    -h, --help            show this help message and exit
    --host HOST           Location of the server to synchronise to (default: localhost)
    --port PORT           Port to connect to the server through (default: 5000)
    --include-hidden, -a  If specified, do not ignore files or directories whose names start with a '.'

For example, to run the client application with source folder `src` and default host settings (localhost:5000, so the server must be running on the same machine as the client):

    $ python app.py src

If instead you would like to connect to a remote host at 12.34.56.78:3333:

    $ python app.py --host 12.34.56.78 --port 3333 src

By default, hidden files and directories (those with names starting with a '.') will be ignored and not uploaded to the server. This bahviour can be disabled with the --include-hidden (or -a) flag, like so:

    $ python app.py --include hidden src

If the source folder is not empty when you start the client, it should immediately upload the current contents to the server. After this, any changes made in the source folder will be detected and uploaded to the server.

## Approach
### Client
### Server

## Future Work