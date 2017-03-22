import os

# run first, will setup a file structure for saving that the rest of the script depends on

def config_store():
    dot =  os.path.exists(os.path.expanduser("~/.lsipw"))
    if dot != True:
        os.mkdir(os.path.expanduser("~/.lsipw"))
        os.mkdir(os.path.expanduser("~/.lsipw/data"))
        os.mkdir(os.path.expanduser("~/.lsipw/models"))
    data = os.path.exists(os.path.expanduser("~/.lsipw/data"))
    if data != True:
        os.mkdir(os.path.expanduser("~/.lsipw/data"))
    models = os.path.exists(os.path.expanduser("~/.lsipw/models"))
    if models != True:
        os.mkdir(os.path.expanduser("~/.lsipw/models"))
    return 1    


a = config_store()
if a != 1:
    print("FAILED")
print("SUCCESS")
