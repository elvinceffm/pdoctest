import logging
import numpy as np
import os
import pandas as pd
pd.set_option("display.max_columns", None)
import pickle as pkl

from core.evaluation import VRP_SOLUTION
from core.utils import set_file_directory

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

_, path_to_load_hvrptw_pkls, path_to_read_sol_pkl, _ = set_file_directory()

result_dict = {
    "instance_name": [],
    "seed": [],
    "no_of_veh_types": [],
    "veh_cap_interval": [],
    "veh_capa_cost_ratio": [],
    "sum_avail_large_veh": [],
    "fleet_scenario": [],
    "fix_var_multiplier": [],
    #"total_costs": [],
    #"var_costs": [],
    #"fix_costs": [],
    #"runtime": [],
}
veh_types = 3
if veh_types == 3:
    list_of_type_names = ["XS", "M", "XL"]
if veh_types == 5:
    list_of_type_names = ["XS", "S", "M", "L", "XL"]
for veh_type_name in list_of_type_names:
    result_dict.update(
        {
            f"{veh_type_name}_min_util": [],
            f"{veh_type_name}_mean_util": [],
            f"{veh_type_name}_min_load_unit_costs": [],
            f"{veh_type_name}_max_load_unit_costs": [],
            f"{veh_type_name}_mean_load_unit_costs": [],
        }
    )

counter = 0
for root, dirs, files in os.walk(path_to_read_sol_pkl):
    for file in files:
        with open(os.path.join(root, file), "rb") as f:
            instance_sol = pkl.load(f)
        #print('debug')
        if instance_sol.veh_type_params["no_of_types"] != veh_types:
            continue
        # create an aggregated route_df grouped by veh_type
        agg_route_df = instance_sol.route_df.groupby("veh_type").agg(
            #min_var_costs=("var_costs", np.min),
            #max_var_costs=("var_costs", np.max),
            #mean_var_costs=("var_costs", np.mean),
            min_util=("utilization", np.min),
            # max_util=("utilization", np.max),
            mean_util=("utilization", np.mean),
            #min_f_v_ratio=("f_v_ratio", np.min),
            #max_f_v_ratio=("f_v_ratio", np.max),
            #mean_f_v_ratio=("f_v_ratio", np.mean),
            min_load_unit_costs=("load_unit_costs", np.min),
            max_load_unit_costs=("load_unit_costs", np.max),
            mean_load_unit_costs=("load_unit_costs", np.mean)
        )
        if len(list_of_type_names) > len(agg_route_df.index):
            print(len(agg_route_df.index))
            continue
         # add data to result_dict
        try:
            result_dict["seed"].append(instance_sol.solver_hyper_params["seed"])
            result_dict["instance_name"].append(instance_sol.name)
            result_dict["no_of_veh_types"].append(instance_sol.veh_type_params["no_of_types"])
            result_dict["veh_cap_interval"].append(instance_sol.veh_type_params["veh_cap_interval_str"])
            result_dict["veh_capa_cost_ratio"].append(instance_sol.veh_type_params["veh_capa_cost_ratio"])
            result_dict["sum_avail_large_veh"].append(instance_sol.veh_type_params["sum_avail_large_veh"])
            result_dict["fleet_scenario"].append(instance_sol.veh_type_params["fleet_scenario"])
            result_dict["fix_var_multiplier"].append(instance_sol.veh_type_params["fix_var_multiplier"])
            #result_dict["total_costs"].append(instance_sol.total_costs)
            #result_dict["var_costs"].append(instance_sol.var_costs_tt)
            #result_dict["fix_costs"].append(instance_sol.fix_costs)
            #result_dict["runtime"].append(instance_sol.runtime)
        except Exception as e:
            counter += 1
            continue
        for veh_type_name in list_of_type_names:
            try:
                result_dict[f"{veh_type_name}_min_util"].append(agg_route_df.loc[veh_type_name, "min_util"])
                result_dict[f"{veh_type_name}_mean_util"].append(agg_route_df.loc[veh_type_name, "mean_util"])
                result_dict[f"{veh_type_name}_min_load_unit_costs"].append(agg_route_df.loc[veh_type_name, "min_load_unit_costs"])
                result_dict[f"{veh_type_name}_max_load_unit_costs"].append(agg_route_df.loc[veh_type_name, "max_load_unit_costs"])
                result_dict[f"{veh_type_name}_mean_load_unit_costs"].append(agg_route_df.loc[veh_type_name, "mean_load_unit_costs"])
            except Exception as e:
                counter += 1
                continue
# get lenght of each list in result_dict
lenghts = [len(value) for value in result_dict.values()]
# create a DataFrame from result_dict
result_df = pd.DataFrame(result_dict)
print('debug')
# save result_df to csv
result_df.to_csv(f"veh_result_df_types_{veh_types}.csv")