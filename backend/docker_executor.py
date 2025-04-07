import subprocess
import uuid
import os

def execute_function(code: str, language: str, timeout: int = 5):
    temp_dir = f"temp_exec/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)

    if language == "python":
        file_name = "user_code.py"
        docker_image = "lambda-python"
        dockerfile_path = "./docker-images/python-base"
    elif language == "javascript":
        file_name = "user_code.js"
        docker_image = "lambda-js"
        dockerfile_path = "./docker-images/js-base"
    else:
        return {"error": "Unsupported language"}

    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, "w") as f:
        f.write(code)

    # Build image (only once ideally, you can cache)
    subprocess.run(["docker", "build", "-t", docker_image, dockerfile_path], check=True)

    # Run container
    try:
        result = subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(temp_dir)}:/app",
            docker_image
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)

        return {
            "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode()
        }

    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out"}

    finally:
        # Cleanup
        subprocess.run(["rm", "-rf", temp_dir])
if __name__ == "__main__":
    code = "print('Hello from Python!')"  # or JS code
    result = execute_function(code, "python", timeout=5)
    print(result)
 
