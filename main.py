import os

from lib.main import Main

workfolder = os.path.dirname(os.path.abspath(__file__))
os.chdir(workfolder)

if __name__ == "__main__":
    Main()
