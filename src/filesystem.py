import os

class VirtualFS:
    def __init__(self, fs_file="fs_tree.txt"):
        self.fs_file = fs_file
        self.parsedFS = {}
        self.filesystem = {}
        self.load_filesystem()

    def load_filesystem(self):
        """Load or initialize the filesystem."""
        if not os.path.exists(self.fs_file):
            self.filesystem = {"/": {"type": "dir", "content": {}}}
            self.populate_from_current_directory(os.getcwd())
            self.save_filesystem()
        else:
            with open(self.fs_file, "r") as f:
                data = f.read()
                self.filesystem = self.parse_filesystem(data)

    def save_filesystem(self):
        """Save the virtual filesystem to the fs_tree.txt file."""
        with open(self.fs_file, "w") as f:
            f.write(self.serialize_filesystem(self.filesystem))

    def populate_from_current_directory(self, path):
        """Populate the virtual filesystem using the current directory."""
        for root, dirs, files in os.walk(path):
            rel_root = os.path.relpath(root, start=path).replace(os.sep, "/")
            virtual_root = "/" if rel_root == "." else f"/{rel_root}"
            for dir_name in dirs:
                self.create_directory(f"{virtual_root}/{dir_name}")
            for file_name in files:
                full_path = os.path.join(root, file_name)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.create_file(f"{virtual_root}/{file_name}", content)
                except UnicodeDecodeError:
                    with open(full_path, "rb") as f:
                        content = f.read()
                    self.create_file(f"{virtual_root}/{file_name}", content, is_binary=True)

    def get_current_directory_files(self, path):
        """List files and directories in the current directory."""
        return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) or os.path.isfile(os.path.join(path, f))]

    def parse_filesystem(self, data):
        """Parse the filesystem data from fs_tree.txt."""
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
        """Convert the filesystem into a string for storage."""
        output = []
        for key, value in fs.items():
            output.append(" " * indent + f"{key}:{value['type']}")
            if value["type"] == "dir":
                output.append(self.serialize_filesystem(value["content"], indent + 2))
        return "\n".join(output)

    def create_file(self, path, content, is_binary=False):
        """Add a file to the virtual filesystem."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        for d in dirs[:-1]:
            if d not in current or current[d]["type"] != "dir":
                raise FileNotFoundError(f"Directory '{d}' not found.")
            current = current[d]["content"]
        current[dirs[-1]] = {"type": "file", "content": content, "is_binary": is_binary}
        self.save_filesystem()

    def create_directory(self, path):
        """Add a directory to the virtual filesystem."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        for d in dirs:
            if d not in current:
                current[d] = {"type": "dir", "content": {}}
            elif current[d]["type"] != "dir":
                raise FileExistsError(f"'{d}' already exists as a file.")
            current = current[d]["content"]
        self.save_filesystem()

    def list_directory(self, path):
        """List the contents of a directory in the virtual filesystem."""
        dirs = path.strip("/").split("/")
        current = self.filesystem["/"]["content"]
        result = []
        result.append("Directories")
        for d in dirs[:-1]:
            if current[d]["type"] == "dir":
                result.append(d)
        return result

    def read_file(self, path):
        """Read a file from the virtual filesystem."""
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
        """Delete a file or directory from the virtual filesystem."""
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

    def file_exists(self, path):
        """Check if a file exists in the filesystem."""
        return path in self.filesystem and isinstance(self.filesystem[path], str)
