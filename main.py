import subprocess

def run_script(script_name):
    print(f"Starting {script_name}")
    subprocess.Popen(["python3", script_name])

if __name__ == "__main__":
    # Replace 'script1.py' and 'script2.py' with the actual names of your scripts
    run_script("ptz.py")
    run_script("xf.py")

    print("Both scripts are running concurrently...")
    # Wait for the user to press Enter to stop the scripts
    input("Press Enter to exit...")

    # You can add logic to terminate the scripts if needed
