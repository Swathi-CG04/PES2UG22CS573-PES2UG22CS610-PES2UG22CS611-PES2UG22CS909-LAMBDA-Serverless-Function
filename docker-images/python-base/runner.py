import sys
import os

def main():
    if len(sys.argv) < 2:
        print("No path to user code provided.")
        return

    user_code_path = os.path.join(sys.argv[1], "user_code.py")
    try:
        with open(user_code_path, "r") as f:
            code = f.read()
            exec(code, {})
    except Exception as e:
        print(f"Execution error: {e}")

if __name__ == "__main__":
    main()
