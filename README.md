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

By default, hidden files and directories (those with names starting with a '.') will be ignored and not uploaded to the server. This behaviour can be disabled with the --include-hidden (or -a) flag, like so:

    $ python app.py --include hidden src

If the source folder is not empty when you start the client, it should immediately upload the current contents to the server. After this, any changes made in the source folder will be detected and uploaded to the server.

---

## Approach
There were two main implementation decisions to consider with this task: how to watch a directory for changes, and how to send those changes over IP to a server. I considered a few options for each of these, but settled on the ones which I thought would be most efficient.

For monitoring a directory, I first tried the simple approach of polling the directory at a fixed interval and comparing it with a snapshot taken at the previous poll. While this had the advantage of not requiring any third party libraries and being easy to implement, it would not have scaled well, and it meant that there was always a delay between a change being made and that change being detected by the application. I then decided to take advantage of being given free choice over which operating system to develop for, and moved to a new approach which uses **inotify** from the Linux kernel. Inotify can be used to place a watch on a directory. Whenever a change is made in the directory, the watch fires an event describing the change. This is a much nicer approach, which isn't constantly doing unnecessary work when no changes are being made and can respond immediately when changes are made. While it would be possible to implement this approach without any external packages, there is an inotify python package which provides an interface to inotify and saves me some legwork.

For uploading the changes, I briefly considered using a protocol such as HTTP or FTP, but both of these come with overhead which isn't necessary for this application and would really just slow down the process. Instead, I went with the lowish level approach of sockets, allowing me to send raw data without any headers so that I can more easily minimise the amount of data that I need to transfer. Below is an outline of the data transfer process between client and server:
 - Client establishes connection to server
 - Client sends a single int, telling server how many updates will be sent
 - Server receives this number and begins a loop:
   - Server sends a single byte to the client to say "Ready to receive update info"
   - Client receives this byte and replies with info for the next update to be sent. This packet contains the following pieces of information, each seperated by a semi-colon:
     - Update type, which is either A (file added), R (file removed), C (file changed), or M (file moved or renamed).
     - File type, which is either F (regular file) or D (directory)
     - File path (including name) relative to the source/destination folder. For update type M, this is instead tuple of the form (*old path*, *new path*).
     - Filesize in bytes
    - Server receives update info and takes action according to the update type:
      - **A (file added)** - If the file type is directory, simply create the directory. Otherwise, the server needs the content for the newly created file. The client will be waiting for the signal to send this content, so send a single byte back to tell the client to start sending. Then, receive a number of bytes equal to the size of the new file.
      - **R (file removed)** - Delete the file at the specified address. If the file type is directory, recurseively delete the contents of the directory as well as the directory itself.
      - **C (file changed)** - Receive new contents for the specified file and overwrite old contents. This uses the same process as for adding a new file - signal the client to start sending the file, and then receive *filesize* bytes.
      - **M (file moved)** - Move the file/directory located at the specified *old path* to *new path*.
  - Once the loop has finished (all updates have been received and processed), the connection is ended.

This process is initiated immediately when the client is started in order to synchronise the initial contents of the source folder, and then again whenever an update is detected.

---

## Shortcomings
There are a few aspects of this application (of which I am aware) which could definitely be improved. 

Firstly, there is a bug with the inotify python package relating to recreated directories. If a sub-directory of the watched directory is deleted and then a new directory is created with the same name as the deleted one, changes in that new directory will not be detected. This is due to the watch on the old directory not being removed properly, so when the package tries to create a watch on the new directory it thinks it is already monitoring it and so throws an error and does not create the new watch. This will hopefully one day be resolved by the maintainers of the package, but there are issues relating to this bug on the github for the package which are over a year old, so this fix may not come any time soon. Alternatively there may be some kind of workaround, but I was unable to find or come up with one which doesn't involve rewriting a large amount of functionality which is provided by the package. Another possible solution would be to abandon the package and interact directly with inotify instead, by executing commands through python with the subprocess module or similar. Perhaps the optimal solution would be to fork the inotify repository, fix the bug and submit a pull request with the fix, but I deemed this to be beyond the scope of this task. 

Secondly, the initialisation process could be improved by detecting the differences between the source and destination folders at startup and sending only the necessary updates to get them synchronised. This would remove the need for the destination folder to be empty at startup. This could be achieved to an extent by simply having the server send a directory listing at startup, but this does not account for differences in the content of the files. In order to detect such differences, the server would need to send every file in its entirety so that a byte-by-byte comparison between the copies of the files on the client and those on the server could be made, which is then no more efficient than just sending the contents of the client folder. A possible alternative would be to hash every file and compare the hashes instead. This would involve less data being sent over the network, but would be computationally expensive for both client and server, especially with large files. 

Finally, the process of synchronising changes to the content of a file could be optimised by detecting which bytes in the file have changed and then sending only those bytes, along with sufficient information for the server to update the bytes at the correct positions. This could be done by keeping a cache of file contents, and then comparing the contents of files which are updated with their cached versions to find the locations of changes. After that, send the updates and update the cached files. This could greatly reduce the volume of data transfer when small changes are made to large files, but would increase the storage or memory requirements of the application depending on how the cache is implemented.

## Conclusion
This was a fun task, which I ended up spending around 20 hours on in total including the time spent doing research and such (a little over the 3 hours suggested). I'd defintely like to come back to it at some point to see if I can sort out the issues I mentioned in the previous section.
