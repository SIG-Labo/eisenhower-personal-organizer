 
"""
Eisenhower-Matrix Personal Planner 3.0
Copyright (c) 2024 Peter De Ceuster
https://peterdeceuster.uk/
Free to distribute
Distributed under the FPA General Code License
"""


import subprocess
import os

def main():
    # Wait for unlocksoft.py to finish
    process = subprocess.Popen(["python", "unlocksoft.py"])
    process.wait()

    # Launch E-Matrix 3.0.exe after unlocksoft.py has exited
    os.startfile("E-Matrix 3.0.exe")

if __name__ == "__main__":
    main()
