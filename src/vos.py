import time
from filesystem import VirtualFS
from kernel import VirtualKernel
from shell import VirtualShell
import sys


class vOS:
    def __init__(self):
        print("Initializing vOS...")
        self.user = "user"
        self.fs = VirtualFS()
        self.kernel = VirtualKernel(self.fs)
        self.shell = VirtualShell(self.fs, self.kernel, self.user)

        # Register core system processes
        print("Starting Kernel Process...")
        self.kernel.create_process("kernel", lambda: None, user="kernel", system=True)

        print("Kernel: Starting VirtualFS...")
        self.kernel.create_process("filesystem", lambda: None, user="kernel", system=True)

        print("Kernel: Starting VirtualShell...")
        self.kernel.create_process("shell", self.shell.start, user="kernel", system=True)

    def run(self):
        print("Starting vOS...")
        print("vOS is running. Type 'exit' in the shell to shut down.")

        while True:
            # Check if the shell process is still running
            shell_process = next(
                (p for p in self.kernel.list_processes() if p["name"] == "shell"),
                None,
            )
            if not shell_process or shell_process["status"] != "running":
                break  # Exit once the shell process finishes
            else:
                VirtualShell.start(self.shell)
            time.sleep(1)  # Check the process status every second

        # Shutdown the kernel and the system after exiting the shell
        self.kernel.shutdown()
        print("vOS has shut down.")


if __name__ == "__main__":
    try:
        os_instance = vOS()
        os_instance.run()
    except SystemExit:
        print("vOS shutting down... Goodbye!")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nForced shutdown. Goodbye!")
        sys.exit(0)
