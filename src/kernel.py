import time

class VirtualKernel:
    def __init__(self, fs):
        self.fs = fs
        self.processes = []
        self.start_time = time.monotonic()  # Record the start time of vOS

    # Process Management
    def create_process(self, name, func, user, system=False):
        """Create a process and add it to the process list."""
        self.processes.append({
            "name": name,
            "func": func,
            "status": "running" if system else "ready",
            "user": user,  # The owner of the process (kernel, root, user)
            "system": system  # True if the process is critical and cannot be killed
        })

    def list_processes(self):
        """List all processes with their name, status, and owner."""
        return [
            {"name": p["name"], "status": p["status"], "user": p["user"]}
            for p in self.processes
        ]

    def execute_process(self, name):
        """Execute a process by name."""
        for process in self.processes:
            if process["name"] == name:
                if process["status"] != "running":  # Prevent re-execution of system processes
                    process["status"] = "running"
                    try:
                        process["func"]()
                        if not process["system"]:
                            process["status"] = "completed"
                    except Exception as e:
                        process["status"] = "error"
                        print(f"Error in process '{name}': {e}")
                return
        print(f"Process '{name}' not found.")

    def kill_process(self, name, user):
        """Kill a process by name, enforcing user permissions."""
        for process in self.processes:
            if process["name"] == name:
                if process["user"] in ["kernel", "root"] and user == "user":
                    print(f"Permission denied: '{user}' cannot kill '{process['user']}' process '{name}'.")
                    return False
                if process["user"] == "kernel" and user == "root":
                    print(f"Permission denied: 'root' cannot kill kernel process '{name}'.")
                    return False
                if user == "kernel" or process["user"] == user or user == "root":
                    print(f"Process '{name}' owned by '{process['user']}' has been killed by '{user}'.")
                    self.processes.remove(process)
                    return True
        print(f"Process '{name}' not found.")
        return False

    def uptime(self):
        """Calculate uptime in seconds."""
        return time.monotonic() - self.start_time

    # Filesystem Management
    def create_file(self, path, content=""):
        self.fs.create_file(path, content)

    def create_directory(self, path):
        self.fs.create_directory(path)

    def delete(self, path):
        self.fs.delete(path)

    def list_directory(self, path="/"):
        return self.fs.list_directory(path)

    def read_file(self, path):
        return self.fs.read_file(path)

    def shutdown(self):
        self.fs.save_filesystem()
        self.kill_process("filesystem", "kernel")
        self.kill_process("shell", "kernel")
        self.kill_process("kernel", "kernel")
