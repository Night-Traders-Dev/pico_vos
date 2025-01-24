import time

class VirtualShell:
    def __init__(self, fs, kernel, user):
        self.fs = fs
        self.kernel = kernel
        self.user = user

    def start(self):
        print("vShell: Welcome to the Virtual Shell!")
        while True:
            command = input("$ ").strip()
            if command == "exit":
                print("Exiting vShell...")
                self.exit_vos()  # Gracefully shut down vOS
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
        print("  ps                    - List active processes")
        print("  kill [process_name]   - Kill a process by name (user restrictions apply)")

    def execute_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        try:
            if cmd == "ls":
                path = args[0] if args else "/"
                directory_contents = self.fs.list_directory(path)
                if directory_contents:
                    print("\n".join(directory_contents))
                else:
                    print(f"Error: Directory '{path}' not found.")
            elif cmd == "cat":
                path = args[0]
                try:
                    content = self.fs.read_file(path)
                    print(content)
                except FileNotFoundError:
                    print(f"Error: File '{path}' not found.")
            elif cmd == "touch":
                path = args[0]
                self.fs.create_file(path, content="", is_binary=False)
                print(f"File '{path}' created.")
            elif cmd == "mkdir":
                path = args[0]
                self.fs.create_directory(path)
                print(f"Directory '{path}' created.")
            elif cmd == "rm":
                path = args[0]
                self.fs.delete(path)
                print(f"File/Directory '{path}' deleted.")
            elif cmd == "uptime":
                uptime = self.kernel.uptime()
                print(f"vOS Uptime: {uptime:.2f} seconds")
            elif cmd == "ps":
                processes = self.kernel.list_processes()
                for process in processes:
                    print(f"Process: {process['name']}, Status: {process['status']}, User: {process.get('user', 'unknown')}")
            elif cmd == "kill":
                process_name = args[0]
                process = next((p for p in self.kernel.processes if p["name"] == process_name), None)
                if not process:
                    print(f"Process '{process_name}' not found.")
                elif process["user"] == "kernel":
                    print(f"Cannot kill kernel process: {process_name}")
                elif process["user"] == "root" and process_name not in ["shell", "filesystem"]:
                    print(f"Cannot kill root-level process: {process_name}")
                elif self.kernel.kill_process(process_name, self.user):
                    print(f"Process '{process_name}' killed.")
                else:
                    print(f"Failed to kill process '{process_name}'.")
            else:
                print(f"Unknown command: {cmd}")
        except IndexError:
            print("Error: Missing arguments.")
        except Exception as e:
            print(f"Error: {e}")

    def exit_vos(self):
        print("vOS will now shut down...")
        self.kernel.shutdown()
        time.sleep(1)  # Brief delay for graceful shutdown
        exit(0)
