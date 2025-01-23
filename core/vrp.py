import os
import pandas as pd
import pickle as pkl
import numpy as np

from core.data_processing import (
    data_cleansing_gh_bks_solution,
    read_gh_instance,
    read_gh_solution,
)
from core.evaluation import calculate_variable_costs
from core.solving import solve_with_pyvrp_hgs
from core.utils import util_write_object_to_pkl


class VRP_OBJECT:
    """ """

    def __init__(self, name: str, type: str = "HVRPTW") -> "VRP_OBJECT":
        self.name = name
        self.type = type

    def load_instance(
        self,
        path_to_data: str,
        read_pkl: bool = False,
    ) -> "VRP_OBJECT":
        """
        Function to load the instance data from a file in the Solomon/ Gehring Homberger benchmark format.

        Parameters:
        ----------
        path_to_data: str
            Path to the instance file

        Returns:
        ----------
        None
        """
        if read_pkl:
            with open(path_to_data, "rb") as f:
                return pkl.load(f)
        instance_data_dict = read_gh_instance(
            os.path.join(path_to_data, "original", self.name + ".TXT")
        )
        instance_solution_dict = read_gh_solution(
            os.path.join(path_to_data, "solution", self.name + ".sol")
        )
        self.name = instance_data_dict["name"]
        self.spatial_char = self.name.split("_")[0][:-1]
        self.veh_char = self.name.split("_")[0][-1:]
        self.temp_char = self.name.split("_")[-1]
        self.distance_matrix = instance_data_dict["edge_weight"]
        self.stop_df = pd.DataFrame(
            {
                "x_coord": instance_data_dict["node_coord"][:, 0],
                "y_coord": instance_data_dict["node_coord"][:, 1],
                "demand": instance_data_dict["demand"],
                "tw_start": instance_data_dict["time_window"][:, 0],
                "tw_end": instance_data_dict["time_window"][:, 1],
                "service_time": instance_data_dict["service_time"],
            }
        )
        # Add the stop ID as the index
        self.stop_df["stop_id"] = self.stop_df.index.astype(str)
        self.depot_identifier = self.stop_df[self.stop_df["demand"] == 0][
            "stop_id"
        ].values[0]
        self.dimension = len(self.stop_df) - 1  # excluding the depot from the dimension
        self.bks_route_dict = data_cleansing_gh_bks_solution(
            instance_solution_dict["routes"], self.depot_identifier
        )
        self.veh_base_capacity = instance_data_dict[
            "capacity"
        ]
        return self

    
    def setup_heterogeneous_fleet(
        self,
        no_of_vehicle_types: int,
        sum_avail_large_veh: float = 0.9,
        avail_ratio=None,
        capa_interval_str="double",
        capa_cost_ratio: float = 0.8,
        fleet_scenario: str = "f_v_even",
        fix_var_multiplier=2.0,
    ) -> "VRP_OBJECT":

        variable_costs = calculate_variable_costs(
            self.distance_matrix,
            self.bks_route_dict,
            convert_to_idx=True,
            stop_df=self.stop_df,
        )
        # Create vehicle_type_df
        if no_of_vehicle_types == 3:
            veh_types = ["XS", "M", "XL"]
        elif no_of_vehicle_types == 5:
            veh_types = ["XS", "S", "M", "L", "XL"]
        else:
            veh_types = [str(x) for x in range(1,no_of_vehicle_types+1)]
        # ----------------------------------------------
        # Calculate vehicle capacities
        if capa_interval_str != "double":
            Warning("The capa_interval_str must be 'double' for now; setting it to 'double'")
        if capa_interval_str == "double":
            capa_interval = (np.ceil(self.veh_base_capacity * 0.5), self.veh_base_capacity)
        veh_capacities = []
        for i in range(no_of_vehicle_types):
            veh_capacities.append(
                np.ceil(capa_interval[0] + i * (capa_interval[1] - capa_interval[0]) / (no_of_vehicle_types - 1))
            )
        # ----------------------------------------------
        # Calculate vehicle availabilities
        if avail_ratio is None or len(avail_ratio) != no_of_vehicle_types:
            avail_ratio = [1]
            # linearly distribute the availability of large vehicles
            for i in range(1, no_of_vehicle_types):
                avail_ratio.append(
                    round(
                        sum_avail_large_veh / (no_of_vehicle_types-1),
                        4
                    )
                )
        veh_availabilities = [len(self.stop_df[1:])]
        for i in range(1, no_of_vehicle_types):
            veh_availabilities.append(
                max(
                    1,
                    np.ceil((self.stop_df.demand.sum() * avail_ratio[i]) / veh_capacities[i])
                )
            )
        # ----------------------------------------------
        # Calculate vehicle costs
        no_of_routes_in_bks = len(self.bks_route_dict)
        if fleet_scenario == "f_v_even":
            veh_base_costs = np.ceil(
                variable_costs / no_of_routes_in_bks
            )
        elif fleet_scenario == "f_dominant":
            veh_base_costs = np.ceil(
                fix_var_multiplier * variable_costs / no_of_routes_in_bks
            )
        elif fleet_scenario == "v_dominant":
            veh_base_costs = np.ceil(
                variable_costs / (no_of_routes_in_bks * fix_var_multiplier)
            )
        else:
            raise ValueError(
                f"The fleet scenario must be one of ['f_v_even', 'f_dominant', 'v_dominant']; not {self.fleet_scenario}"
            )
        cost_interval = (veh_base_costs/(capa_interval[1]/capa_interval[0]*capa_cost_ratio), veh_base_costs)
        veh_costs = []
        for i in range(no_of_vehicle_types):
            veh_costs.append(
                np.ceil(cost_interval[0] + i * (cost_interval[1] - cost_interval[0]) / (no_of_vehicle_types - 1))
            )
        # Create vehicle_type_df
        self.veh_type_df = pd.DataFrame(
            {
                "veh_type": veh_types,
                "capacity": veh_capacities,
                "costs": veh_costs,
                "no_of_available": veh_availabilities,
                # calculate the share on the complete fleet based no_of_available
                "fleet_share": np.round(np.array(veh_availabilities) / sum(veh_availabilities), 4),
            }
        )
        # Store the vehicle type information as a dictionary to self
        self.veh_type_params = {
            "no_of_types": no_of_vehicle_types,
            "veh_cap_interval_str": capa_interval_str,
            "veh_avail_ratio": avail_ratio,
            "veh_capa_cost_ratio": capa_cost_ratio,
            "veh_base_costs": veh_base_costs,
            "sum_avail_large_veh": sum_avail_large_veh,
            "fleet_scenario": fleet_scenario,
            "fix_var_multiplier": fix_var_multiplier,
        }
        return self
    
    def solve(self, solver_hyper_params: dict) -> dict:
        """

        """
        if solver_hyper_params["solver"] == "pyvrp":
            return solve_with_pyvrp_hgs(self, solver_hyper_params)
        return None

    def write_to_pkl(self, path_to_write_pkl: str) -> None:
        """
        """
        util_write_object_to_pkl(self, path_to_write_pkl)