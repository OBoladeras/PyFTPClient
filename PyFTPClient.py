import os
import sys
import time
import ftplib
import getpass
import readline

version = "1.5"
url = "https://github.com/OBoladeras"

RESET = '\x1b[0m'
RED = '\x1b[31m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'
BLUE = '\x1b[34m'
MAGENTA = '\x1b[35m'
CYAN = '\x1b[36m'
WHITE = '\x1b[37m'

BOLD = '\x1b[1m'
RESET_BOLD = '\x1b[22m'


ftp = None
passive = True
localDir = False
ftpUsername = ""
cwd = os.getcwd()
command_history = []
commands = ['ls', 'cd', 'pwd', 'get', 'put', 'rm', 'mkdir', 'rmdir', 'passive', 'chmod', 'rename', 'size', 'status',
            'open', 'history', 'local', 'whoami', 'source', 'help']


def create_ftp_connection():
    global ftp
    ftp = ftplib.FTP()

    try:
        host = sys.argv[1]

        if host == "help" or host == "-h" or host == "-help" or host == "-?" or host == "--help":
            print_help()
            exit()
    except IndexError:
        print(
            f"Specify host address, example:\n\t{GREEN}python3{RESET} {__file__.split('/')[-1]} {MAGENTA}192.168.0.1 21{RESET}")
        exit()

    try:
        port = sys.argv[2]
    except:
        port = 21

    try:
        ftp.connect(host, port)
        print(f'Connected to FTP server at {MAGENTA}{host}:{port}{RESET}')
    except:
        print(f'{RED}Could not connect to FTP server{RESET}')
        exit()

    while True:
        try:
            global ftpUsername
            ftpUsername = input(f'\nEnter FTP username: ')
            ftp_password = getpass.getpass(prompt=f'Enter FTP password: ')

            ftp.login(ftpUsername, ftp_password)
            ftp.set_pasv(passive)
            print(f'\n{GREEN}Logged in as {ftpUsername}{RESET}')
            break

        except ftplib.error_perm as e:
            print(f"{YELLOW}Incorrect credentials{RESET}")

        except KeyboardInterrupt:
            print(f'\n{RED}KeyboardInterrupt{RESET}')
            exit()

        except Exception as e:
            print(f"{RED}Error: {RESET}{e}")


    return host


def main():
    IP = create_ftp_connection()

    readline.set_completer(completer)
    readline.parse_and_bind('tab: complete')
    readline.set_pre_input_hook(prev_command_hook)

    while True:
        try:
            if localDir:
                directory = cwd
                directory = directory.replace(f'/home/{os.environ.get("USER")}', '~')
            else:
                directory = ftp.pwd()
                directory = directory.replace(f'/home/{ftpUsername}', '~')
            request = input(
                f'{GREEN}({BOLD}{MAGENTA}{ftpUsername}@{IP}{GREEN}{RESET_BOLD})-[{WHITE}{directory}{GREEN}]: {RESET}')

            if request in ['exit', 'quit', 'close']:
                print(f"\nSee you next time!")
                ftp.quit()
                break
            else:
                if request is not None:
                    command_history.append(request)
                request = request.split()
                handle_request(ftp, request)

        except IndexError:
            pass

        except ftplib.error_temp:
            print(f"{YELLOW}Timeout, login again{RESET}")
            ftp.quit()
            IP = create_ftp_connection()

        except ftplib.error_proto as e:
            print(f"{RED}Broken Pipe Error: {RESET}\nTry logging in again")
            ftp.quit()
            IP = create_ftp_connection()

        except KeyboardInterrupt:
            print(f'\n\n{RED}KeyboardInterrupt{RESET}')
            print(f"See you next time!")
            ftp.quit()
            exit()

        except Exception as e:
            print(f'{RED}Error:{RESET} {e}')


