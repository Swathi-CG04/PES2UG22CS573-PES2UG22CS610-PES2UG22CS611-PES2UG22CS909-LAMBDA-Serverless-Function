import subprocess
import uuid
import os
import time

def warm_up_images():
    print("Warming up Docker base images...")

    subprocess.run([
        "docker", "build", "-t", "lambda-python",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../docker-images/python-base"))
    ], check=True)

    subprocess.run([
        "docker", "build", "-t", "lambda-js",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../docker-images/js-base"))
    ], check=True)

    print("Warm-up complete.")

def execute_function(code: str, language: str, timeout: int = 5, runtime: str = "runc"):
    temp_dir = f"temp_exec/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)

    if language == "python":
        file_name = "user_code.py"
        docker_image = "lambda-python"
        dockerfile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docker-images/python-base"))
    elif language == "javascript":
        file_name = "user_code.js"
        docker_image = "lambda-js"
        dockerfile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docker-images/js-base"))
    else:
        return {"error": "Unsupported language"}

    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, "w") as f:
        f.write(code)

    # Build image (ideally cache this — already handled in warm-up)
    subprocess.run(["docker", "build", "-t", docker_image, dockerfile_path], check=True)

    try:
        start_time = time.perf_counter()

        result = subprocess.run([
            "docker", "run", "--rm",
            "--runtime", runtime,
            "-v", f"{os.path.abspath(temp_dir)}:/app/usercode",
            docker_image
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)

        end_time = time.perf_counter()
        elapsed = round(end_time - start_time, 3)

        return {
            "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode(),
            "duration": f"{elapsed}s"
        }

    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out"}

    finally:
        subprocess.run(["rm", "-rf", temp_dir])

if __name__ == "__main__":
    warm_up_images()
    code = "print('Hello from Python!')"
    result = execute_function(code, "python", timeout=5, runtime="runc")
    print(result)
