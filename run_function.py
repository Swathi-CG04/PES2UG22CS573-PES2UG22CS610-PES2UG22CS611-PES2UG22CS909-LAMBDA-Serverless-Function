import os
import shutil
import subprocess
import uuid

def run_function(code: str, language: str, timeout: int):
    temp_id = uuid.uuid4().hex[:8]
    temp_dir = f"temp_{temp_id}"
    os.makedirs(temp_dir, exist_ok=True)

    # Determine filename and base image
    if language == "python":
        filename = "function.py"
        base_image = "func-python-base"
        run_cmd = ["python3", filename]
    elif language == "javascript":
        filename = "function.js"
        base_image = "func-js-base"
        run_cmd = ["node", filename]
    else:
        print("Unsupported language.")
        return

    # Write the function code to a file
    function_path = os.path.join(temp_dir, filename)
    with open(function_path, "w") as f:
        f.write(code)

    # Write the Dockerfile
    dockerfile_path = os.path.join(temp_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(f"""
FROM {base_image}
WORKDIR /app
COPY {filename} ./
CMD {str(run_cmd).replace("'", '"')}
""")

    # Build and run the container
    image_tag = f"{language}_func_{temp_id}"
    try:
        print(f"Building Docker image: {image_tag}")
        subprocess.run(["docker", "build", "-t", image_tag, "."], cwd=temp_dir, check=True)

        print("Running function in Docker container...")
        result = subprocess.run(
            ["docker", "run", "--rm", image_tag],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        print("Function Output:\n", result.stdout)
        if result.stderr:
            print("Function Error Output:\n", result.stderr)
    except subprocess.TimeoutExpired:
        print("Execution timed out.")
    except subprocess.CalledProcessError as e:
        print("Docker build/run failed:", e)
    finally:
        # Clean up: remove image and temp directory
        subprocess.run(["docker", "rmi", "-f", image_tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(temp_dir)

# Test run - Python
if __name__ == "__main__":
    python_code = '''
print("Starting function")
print("This is a test from a Python function.")
print("Ending function")
'''
    run_function(python_code, language="python", timeout=10)
