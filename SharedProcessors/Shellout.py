import subprocess
import shlex
from autopkglib import Processor, ProcessorError  # Import AutoPkg's base classes

__all__ = ["Shellout"]

class Shellout(Processor):
    """
    A processor for executing shell commands with a timeout.
    """
    input_variables = {
        "command": {
            "required": True,
            "description": "The shell command to execute.",
        },
        "timeout": {
            "required": False,
            "description": "Timeout for the shell command in seconds. Defaults to 30.",
        },
        "live_output": {
            "required": False,
            "description": "Whether to display the command output live. Defaults to False.",
        },
    }
    output_variables = {
        "stdout": {
            "description": "The standard output of the shell command.",
        },
        "stderr": {
            "description": "The standard error of the shell command.",
        },
        "return_code": {
            "description": "The return code of the shell command.",
        },
    }

    def execute_shell_command(self, command, timeout):
        """
        Executes a shell command with a timeout and optional live output.

        Args:
            command (str): The shell command to execute.
            timeout (int): The timeout in seconds.
            live_output (bool): Whether to display the output live.

        Returns:
            tuple: stdout, stderr, return_code
        """
        try:
            process = subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True,
            )
            return (process.stdout.strip(), process.stderr.strip(), process.returncode)

        except subprocess.TimeoutExpired:
            raise ProcessorError(f"Command '{command}' timed out after {str(timeout)} seconds.")
        except subprocess.CalledProcessError as e:
            raise ProcessorError(f"Command '{command}' failed with return code {str(e.returncode)}. Output: {e.output}")
        except Exception as e:
            raise ProcessorError(f"Unexpected error occurred: {e}")

    def main(self):
        command = self.env.get("command")
        timeout = self.env.get("timeout", 30)  # Default timeout is 30 seconds

        if not command:
            raise ProcessorError("No command specified.")

        timeout = int(timeout)

        self.output(f"Executing command: {command} with timeout {str(timeout)}")  # Convert timeout to string

        stdout, stderr, return_code = self.execute_shell_command(command, timeout)

        # Set the outputs
        self.env["stdout"] = stdout
        self.env["stderr"] = stderr
        self.env["return_code"] = return_code

        self.output(f"Command executed successfully. Return code: {return_code}")


if __name__ == "__main__":
    processor = Shellout()
    processor.execute_shell()
