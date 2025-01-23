"""
This script is used to run the errorgap benchmark on the HVRPTW instances.
20k iterations are run on each instance to determine an approximate BKS.
"""
 
import logging
import os
import pickle as pkl#from core.vrp import VRP_OBJECT
#from tabulate import tabulate
import matplotlib.pyplot as plt

from core.vrp import VRP_OBJECT
from core.evaluation import VRP_SOLUTION
from core.utils import set_file_directory

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# test data filepaths

path_to_load_sing_hvrptw_pkl = os.path.join(os.getcwd(), "test_input/c1_2_1.pkl")

path_to_write_sing_sol_pkl = os.path.join(os.getcwd(), "test_output")

path_to_write_sing_sol_stats = os.path.join(os.getcwd(), "test_output/stats")

# logger minimal setup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), "testlog/test.log"), mode="w"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger()

# solver params

solver_hyper_params = {
    "solver": "pyvrp",
    "stop_criterion": "iterations", # convention: run algo on no-improvement for 20k to determine approx. BKS 
    "stop_criterion_value": 10000,
    "multiplier": 100,
    "seed": 0,
}

# load instance and generate solution for vrp

instance = VRP_OBJECT(name="", type="HVRPTW").load_instance(os.path.join(path_to_load_sing_hvrptw_pkl), read_pkl=True)
route_dict, runtime, result_raw = instance.solve(solver_hyper_params)
instance_sol = VRP_SOLUTION(instance, solver_hyper_params, runtime, route_dict)
instance_sol.write_to_pkl(path_to_write_sing_sol_pkl)

logger.info(f"Run completed in {runtime} sec.")
logger.info("done")

result_raw.stats.to_csv(os.path.join(path_to_write_sing_sol_stats, "_stats_ss2.csv"))

print(instance_sol.total_costs)