def handle_request(ftp, request):
    if request[0] == 'local':
        if request[1] == 'cd':
            change_directory(request[2:])
        else:
            output = run_command(request[1:])

            if output is not None:
                print(output)

    else:
        if request[0] == 'ls':
            for line in get_remote_item_list_ftp(request):
                print(line)

        elif request[0] == 'cd':
            if len(request) > 1:
                try:
                    directory = " ".join(request[1:])
                    ftp.cwd(directory)
                    print(f'Directory successfully changed')
                except:
                    print(f"{RED}Invalid directory{RESET}")

            else:
                print(f"{YELLOW}WARNING:{RESET} You must specify a directory")

        elif request[0] == 'pwd':
            directory = ftp.pwd()
            print(f'Remote directory: `{CYAN}{str(directory)}{RESET}`')

        elif request[0] == 'get':
            if len(request) == 3:
                download_ftp(request[1], request[2])
            if len(request) == 2:
                download_ftp(request[1], cwd)

        elif request[0] == 'put':
            upload_ftp(request)

        elif request[0] == 'rm':
            if len(request) >= 2:
                file_path = " ".join(request[1:])
                try:
                    ftp.delete(file_path)
                    print(f"File `{CYAN}{file_path}{RESET}` removed")

                except Exception as e:
                    print(f"{RED}Error: {RESET}{e}")
            else:
                print(f"{YELLOW}WARNING:{RESET} You must specify a file")

        elif request[0] == 'mkdir':
            if len(request) > 1:
                try:
                    directory = " ".join(request[1:])
                    ftp.mkd(directory)
                    print(f"Directory `{CYAN}{directory}{RESET}` created in `{CYAN}{ftp.pwd()}{RESET}`")
                except Exception as e:
                    print(f"{RED}Error while creating directory: {e}{RESET}")
            else:
                print(f"{YELLOW}WARNING:{RESET} You must specify a directory")

        elif request[0] == 'rmdir':
            if len(request) > 1:
                try:
                    directory = " ".join(request[1:])
                    ftp.rmd(directory)
                    print(f"Directory `{CYAN}{directory}{RESET}` removed")

                except Exception as e:
                    print(f"{RED}Error: {RESET}{e}")
            else:
                print(f"{YELLOW}WARNING:{RESET} You must specify a directory")

        elif request[0] == 'open':
            if len(request) > 1:
                try:
                    path = " ".join(request[1:])
                    open_file_from_ftp(ftp, path)
                except Exception as e:
                    print(f"{RED}Error: {RESET}{e}")
            else:
                print(f"{YELLOW}WARNING:{RESET} You must specify a file")

        elif request[0] == 'history':
            for command in command_history:
                print(command)

        elif request[0] == 'whoami':
            print(f"You logged in as {GREEN}{ftpUsername}{RESET}")

        elif request[0] == 'help':
            print_help()

        elif request[0] == 'source':
            global localDir

            if len(request) == 2:
                if request[1] == 'local':
                    localDir = True
                elif request[1] in ['ftp', 'remote']:
                    localDir = False
                else:
                    print(f"{YELLOW}Unknown command {RESET}'{GREEN}{request[1]}{RESET}'")
            elif len(request) == 1:
                if localDir:
                    localDir = False
                else:
                    localDir = True
            else:
                print(f"{YELLOW}WARNING{RESET} Need 1 or 0 arguments, got {len(request)}{RESET}")

        elif request[0] in ['passive', 'passive?']:
            global passive
            def check_passive():
                if passive:
                    print(f"Passive mode is {GREEN}enabled{RESET}")
                else:
                    print(f"Passive mode is {YELLOW}disabled{RESET}")
            

            if len(request) == 2:
                if request[1] == '?':
                    check_passive()
            else:
                if request[0] == 'passive?':
                    check_passive()
                else:
                    if passive:
                        try:
                            passive = False
                            ftp.set_pasv(passive)
                            print(f"Passive mode {YELLOW}disabled{RESET}")
                        except Exception as e:
                            print(f"{RED}Error disabling passive mode: {RESET}{e}")
                    else:
                        try:
                            passive = True
                            ftp.set_pasv(passive)
                            print(f"Passive mode {GREEN}enabled{RESET}")
                        except Exception as e:
                            print(f"{RED}Error entering passive mode: {RESET}{e}")

        elif request[0] == 'chmod':
            if len(request) == 3:
                try:
                    ftp.sendcmd(f"SITE CHMOD {request[1]} {request[2]}")
                    print(f"File `{CYAN}{request[2]}{RESET}` permissions changed ({MAGENTA}{request[1]}{RESET})")
                except Exception as e:
                    print(f"{RED}Error: {RESET}{e}")
            else:
                print(f"{YELLOW}WARNING{RESET} Need 3 arguments, got {len(request)}{RESET}")

        elif request[0] == 'rename':
            if len(request) == 3:
                try:
                    ftp.rename(request[1], request[2])
                    print(f"Renamed from `{CYAN}{request[1]}{RESET}` to `{CYAN}{request[2]}{RESET}`")
                except Exception as e:
                    print(f"{RED}Error: {RESET}{e}")
            else:
                print(f"{YELLOW}WARNING{RESET} Need 3 arguments, got {len(request)}{RESET}")

        elif request[0] == 'size':
            if len(request) == 2:
                try:
                    size = ftp.size(request[1])

                    if size > 1048576:
                        size = round(size / 1048576, 2)
                        print(f"File `{CYAN}{request[1]}{RESET}` size: {size} MB")
                    else:
                        print(f"File `{CYAN}{request[1]}{RESET}` size: {size/1024:.2f} KB")
                except Exception as e:
                    print(f"{RED}Error: {RESET}{e}")
            else:
                print(f"{YELLOW}WARNING{RESET} Need 2 arguments, got {len(request)}{RESET}")

        elif request[0] == 'status':
            if len(request) == 1:
                try:
                    status = ftp.sendcmd("STAT")
                    status = status.split("\n")

                    text = ""
                    i = 0

                    print(f"FTP Server status: {text}")
                    for line in status:
                        if i != 0 and i != len(status) - 1:
                            print(line)
                        i += 1

                except Exception as e:
                    print(f"{RED}Error: {RESET}{e}")
            else:
                print(f"{YELLOW}WARNING{RESET} Need 1 argument, got {len(request)}{RESET}")

        else:
            print(f"{YELLOW}Unknown command {RESET}'{GREEN}{request[0]}{RESET}'")
            print(f"Try '{GREEN}help{RESET}' for more information")


