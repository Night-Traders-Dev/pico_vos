import time

class VirtualShell:
    def __init__(self, fs, kernel, user):
        self.fs = fs
        self.kernel = kernel
        self.user = user
        self.commands = {
            "help": self.show_help,
            "exit": self.exit_vos,
            "ls": self.ls,
            "cat": self.cat,
            "touch": self.touch,
            "mkdir": self.mkdir,
            "rm": self.rm,
            "uptime": self.uptime,
            "ps": self.ps,
            "kill": self.kill
        }

    def start(self):
        print("vShell: Welcome to the Virtual Shell!")
        while True:
            self.kernel.update_process_runtime()
            command = input("$ ").strip()
            parts = command.split()
            cmd = parts[0] if parts else ""
            args = parts[1:]

            # Check if the command is valid
            if cmd in self.commands:
                self.commands[cmd](args)
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for a list of commands.")

    def show_help(self, args=None):
        print("Available commands:")
        print("  help                  - Show this help message")
        print("  exit                  - Exit the shell and shut down vOS")
        print("  ls [path]             - List directory contents")
        print("  cat [path]            - Read a file")
        print("  touch [path]          - Create an empty file")
        print("  mkdir [path]          - Create a directory")
        print("  rm [path]             - Delete a file or directory")
        print("  uptime                - Show the uptime of vOS")
        print("  ps                    - List active processes with their status and runtime")
        print("  kill [process_name]   - Kill a process by name (user restrictions apply)")

    def ls(self, args):
        content = self.fs.list_directory("")
        print(content)

    def cat(self, args):
        if not args:
            print("Error: Missing file path.")
            return
        path = args[0]
        try:
            content = self.fs.read_file(path)
            print(content)
        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")

    def touch(self, args):
        if not args:
            print("Error: Missing file path.")
            return
        path = args[0]
        self.fs.create_file(path, content="")
        print(f"File '{path}' created.")

    def mkdir(self, args):
        if not args:
            print("Error: Missing directory path.")
            return
        path = args[0]
        self.fs.create_directory(path)
        print(f"Directory '{path}' created.")

    def rm(self, args):
        if not args:
            print("Error: Missing file or directory path.")
            return
        path = args[0]
        self.fs.delete(path)
        print(f"File/Directory '{path}' deleted.")

    def uptime(self, args):
        uptime = self.kernel.uptime()
        print(f"vOS Uptime: {uptime:.2f} seconds")

    def ps(self, args):
        processes = self.kernel.list_processes()
        if not processes:
            print("No active processes.")
        for process in processes:
            print(
                f"Process: {process['name']}, Status: {process['status']}, "
                f"User: {process['user']}, Runtime: {process['runtime']} seconds"
            )

    def kill(self, args):
        if not args:
            print("Error: Missing process name.")
            return
        process_name = args[0]
        if self.kernel.kill_process(process_name, self.user):
            print(f"Process '{process_name}' killed.")
        else:
            print(f"Failed to kill process '{process_name}'.")

    def exit_vos(self, args=None):
        print("vOS will now shut down...")
        self.kernel.shutdown()
        time.sleep(1)
        import sys
        sys.exit(0)
