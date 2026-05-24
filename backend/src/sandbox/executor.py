import subprocess
import tempfile
import os

def run_code(code: str, timeout=2):
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "main.py")

        with open(file_path, "w") as f:
            f.write(code)

        try:
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {"error": "Timeout"}