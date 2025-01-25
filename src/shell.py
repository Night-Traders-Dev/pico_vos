import time

class VirtualShell:
    def __init__(self, fs, kernel, user):
        self.fs = fs
        self.kernel = kernel
        self.user = user

    def start(self):
        print("vShell: Welcome to the Virtual Shell!")
        while True:
            self.kernel.update_process_runtime()
            command = input("$ ").strip()
            if command == "exit":
                print("Exiting vShell...")
                self.exit_vos()
                break
            elif command == "help":
                self.show_help()
            else:
                self.execute_command(command)

    def show_help(self):
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

    def execute_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        try:
            if cmd == "ls":
                print(self.fs.filesystem)
            elif cmd == "cat":
                if not args:
                    print("Error: Missing file path.")
                    return
                path = args[0]
                try:
                    content = self.fs.read_file(path)
                    print(content)
                except FileNotFoundError:
                    print(f"Error: File '{path}' not found.")
            elif cmd == "touch":
                if not args:
                    print("Error: Missing file path.")
                    return
                path = args[0]
                self.fs.create_file(path, content="")
                print(f"File '{path}' created.")
            elif cmd == "mkdir":
                if not args:
                    print("Error: Missing directory path.")
                    return
                path = args[0]
                self.fs.create_directory(path)
                print(f"Directory '{path}' created.")
            elif cmd == "rm":
                if not args:
                    print("Error: Missing file or directory path.")
                    return
                path = args[0]
                self.fs.delete(path)
                print(f"File/Directory '{path}' deleted.")
            elif cmd == "uptime":
                uptime = self.kernel.uptime()
                print(f"vOS Uptime: {uptime:.2f} seconds")
            elif cmd == "ps":
                processes = self.kernel.list_processes()
                if not processes:
                    print("No active processes.")
                for process in processes:
                    print(
                        f"Process: {process['name']}, Status: {process['status']}, "
                        f"User: {process['user']}, Runtime: {process['runtime']} seconds"
                    )
            elif cmd == "kill":
                if not args:
                    print("Error: Missing process name.")
                    return
                process_name = args[0]
                if self.kernel.kill_process(process_name, self.user):
                    print(f"Process '{process_name}' killed.")
                else:
                    print(f"Failed to kill process '{process_name}'.")
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for a list of commands.")
        except IndexError:
            print("Error: Missing arguments.")
        except Exception as e:
            print(f"Error: {e}")

    def exit_vos(self):
        print("vOS will now shut down...")
        self.kernel.shutdown()
        time.sleep(1)  # Brief delay for graceful shutdown
        import sys
        sys.exit(0)