def completer(text, state):
    line = readline.get_line_buffer()
    words = line.split()

    if ((not line or len(words) == 1) and not line.endswith(' ')):
        options = [cmd for cmd in commands if cmd.startswith(text)]
    else:
        # First option case (file-directory)
        if len(words) == 1 or (len(words) == 2 and not line.endswith(' ')):
            # Remote file
            if words[0] in ['cd', 'get', 'rm', 'rmdir', 'open']:
                if words[0] in ['rm', 'open']:
                    files = get_remote_item_list_ftp(['-f'])
                elif words[0] in ['cd', 'rmdir']:
                    files = get_remote_item_list_ftp(['-d'])
                else:
                    files = get_remote_item_list_ftp([])

            # Local file
            if words[0] in ['put', 'local']:
                files = os.listdir(cwd)

        # Second option case (file-directory)
        else:
            # Local directory
            if words[0] == 'get':
                files = os.listdir(cwd)
                files = [f for f in files if os.path.isdir(
                    os.path.join(cwd, f))]

            # Remote file
            elif words[0] == 'put':
                files = get_remote_item_list_ftp(['-f'])

        if not files:
            files = os.listdir(cwd)

        if not text:
            options = [file for file in files]
        else:
            options = [file for file in files if file.startswith(text)]

    if state < len(options):
        return options[state]
    else:
        return None


