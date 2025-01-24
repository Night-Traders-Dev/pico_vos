import os

class VirtualFS:
    def __init__(self, fs_file="fs_tree.txt"):
        self.fs_file = fs_file
        self.filesystem = {}
        self.load_filesystem()

    def load_filesystem(self):
        """Load or initialize the filesystem from the current directory."""
        if self.fs_file not in os.listdir():
            # If fs_tree.txt doesn't exist, initialize it
            self.filesystem = {"/": {"type": "dir", "content": {}}}
            self.populate_from_current_directory(os.getcwd())
            self.save_filesystem()  # Save the populated filesystem to fs_tree.txt
        else:
            # If fs_tree.txt exists, load and verify contents
            with open(self.fs_file, "r") as f:
                data = f.read()
                self.filesystem = self.parse_filesystem(data)

            # Verify that the contents of the filesystem match the current directory
            self.verify_and_sync_filesystem(os.getcwd())

    def save_filesystem(self):
        """Save the virtual filesystem to the fs_tree.txt file."""
        with open(self.fs_file, "w") as f:
            f.write(self.serialize_filesystem(self.filesystem))                                      

    def populate_from_current_directory(self, path):
        """Recursively populate the virtual filesystem from the current directory."""
        for root, dirs, files in os.walk(path):                                                      
            # Create directories
            for dir_name in dirs:
                full_dir_path = os.path.join(root, dir_name)
                virtual_path = os.path.relpath(full_dir_path, start=os.getcwd()).replace(os.sep, "/")
                self.create_directory("/" + virtual_path)

            # Create files
            for file_name in files:
                full_file_path = os.path.join(root, file_name)
                virtual_path = os.path.relpath(full_file_path, start=os.getcwd()).replace(os.sep, "/")
                try:
                    with open(full_file_path, "r", encoding="utf-8") as f:
                        content = f.read()  # Try reading the file as text (UTF-8)
                    self.create_file("/" + virtual_path, content)
                except UnicodeDecodeError:
                    # If UTF-8 decoding fails, treat the file as binary
                    with open(full_file_path, "rb") as f:
                        content = f.read()  # Read the file as bytes
                    self.create_file("/" + virtual_path, content, is_binary=True)

    def verify_and_sync_filesystem(self, path):
        """Verify and sync the virtual filesystem with the current directory's structure."""
        current_files = self.get_current_directory_files(path)
        virtual_files = self.list_directory("/")  # List of files in the virtual filesystem (root dir)

        # Sync files and directories
        for virtual_path in virtual_files:
            if virtual_path not in current_files:
                # Remove files or directories that no longer exist in the current directory
                self.delete("/" + virtual_path)

        for current_path in current_files:
            if current_path not in virtual_files:
                # Add files or directories that exist in the current directory but not in the virtual filesystem
                full_path = os.path.join(path, current_path)
                if os.path.isdir(full_path):
                    self.create_directory("/" + current_path)
                else:
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        self.create_file("/" + current_path, content)
                    except UnicodeDecodeError:
                        with open(full_path, "rb") as f:
                            content = f.read()
                        self.create_file("/" + current_path, content, is_binary=True)

    def get_current_directory_files(self, path):
        """Get a list of files and directories in the current directory (non-recursive)."""
        return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) or os.path.isfile(os.path.join(path, f))]

    def parse_filesystem(self, data):
        """Parse the filesystem data from the text file."""
        fs = {}
        lines = data.strip().split("\n")
        stack = [fs]
        for line in lines:
            indent = len(line) - len(line.lstrip(" "))
            key, value = line.strip().split(":")
            node = {"type": value, "content": {} if value == "dir" else ""}
            while len(stack) > indent + 1:
                stack.pop()
            stack[-1][key] = node
            if value == "dir":
                stack.append(node["content"])
        return fs

    def serialize_filesystem(self, fs, indent=0):
        """Serialize the filesystem to a string format."""
        output = []
        for key, value in fs.items():
            output.append(" " * indent + f"{key}:{value['type']}")
            if value["type"] == "dir":
                output.append(self.serialize_filesystem(value["content"], indent + 2))
        return "\n".join(output)

    def create_file(self, path, content, is_binary=False):
        """Create a file at the given path with the provided content."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        for d in dirs[:-1]:
            if d not in current or current[d]["type"] != "dir":
                raise FileNotFoundError(f"Directory '{d}' not found.")
            current = current[d]["content"]
        current[dirs[-1]] = {"type": "file", "content": content, "is_binary": is_binary}
        self.save_filesystem()

    def create_directory(self, path):
        """Create a directory at the given path."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        for d in dirs:
            if d not in current:
                current[d] = {"type": "dir", "content": {}}
            elif current[d]["type"] != "dir":
                raise FileExistsError(f"'{d}' already exists as a file.")
            current = current[d]["content"]
        self.save_filesystem()

    def list_directory(self, path="/"):
        """List the contents of a directory."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        for d in dirs:
            if d not in current or current[d]["type"] != "dir":
                raise FileNotFoundError(f"Directory '{path}' not found.")
            current = current[d]["content"]
        return list(current.keys())

    def read_file(self, path):
        """Read the contents of a file."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        for d in dirs[:-1]:
            if d not in current or current[d]["type"] != "dir":
                raise FileNotFoundError(f"Directory '{d}' not found.")
            current = current[d]["content"]
        if dirs[-1] not in current or current[dirs[-1]]["type"] != "file":
            raise FileNotFoundError(f"File '{path}' not found.")
        return current[dirs[-1]]["content"]

    def delete(self, path):
        """Delete a file or directory at the given path."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        for d in dirs[:-1]:
            if d not in current or current[d]["type"] != "dir":
                raise FileNotFoundError(f"Directory '{d}' not found.")
            current = current[d]["content"]
        if dirs[-1] in current:
            del current[dirs[-1]]
        else:
            raise FileNotFoundError(f"Path '{path}' not found.")
        self.save_filesystem()
