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
            "system": system,  # True if the process is critical and cannot be killed
            "start_time": time.monotonic(),  # Track when the process starts running
            "runtime": 0  # Total runtime in seconds
        })

    def list_processes(self):
        """List all processes with their name, status, owner, and runtime."""
        self.update_process_runtime()
        processes_list = []
        for process in self.processes:
            processes_list.append({
                "name": process["name"],
                "status": process["status"],
                "user": process["user"],
                "runtime": round(process["runtime"], 2)  # Rounded to 2 decimals
            })
        return processes_list

    def update_process_runtime(self):
        """Update the runtime of all running processes."""
        current_time = time.monotonic()
        for process in self.processes:
            if process["status"] == "running" and process["start_time"]:
                process["runtime"] = current_time - process["start_time"]

    def execute_process(self, name):
        """Execute a process by name."""
        for process in self.processes:
            if process["name"] == name:
                if process["status"] != "running":  # Prevent re-execution of system processes
                    process["status"] = "running"
                    process["start_time"] = time.monotonic()  # Set the process start time
                    try:
                        print(f'Executing process: {process["name"]}')
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
                    for i in self.processes:
                        print(".")
                        time.sleep(0.1)
#                    print(f"Process '{name}' owned by '{process['user']}' has been killed by '{user}'.")
                    self.processes.remove(process)
                    return True
        print(f"Process '{name}' not found.")
        return False

    def uptime(self):
        """Calculate uptime in seconds."""
        return round(time.monotonic() - self.start_time, 2)

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
        """Shutdown the kernel and all processes."""
        self.fs.save_filesystem()
        for process in list(self.processes):  # Use a copy to avoid modification during iteration
            self.kill_process(process["name"], "kernel")
        print("Kernel has shut down.")