def prev_command_hook():
    def get_previous_command():
        if command_history:
            return command_history.pop()
        return ''

    def get_next_command():
        if command_history:
            return command_history[-1]
        return ''

    key = readline.get_key()
    if key == '\x1b[A':  # Up arrow key
        prev_command = get_previous_command()
        readline.insert_text(prev_command)
    elif key == '\x1b[B':  # Down arrow key
        next_command = get_next_command()
        readline.insert_text(next_command)

    readline.redisplay()


# FTP commands
def change_directory(directory):
    global cwd

    if len(directory) == 0:
        dir_path = os.path.expanduser("~")
    else:
        dir_path = os.path.join(*directory)

    try:
        os.chdir(dir_path)
        cwd = os.getcwd()
    except Exception as e:
        print(f"{RED}Error: {RESET}{e}")


def get_remote_item_list_ftp(request):
    directory_listing = []

    if len(request) == 2:
        if request[1] == '-lf' or request[1] == '-fl':
            request.append('-l')
            request.append('-f')
        if request[1] == '-ld' or request[1] == '-dl':
            request.append('-l')
            request.append('-d')

    if '-l' in request:
        ftp.retrlines('LIST', directory_listing.append)
        if '-f' in request:
            listing = [name for name in directory_listing if ftp.nlst(name.split(' ')[-1]) != [name]]
        elif '-d' in request:
            listing = [name for name in directory_listing if ftp.nlst(name.split(' ')[-1]) == [name]]
        else:
            listing = directory_listing

    else:
        ftp.retrlines('NLST', directory_listing.append)

        if '-d' in request:
            listing = [name for name in directory_listing if ftp.nlst(name) != [name]]
        elif '-f' in request:
            listing = [name for name in directory_listing if ftp.nlst(name) == [name]]
        else:
            listing = directory_listing

    return listing


def download_ftp(remote_file_path, local_file_path):
    try:
        total_size = ftp.size(remote_file_path)
        downloaded_size = 0

        if os.path.isdir(local_file_path):
            local_file_path = os.path.join(local_file_path, remote_file_path)

        start_time = time.time()


        with open(local_file_path, 'wb') as local_file:

            def callback(data):
                nonlocal downloaded_size
                downloaded_size += len(data)
                local_file.write(data)
                print_progress(downloaded_size)

            def print_progress(progress):
                percentage = round((progress / total_size) * 100, 2)

                total_mb = total_size / 1048576

                elapsed_time = time.time() - start_time
                download_speed = progress / elapsed_time / 1048576

                progress_bar_filled = '=' * int(percentage / 2)
                progress_bar_remaining = '-' * (50 - int(percentage / 2))

                text = f"[{GREEN}{progress_bar_filled}{RESET}{progress_bar_remaining}] {percentage:.2f}%  of {total_mb:.2f} MB  [{download_speed:.2f} MB/s]"
                if percentage == total_mb:
                    print('\r' + ' ' * len(text) + '\r', end='', flush=True)
                    print(text, flush=True)
                else:
                    print('\r' + ' ' * len(text) + '\r', end='', flush=True)
                    print(text, end='', flush=True)

            ftp.retrbinary(f"RETR {remote_file_path}", callback)
            print("")

        download_time = time.time() - start_time

        if download_time < 60:
            print(f"File '{CYAN}{remote_file_path}{RESET}' downloaded to '{CYAN}{local_file_path}{RESET}' in {download_time:.2f} seconds")
        else:
            download_time = format_time(download_time)
            print(f"File '{CYAN}{remote_file_path}{RESET}' downloaded to '{CYAN}{local_file_path}{RESET}' in {download_time}")

    except KeyboardInterrupt:
        print(f"{CYAN}Download interrupted by user.{RESET}")
        exit()
        # Handle this exception
        if input(f"\n{YELLOW} !!! Are you sure you want to exit?  !!! {RESET}(y/n) ") == 'y':
            print("Download interrupted by user.")
            os.remove(local_file_path)
        else:
            print("Retrying...")
            download_ftp(remote_file_path, local_file_path)

    except FileNotFoundError:
        print(
            f"{RED}Error: {RESET}Local directory '{CYAN}{local_file_path}{RESET}' not found.")

    except Exception as e:
        print(f"{RED}Error during download: {RESET}{e}")


