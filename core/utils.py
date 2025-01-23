import os
import pickle as pkl
from platform import platform


def set_file_directory(on_server: bool = False):
    """
    Function to set the file directory based on the system to easily switch between local and server paths

    Returns:
    local_path_to_instances (str): local path to the instances
    path_to_write_pkl (str): path to write the instance pkl files
    path_to_write_sol_pkl (str): path to write the solution pkl files

    """
    if on_server:
        local_path_to_instances = os.path.join(
            os.getcwd(), "ssot_data/input_data/gehring_homberger"
        )
        path_to_write_pkl = os.path.join(
            os.getcwd(), "ssot_data/input_data/05_sap_gh_hvrptw/instance_pkls"
        )
        path_to_write_sol_pkl = os.path.join(
            os.getcwd(), "ssot_data/result_data/sap_project/solution_pkls"
        )
        log_dir = os.path.join(os.getcwd(), "sap_vrp_opt_lagrange/zzz_log_files/")
    else:
        # TODO: This needs to be updated!
        local_path_to_instances = (
            "C:\\big_data_storage\\ssot_data\\input_data\\gehring_homberger"
        )
        path_to_write_pkl = "C:\\big_data_storage\\ssot_data\\input_data\\05_sap_gh_hvrptw\instance_pkls"
        path_to_write_sol_pkl = (
            "C:\\big_data_storage\\ssot_data\\result_data\\sap_project\\solution_pkls"
        )
        log_dir = os.path.join(os.getcwd(), "zzz_log_files")

    return local_path_to_instances, path_to_write_pkl, path_to_write_sol_pkl, log_dir


def util_write_object_to_pkl(routing_object, path_to_write_pkl, sol_object=False):

    # check if f"veh_types_{no_vehicle_types}" is a folder in path_to_write_pkl and if not create it
        n_types = routing_object.veh_type_params["no_of_types"]
        if not os.path.exists(os.path.join(path_to_write_pkl, f"n_veh_types_{n_types}")):
            os.makedirs(os.path.join(path_to_write_pkl, f"n_veh_types_{n_types}"))
        path_to_write_pkl = os.path.join(path_to_write_pkl, f"n_veh_types_{n_types}")
        # check if fleet_scenario is a folder in local_path_to_store_hetero_instance_pkl and if not create it
        f_v_s = f"{routing_object.veh_type_params['fleet_scenario']}_m{routing_object.veh_type_params['fix_var_multiplier']}"
        if not os.path.exists(os.path.join(path_to_write_pkl, f_v_s)):
            os.makedirs(os.path.join(path_to_write_pkl, f_v_s))
        path_to_write_pkl = os.path.join(path_to_write_pkl, f_v_s)
        # check if capa_interval_str is a folder in local_path_to_store_hetero_instance_pkl and if not create it
        capa_interval_str = routing_object.veh_type_params["veh_cap_interval_str"]
        if not os.path.exists(os.path.join(path_to_write_pkl, f"capa_interval_{capa_interval_str}")):
            os.makedirs(os.path.join(path_to_write_pkl, f"capa_interval_{capa_interval_str}"))
        path_to_write_pkl = os.path.join(path_to_write_pkl, f"capa_interval_{capa_interval_str}")
        # check if capa_cost_ratio is a folder in local_path_to_store_hetero_instance_pkl and if not create it
        capa_cost_ratio = routing_object.veh_type_params["veh_capa_cost_ratio"]
        if not os.path.exists(os.path.join(path_to_write_pkl, f"capa_cost_ratio_{capa_cost_ratio}")):
            os.makedirs(os.path.join(path_to_write_pkl, f"capa_cost_ratio_{capa_cost_ratio}"))
        path_to_write_pkl = os.path.join(path_to_write_pkl, f"capa_cost_ratio_{capa_cost_ratio}")
        # concat items of avail_ratio to string
        avail_ratio_str = "_".join(map(str, routing_object.veh_type_params["veh_avail_ratio"]))
        # check if avail_ratio is a folder in local_path_to_store_hetero_instance_pkl and if not create it
        sum_avail_large_veh = routing_object.veh_type_params["sum_avail_large_veh"]
        if not os.path.exists(os.path.join(path_to_write_pkl, f"avail_ratio_{avail_ratio_str}__{sum_avail_large_veh}")):
            os.makedirs(os.path.join(path_to_write_pkl, f"avail_ratio_{avail_ratio_str}__{sum_avail_large_veh}"))
        # update path_to_write_pkl
        path_to_write_pkl = os.path.join(path_to_write_pkl, f"avail_ratio_{avail_ratio_str}__{sum_avail_large_veh}")
        if sol_object:
            hp = routing_object.solver_hyper_params
            file_name = f'{routing_object.name}_{hp["solver"]}_{hp["stop_criterion"]}{hp["stop_criterion_value"]}_s{hp["seed"]}.pkl'
        else:
            file_name = f"{routing_object.name}.pkl"
        # Save instance to pkl
        with open(os.path.join(path_to_write_pkl, file_name), "wb") as f:
            pkl.dump(routing_object, f)