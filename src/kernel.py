import time
import getpass

class VirtualKernel:
    def __init__(self, fs):
        self.fs = fs
        self.processes = []
        self.start_time = time.monotonic()  # Record the start time of vOS
        self.current_user = None

    def boot(self):
        """Handle login or account creation on boot."""
        print("Booting vOS...")
        if self.fs.file_exists("pass.file"):
            self.login()
        else:
            print("No users found. Create a new account.")
            self.create_account()

    def login(self):
        """Prompt the user to log in."""
        print("vOS Login:")
        while True:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ").strip()
            if self.authenticate_user(username, password):
                self.current_user = username
                print(f"Welcome, {username}!")
                break
            else:
                print("Invalid username or password. Please try again.")

    def create_account(self):
        """Create a new account and store it in pass.file."""
        print("Create a new account:")
        while True:
            username = input("New Username: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            if self.user_exists(username):
                print("Username already exists. Choose a different one.")
                continue
            password = getpass.getpass("New Password: ").strip()
            if not password:
                print("Password cannot be empty.")
                continue
            confirm_password = getpass.getpass("Confirm Password: ").strip()
            if password != confirm_password:
                print("Passwords do not match. Try again.")
                continue
            self.add_user(username, password)
            self.current_user = username
            print(f"Account created successfully! Welcome, {username}!")
            break

    def authenticate_user(self, username, password):
        """Check if the username and password match an entry in pass.file."""
        try:
            content = self.fs.read_file("pass.file")
            lines = content.splitlines()
            for line in lines:
                user_info = line.split(":")
                if len(user_info) == 2 and user_info[0] == username and user_info[1] == password:
                    return True
        except FileNotFoundError:
            pass
        return False

    def user_exists(self, username):
        """Check if a user already exists in pass.file."""
        try:
            content = self.fs.read_file("pass.file")
            lines = content.splitlines()
            for line in lines:
                if line.split(":")[0] == username:
                    return True
        except FileNotFoundError:
            pass
        return False

    def add_user(self, username, password):
        """Add a new user to pass.file."""
        user_entry = f"{username}:{password}\n"
        if self.fs.file_exists("pass.file"):
            content = self.fs.read_file("pass.file")
            content += user_entry
        else:
            content = user_entry
        self.fs.create_file("pass.file", content)

    # Process Management
    def create_process(self, name, func, user, system=False):
        self.processes.append({
            "name": name,
            "func": func,
            "status": "running" if system else "ready",
            "user": user,
            "system": system,
            "start_time": time.monotonic(),
            "runtime": 0
        })

    def list_processes(self):
        self.update_process_runtime()
        return [
            {
                "name": p["name"],
                "status": p["status"],
                "user": p["user"],
                "runtime": round(p["runtime"], 2)
            }
            for p in self.processes
        ]

    def update_process_runtime(self):
        current_time = time.monotonic()
        for process in self.processes:
            if process["status"] == "running" and process["start_time"]:
                process["runtime"] = current_time - process["start_time"]

    def kill_process(self, name, user):
        for process in self.processes:
            if process["name"] == name:
                if process["user"] in ["kernel", "root"] and user == "user":
                    print(f"Permission denied: '{user}' cannot kill '{process['user']}' process '{name}'.")
                    return False
                if process["user"] == "kernel" and user == "root":
                    print(f"Permission denied: 'root' cannot kill kernel process '{name}'.")
                    return False
                if user == "kernel" or process["user"] == user or user == "root":
                    self.processes.remove(process)
                    return True
        print(f"Process '{name}' not found.")
        return False

    def uptime(self):
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
        self.fs.save_filesystem()
        for process in list(self.processes):
            self.kill_process(process["name"], "kernel")
        print("Kernel has shut down.")
