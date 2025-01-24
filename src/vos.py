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
        self.kernel.create_process("kernel", self.proc_msg("kernel"), user="kernel", system=True)
        print("Kernel: Starting VirtualFS...")
        self.kernel.create_process("filesystem", self.proc_msg("filesystem"), user="kernel", system=True)
        print("Kernel: Starting VirtualShell...")
        self.kernel.create_process("shell", self.proc_msg("shell"), user="kernel", system=True)

    def proc_msg(self, proc):
        self.kernel.execute_process(proc)
        print(f"{proc} Running")
        if proc == "shell":
            self.shell.start()

    def run(self):
        print("Starting vOS...")

        # Let the shell process run and wait for exit
        print("vOS running. Type 'exit' to shut down.")
        while True:
            # Check if the shell process is still running
            shell_process = next((p for p in self.kernel.list_processes() if p["name"] == "shell"), None)
            if not shell_process or shell_process["status"] != "running":
                break  # Exit the loop once the shell process finishes
            else:
                VirtualShell.start(self.shell)
            time.sleep(1)  # Check every second

        # Once 'exit' is called, shutdown the kernel and the system
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