def upload_ftp(request):
    cwd = ftp.pwd()

    try:
        if len(request) == 3:
            ftp.cwd(request[2])
    except Exception as e:
        print(f"{RED}Error: {RESET}{e}")

    try:
        globalProgress = 0
        local_file_path = request[1]
        total_size = os.path.getsize(local_file_path)

        start_time = time.time()

        def progress_callback(data):
            nonlocal globalProgress
            globalProgress += len(data)
            percentage = round((globalProgress / total_size) * 100, 2)

            elapsed_time = time.time() - start_time
            upload_speed = globalProgress / elapsed_time / 1048576

            total_mb = total_size / 1048576
            progress_bar_filled = '=' * int(percentage / 2)
            progress_bar_remaining = '-' * (50 - int(percentage / 2))

            text = f"[{GREEN}{progress_bar_filled}{RESET}{progress_bar_remaining}] {percentage:.2f}%  of {total_mb:.2f} MB  [{upload_speed:.2f} MB/s]"
            if globalProgress == total_size:
                print('\r' + ' ' * len(text) + '\r', end='', flush=True)
                print(text, flush=True)
            else:
                print('\r' + ' ' * len(text) + '\r', end='', flush=True)
                print(text, end='', flush=True)

        with open(local_file_path, 'rb') as local_file: # 8192
            ftp.storbinary(f"STOR {os.path.basename(local_file_path)}", local_file, blocksize=8192, callback=progress_callback)
    
        upload_time = time.time() - start_time

        if upload_time < 60:
            print(f"File '{CYAN}{local_file_path}{RESET}' uploaded to '{CYAN}{ftp.pwd()}{RESET}' in {upload_time:.2f} seconds")
        else:
            upload_time = format_time(upload_time)
            print(f"File '{CYAN}{local_file_path}{RESET}' uploaded to '{CYAN}{ftp.pwd()}{RESET}' in {upload_time}")

    except KeyboardInterrupt:
        print(f"{CYAN}Download interrupted by user.{RESET}")
        exit()
        # Handle this exception
        if input(f"\n{YELLOW} !!! Are you sure you want to exit? !!! {RESET}(y/n) ") == 'y':
            print("Download interrupted by user.")
            ftp.delete(local_file_path)
        else:
            print("Retrying...")
            upload_ftp(request)

    except FileNotFoundError:
        print(f"{RED}Error: {RESET}Local file '{local_file_path}' not found.")

    except Exception as e:
        print(f"{RED}Error: {RESET}{e}")

    finally:
        ftp.cwd(cwd)


def open_file_from_ftp(ftp, remote_file_path):
    try:
        data = bytearray()
        ftp.retrbinary(f"RETR {remote_file_path}",
                       callback=lambda x: data.extend(x))
        print(f"File '{CYAN}{remote_file_path}{RESET}' contents:\n")
        print(data.decode())

    except FileNotFoundError:
        print(
            f"{RED}Error:{RESET} Remote file '{CYAN}{remote_file_path}{RESET}' not found.")

    except Exception as e:
        print(f"{RED}Error: {RESET}{e}")


