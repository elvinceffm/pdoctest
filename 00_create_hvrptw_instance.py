import os

#test

from core.vrp import VRP_OBJECT
from core.utils import set_file_directory

local_path_to_instances, path_to_write_pkl, _ = set_file_directory()

# Read instance and solution files
list_of_instances = [
    "C1_2_1",
    "C1_2_4",
    "C1_2_8",
    "RC2_2_1",
    "RC2_2_4",
    "RC2_2_8",
]

fleet_scenarios_list = ["f_dominant", "v_dominant", "f_v_even"]
no_of_vehicle_types_list = [3, 5]
sum_avail_large_veh_list = [0.67, 0.8, 0.95]  # [0.67, 0.75, 0.8, 0.9, 0.95, 1]
capa_interval_str_list = ["double"]
capa_cost_ratio_list = [0.67, 0.8, 0.95]  #  [0.67, 0.75, 0.8, 0.9, 0.95, 1]

avail_ratio = None  # TODO: discuss this with SAP again if uniform availability is okay

for instance_name in list_of_instances:
    for fleet_scenario in fleet_scenarios_list:
        print(f"{instance_name}_{fleet_scenario}")
        if fleet_scenario == "f_v_even":
            fix_var_multiplier_list = [1]
        else:
            fix_var_multiplier_list = [1.5, 2, 3]
        for fix_var_multiplier in fix_var_multiplier_list:
            for no_vehicle_types in no_of_vehicle_types_list:
                for sum_avail_large_veh in sum_avail_large_veh_list:
                    for capa_interval_str in capa_interval_str_list:
                        for capa_cost_ratio in capa_cost_ratio_list:
                            instance = VRP_OBJECT(
                                name=instance_name, type="HVRPTW"
                            ).load_instance(os.path.join(local_path_to_instances))
                            instance.setup_heterogeneous_fleet(
                                no_vehicle_types,
                                sum_avail_large_veh,
                                avail_ratio,
                                capa_interval_str,
                                capa_cost_ratio,
                                fleet_scenario,
                                fix_var_multiplier,
                            )
                            instance.write_to_pkl(path_to_write_pkl)
print("done")
