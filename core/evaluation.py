import pandas as pd

from core.utils import util_write_object_to_pkl

class VRP_SOLUTION:
    def __init__(
        self, VRP_OBJECT, solver_hyper_params:dict , runtime: float, route_dict: dict, dec_prec: int = 4
    ) -> "VRP_SOLUTION":
        self.name = VRP_OBJECT.name
        self.veh_type_params = VRP_OBJECT.veh_type_params
        self.dimension = VRP_OBJECT.dimension
        self.solver_hyper_params = solver_hyper_params
        self.runtime = runtime
        # calculate variable costs
        self.var_costs_tt = calculate_variable_costs(
            VRP_OBJECT.distance_matrix,
            route_dict,
            convert_to_idx=True,
            stop_df=VRP_OBJECT.stop_df,
            dec_prec=dec_prec,
        )
        # calculate fixed costs for each route based on VRP_OBJECT.veh_type_df
        fixed_costs = 0
        for veh_idx in route_dict.keys():
            # get the fixed costs for the vehicle type of the vehicle based on VRP_OBJECT.veh_type_df
            fixed_costs += VRP_OBJECT.veh_type_df["costs"][
                VRP_OBJECT.veh_type_df["veh_type"] == route_dict[veh_idx]["veh_type"]
            ].values[0]
        self.fix_costs = fixed_costs
        # calculate total costs
        self.total_costs = self.var_costs_tt + self.fix_costs
        # create route_df with the following columns: veh_id, veh_type, var_costs, fix_costs, utilization
        route_df = pd.DataFrame(
            columns=["veh_id", "veh_type", "var_costs", "fix_costs"]
        )  # "utilization"])
        for veh_idx in route_dict.keys():
            veh_type = route_dict[veh_idx]["veh_type"]
            var_costs = calculate_variable_costs(
                VRP_OBJECT.distance_matrix,
                {veh_idx: route_dict[veh_idx]},
                convert_to_idx=True,
                stop_df=VRP_OBJECT.stop_df,
                dec_prec=dec_prec,
            )
            fix_costs = VRP_OBJECT.veh_type_df["costs"][
                VRP_OBJECT.veh_type_df["veh_type"] == veh_type
            ].values[0]
            veh_capacity = VRP_OBJECT.veh_type_df["capacity"][
                VRP_OBJECT.veh_type_df["veh_type"] == veh_type
            ].values[0]
            utilization = calculate_utilization(
                route_dict[veh_idx]["route"],
                VRP_OBJECT.stop_df,
                veh_capacity,
                convert_to_idx=True,
                dec_prec=dec_prec,
            )
            route_df = pd.concat(
                [
                    route_df,
                    pd.DataFrame(
                        {
                            "veh_id": veh_idx,
                            "veh_type": veh_type,
                            "var_costs": var_costs,
                            "fix_costs": fix_costs,
                            "total_costs": var_costs + fix_costs,
                            "utilization": utilization,
                            "f_v_ratio": fix_costs / var_costs,
                            "load_unit_costs": fix_costs / (veh_capacity * utilization),
                        },
                        index=[0],
                    ),
                ],
                ignore_index=True,
            )
        self.route_df = route_df

    def write_to_pkl(self, path_to_write_pkl):
        util_write_object_to_pkl(self, path_to_write_pkl, sol_object=True)

def calculate_variable_costs(
    distance_matrix, route_dict, convert_to_idx=True, stop_df=None, dec_prec=4
):
    """
    Function to calculate the variable costs of a solution based on the distance matrix and the route_dict.
    """
    # create list of routes out of dict key "route"
    routes = []
    for veh_idx in route_dict.keys():
        routes.append(route_dict[veh_idx]["route"])

    if convert_to_idx and stop_df is None:
        raise ValueError("If convert_to_idx is True, stop_df must be provided")
    # calculate variable costs for each route based on VRP_OBJECT.distance_matrix
    variable_costs = 0
    for route in routes:
        # transform the route which is a ordered list of stop_ids to the corresponding ordered list of stop indices based on VRP_OBJECT.stop_df
        route_idx = [
            stop_df[stop_df["stop_id"] == stop_id].index[0] for stop_id in route
        ]
        # calculate the variable costs for the route based on the distance matrix
        route_distance = 0
        for i in range(len(route_idx) - 1):
            route_distance += distance_matrix[route_idx[i], route_idx[i + 1]]
        variable_costs += route_distance
    return round(variable_costs, dec_prec)


def calculate_utilization(
    route: list,
    stop_df: pd.DataFrame,
    veh_capacity: float,
    convert_to_idx: bool = True,
    dec_prec: int = 4,
) -> float:
    """
    Function to calculate the utilization of a vehicle based on the route and the stop_df.
    """
    # transform the route which is a ordered list of stop_ids to the corresponding ordered list of stop indices based on stop_df
    if convert_to_idx:
        route_idx = [
            stop_df[stop_df["stop_id"] == stop_id].index[0] for stop_id in route
        ]
    # get the total demand of the route based on the stop_df.demand

    utilization = stop_df.iloc[route_idx].demand.sum() / veh_capacity
    return round(utilization, dec_prec)