def print_help():
    print(f"{BOLD}PyFTPClient {RESET}{version} ( {url} )")

    print(f"\nCREATE CONNECTION:")
    print(f"   {GREEN}python3 {RESET}{__file__.split('/')[-1]} [{MAGENTA}@IP{RESET}] [{MAGENTA}port{RESET}]: Connect to the remote FTP server.")
    print(f"\t - If port is not specified, the default {MAGENTA}port 21{RESET} is used.")

    print(f"\nLOCAL SHELL:")
    print(f"   {GREEN}local{RESET} [{GREEN}command{RESET}]: Run a local shell command and print the output.")
    print(f"   {GREEN}local cd {RESET}[{CYAN}directory{RESET}]: Change the current local directory.")

    print("\nFTP COMMANDS:")
    print(f"   {GREEN}ls {RESET}[{GREEN}-l{RESET}] [{GREEN}-d{RESET}] [{GREEN}-f{RESET}]: List files and directories in the remote FTP server.")
    print(f"\t- The combination of options is possible like [{GREEN}-lf{RESET}].")
    print(f"{GREEN}\t-l{RESET}: Long format listing.")
    print(f"{GREEN}\t-d{RESET}: Show only directories.")
    print(f"{GREEN}\t-f{RESET}: Show only files.")
    print(f"   {GREEN}cd {RESET}[{CYAN}directory{RESET}]: Change the current remote FTP directory.")
    print(f"   {GREEN}pwd{RESET}: Print the current remote FTP directory.")
    print(f"   {GREEN}get {RESET}[{CYAN}remote_file{RESET}] {RESET}[{CYAN}local_file{RESET}]: Download a file from the remote FTP server to the local machine.")
    print(f"\t- If {RESET}[{CYAN}local_file{RESET}] is not specified, the file will be downloaded to the current local directory.")
    print(f"   {GREEN}put {RESET}[{CYAN}local_file{RESET}] {RESET}[{CYAN}remote_directory{RESET}]: Upload a local file to the remote FTP server.")
    print(f"\t- The file will be uploaded to the specified {RESET}[{CYAN}remote_directory{RESET}].")
    print(f"   {GREEN}rm {RESET}[{CYAN}file_path{RESET}]: Remove a file from the remote FTP server.")
    print(f"   {GREEN}mkdir {RESET}[{CYAN}directory{RESET}]: Create a directory on the remote FTP server.")
    print(f"   {GREEN}rmdir {RESET}[{CYAN}directory{RESET}]: Remove a directory from the remote FTP server.")
    print(f"   {GREEN}open {RESET}[{CYAN}remote_file{RESET}]: Open and display the contents of a remote file.")
    print(f"   {GREEN}history{RESET}: Display the command history.")
    print(f"   {GREEN}whoami{RESET}: Print the username of the currently logged in user.")
    print(f"   {GREEN}source{RESET} [{GREEN}local {RESET}/ {GREEN}remote{RESET}]: Change the directory showed in prompt.")
    print(f"\t- Options are not required, by default will toggle between local and remote.")
    print(f"   {GREEN}passive{RESET}[{GREEN}?{RESET}]: Switch between passive and active mode.")
    print(f"\t- If `{GREEN}?{RESET}` is writed it will show the current mode (passive or active).")
    print(f"   {GREEN}chmod{RESET} [{GREEN}option{RESET}] [{CYAN}remote_file{RESET}]: Change permission of a file.")
    print(f"\t- Option is the permission level: ({GREEN}+x{RESET}) or ({GREEN}700{RESET}).")
    print(f"   {GREEN}rename{RESET} [{CYAN}remote_file{RESET}] [{CYAN}new_name{RESET}]: Rename a file.")
    print(f"   {GREEN}size{RESET} [{CYAN}remote_file{RESET}]: Print the size of a file.")
    print(f"   {GREEN}status{RESET}: See the status of the remote FTP server.")
    print(f"   {GREEN}exit{RESET}: Exit the local shell.")
    print(f"   {GREEN}help{RESET}: Print this help message.")


# Command execution
def run_command(command):
    request = " ".join(command)

    try:
        output = os.popen(request).read().strip()
        if len(output) > 0:
            return output

    except Exception as e:
        print(f"{RED}An error occurred: {RESET}{e}")
        return None


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:.0f} hours and {minutes:.0f} minutes" if hours > 0 else f"{minutes:.0f} minutes"


if __name__ == '__main__':
    main()