import sys

def main():
    code = open("user_code.py").read()
    exec(code)

if __name__ == "__main__":
    main()
 
