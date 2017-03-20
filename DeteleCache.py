from config import UPLOAD_FOLDER
import shutil
import os

def DeleteCache():
    try:
        shutil.rmtree(UPLOAD_FOLDER)
        os.mkdir(UPLOAD_FOLDER)
    except:
        pass

if __name__ == "__main__":
    DeleteCache()
