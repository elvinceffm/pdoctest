from datetime import datetime
import logging
import os
import pandas as pd
pd.set_option("display.max_columns", None)
import pickle as pkl

from core.vrp import VRP_OBJECT
from core.evaluation import VRP_SOLUTION
from core.utils import set_file_directory

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# _, path_to_load_hvrptw_pkls, path_to_write_sol_pkl, log_files = set_file_directory()
path_to_load_hvrptw_pkls = os.path.join(os.getcwd(), 'input_data/05_sap_gh_hvrptw/instance_pkls')
# create a folder to store the solution pkl files that is named by the date and time of the experiment
path_to_write_sol_pkl = os.path.join(os.getcwd(), f'result_data/{datetime.now().strftime("%Y%m%d__%H%M")}')
os.makedirs(path_to_write_sol_pkl, exist_ok=True)
# Initialize a counter
pkl_count = 0
# Walk through directory and count .pkl files
for dirpath, dirnames, filenames in os.walk(path_to_load_hvrptw_pkls):
    # Filter and count .pkl files
    pkl_count += sum(1 for f in filenames if f.endswith('.pkl'))
# setup logging
exp_run_name = "20240628_test"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), "zzz_log_files", f"{exp_run_name}.log"), mode="w"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger()

seeds = [0] #,1] #,2,3,4]
solver_hyper_params = {
    "solver": "pyvrp",
    "stop_criterion": "runtime", # "no_improvement", #
    "stop_criterion_value": 10, # 5000, # 3, # 
    "multiplier": 100,
    "seed": -1,
}

total_no_of_runs = pkl_count * len(seeds)
run_no = 0

for root, dirs, files in os.walk(path_to_load_hvrptw_pkls):
    for file in files:
        instance = VRP_OBJECT(name="", type="HVRPTW").load_instance(
            os.path.join(root, file), read_pkl=True
        )
        for seed in seeds:
            # for seed in seeds[:1]:
            run_no += 1
            # set the solver hyper parameters
            solver_hyper_params["seed"] = seed
            try:
                route_dict, runtime = instance.solve(solver_hyper_params)
                instance_sol = VRP_SOLUTION(instance, solver_hyper_params, runtime, route_dict)
            except Exception as e:
                logger.info(e)
                continue
            # save the solution as a pkl file
            instance_sol.write_to_pkl(path_to_write_sol_pkl)
            logger.info(f"Run {run_no}/{total_no_of_runs} completed in {runtime} sec.")
logger.info("done")