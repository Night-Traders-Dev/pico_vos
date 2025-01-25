# Virtual OS(`vOS`)

A lightweight, command-line-based Virtual Shell (`vOS`) for a Virtual OS (vOS) with basic file system and kernel interaction. This project simulates a shell environment for managing files, directories, processes, and system state.

## Features

- **File Management**:
  - `ls [path]` — List directory contents.
  - `cat [path]` — View file content.
  - `touch [path]` — Create an empty file.
  - `mkdir [path]` — Create a directory.
  - `rm [path]` — Delete a file or directory.

- **Process Management**:
  - `ps` — List active processes with their status and runtime.
  - `kill [process_name]` — Terminate a process by name (user restrictions apply).

- **System Utilities**:
  - `uptime` — Display the system's uptime.
  - `help` — Show the list of available commands.
  - `exit` — Exit the shell and shut down the Virtual OS.

## Prerequisites

- Python 3.6 or higher
- A compatible file system (`fs`) and kernel (`kernel`) implementation to integrate with `vShell`.

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Night-Traders-Dev/pico_vos.git
cd vshell
```

### 2. Set Up the Environment
Ensure your project includes:
- A file system (`fs`) object with methods like `list_directory`, `read_file`, `create_file`, `create_directory`, and `delete`.
- A kernel (`kernel`) object with methods like `uptime`, `list_processes`, `kill_process`, and `shutdown`.

### 3. Run the Shell
Run `vOS` by executing:
```bash
python3 vos.py
```

## Usage

Once started, the shell prompts you with a `$` symbol for entering commands. Below is an example workflow:

1. **List contents of the root directory**:
   ```bash
   $ ls /
   ```

2. **Create a directory**:
   ```bash
   $ mkdir /new_directory
   ```

3. **Create an empty file**:
   ```bash
   $ touch /new_directory/file.txt
   ```

4. **View file contents**:
   ```bash
   $ cat /new_directory/file.txt
   ```

5. **List active processes**:
   ```bash
   $ ps
   ```

6. **Shut down the shell**:
   ```bash
   $ exit
   ```

## Extending the Shell

To add new commands or integrate additional system features:
1. Modify the `execute_command` method in `shell.py`.
2. Implement corresponding methods in the `fs` or `kernel` classes.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).

