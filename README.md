 <h1 align=center>PyFTPClient 🚀</h1>
This Python script provides a simple FTP client that allows you to connect to a remote FTP server, perform various file and directory operations, and run local shell commands. The client provides a command-line interface and supports a range of FTP commands for interacting with the remote server.

## Usage 👨‍💻

To run the FTP client, execute the script using Python with the following command:
``` bash
python3 PyFTPClient.py [IP] [port]
```
- **IP**: The IP address of the remote FTP server.
- **port**: (Optional) The port number to connect to the FTP server. The default port is 21.

## Supported Commands ✅
### FTP Commands:
- **ls [-l] [-d] [-f]**: List files and directories in the remote FTP server.
        -l: Long format listing.
        -d: Show only directories.
        -f: Show only files.
        The combination of options is possible, e.g., -lf or -dl.
- **cd [directory]**: Change the current remote FTP directory.
- **pwd**: Print the current remote FTP directory.
- **get [remote_file] [local_file]**: Download a file from the remote FTP server to the local machine.
        If [local_file] is not specified, the file will be downloaded to the current local directory.
- **put [local_file] [remote_directory]**: Upload a local file to the remote FTP server.
        The file will be uploaded to the specified [remote_directory].
- **rm [file_path]**: Remove a file from the remote FTP server.
- **mkdir [directory]**: Create a directory on the remote FTP server.
- **rmdir [directory]**: Remove a directory from the remote FTP server.
- **open [remote_file]**: Open and display the contents of a remote file.
- **history**: Display the command history.
- **whoami**: Print the username of the currently logged-in user.
- **source [local / remote]**: Change the directory showed in prompt.  
        - Options are not required, by default will toggle between local and remote.
- **passive[?]**: Switch between passive and active mode.  
        - If `?` is writed it will show the current mode (passive or active).
- **chmod [permission] [remote_file]**: Change the permissions of the remote file.
- **rename [remote_file] [new_name]**: Set a new name to a remote file.
- **size [remote_file]**: Print the size of a file.
- **exit**: Exit the local shell.
- **help**: Print this help message.

### Local Shell:
- **local [command]**: Run a local shell command and print the output.
- **local cd [directory]**: Change the current local directory.

## Other Features: 🌟
- **Tab-completion**: The client supports tab-completion for commands and file/directory paths.
- **Command History**: The client keeps track of previously executed commands and allows you to access them using the up and down arrow keys.

## Updates: 🆕
- Source command added, now is possible to display local cwd or remote cwd
``` bash
(server@192.168.1.1)-[~]: source 
(server@192.168.1.1)-[~/projects/PyFTPClient]: 
```
- Progress bar added when download and upload files, also with file size and upload speed mesurements.

``` bash
(server@192.168.1.1)-[~/projects/PyFTPClient]: put PyFTPClient.py
[==================================================] 100.00%  of 0.02 MB  [4.92 MB/s]         
File 'PyFTPClient.py' uploaded to '/home/server' in 0.01 seconds
```

- Ability to enter passive and active mode
``` bash
(server@192.168.1.1)-[~]: passive?
Passive mode is enabled
(server@192.168.1.1)-[~]: passive
Passive mode disabled
```

- **New commands**
        - chmod
        - rename
        - size

### Future Features
- Ability to stop downloads and uploads without restarting
- Tab update when working with directories

## Dependencies 🛠️
This FTP client requires Python 3. The following libraries are used for various functionalities and are installed by default along with Python 3:
- **os**
- **sys**
 - **time**
- **ftplib**
- **getpass**
- **readline**

No additional installation is required for these libraries.


## Author ✍️
This FTP client is developed by OBoladeras and available on [GitHub](https://github.com/OBoladeras).

## License 📄
This FTP client is released under the MIT License. Feel free to use and modify it as per your needs.

## Note 📝
This FTP client is a basic implementation and may not cover all use cases or handle errors extensively. Use it at your discretion and ensure proper permissions and access rights for remote FTP operations.
