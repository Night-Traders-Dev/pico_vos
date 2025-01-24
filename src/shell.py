import time

class VirtualShell:
    def __init__(self, fs):
        self.fs = fs

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
        print("  kill [process_name]   - Kill a process by name")

    def execute_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        try:
            if cmd == "ls":
                path = args[0] if args else "/"
                # List directory contents using VirtualFS's method
                directory_contents = self.fs.list_directory(path)
                if directory_contents:
                    print("\n".join(directory_contents))
                else:
                    print(f"Error: Directory '{path}' not found.")
            elif cmd == "cat":
                path = args[0]
                # Read and display file content
                try:
                    content = self.fs.read_file(path)
                    print(content)
                except FileNotFoundError:
                    print(f"Error: File '{path}' not found.")
            elif cmd == "touch":
                path = args[0]
                # Create an empty file
                self.fs.create_file(path, content="", is_binary=False)
                print(f"File '{path}' created.")
            elif cmd == "mkdir":
                path = args[0]
                # Create a directory
                self.fs.create_directory(path)
                print(f"Directory '{path}' created.")
            elif cmd == "rm":
                path = args[0]
                # Delete a file or directory
                self.fs.delete(path)
                print(f"File/Directory '{path}' deleted.")
            elif cmd == "uptime":
                uptime = self.kernel.uptime()  # Assuming kernel has uptime method
                print(f"vOS Uptime: {uptime:.2f} seconds")
            elif cmd == "ps":
                processes = self.kernel.list_processes()  # Assuming kernel has list_processes method
                for process in processes:
                    print(f"Process: {process['name']}, Status: {process['status']}")
            elif cmd == "kill":
                process_name = args[0]
                if process_name == "shell" or process_name == "kernel" or process_name == "filesystem":
                    print(f"Cannot kill critical system process: {process_name}")
                else:
                    if self.kernel.kill_process(process_name):  # Assuming kernel has kill_process method
                        print(f"Process {process_name} killed.")
            else:
                print(f"Unknown command: {cmd}")
        except IndexError:
            print("Error: Missing arguments.")
        except Exception as e:
            print(f"Error: {e}")

    def exit_vos(self):
        print("vOS will now shut down...")
        self.kernel.shutdown()  # Assuming kernel has shutdown method
        time.sleep(5)  # Wait for 5 seconds before exiting
        exit(0)  # Exit the Python script completely
