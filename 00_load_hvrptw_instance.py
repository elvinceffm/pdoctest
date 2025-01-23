import os

from core.vrp import VRP_OBJECT
from core.utils import set_file_directory

_, path_to_load_pkl, path_to_sol = set_file_directory()

# Walk through the directory and read all the files and store them in a list
instance_files = []
for root, dirs, files in os.walk(path_to_sol):
    for file in files:
        instance = VRP_OBJECT(name="", type="HVRPTW").load_instance(
            os.path.join(root, file), read_pkl=True
        )
        print(instance)
