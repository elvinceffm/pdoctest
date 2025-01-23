import time
from pyvrp import Model
from pyvrp.stop import MaxRuntime, NoImprovement, MaxIterations

from core.data_processing import data_cleansing_route






def solve_with_pyvrp_hgs(instance, solver_hyper_params):
    model = prepare_data_for_pyvrp(instance, solver_hyper_params["multiplier"])
    # set stopping criterion
    if solver_hyper_params["stop_criterion"] == "no_improvement":
        stopping_criterion = NoImprovement(solver_hyper_params["stop_criterion_value"])
    elif solver_hyper_params["stop_criterion"] == "runtime":
        stopping_criterion = MaxRuntime(solver_hyper_params["stop_criterion_value"])
    elif solver_hyper_params["stop_criterion"] == "iterations":
        stopping_criterion = MaxIterations(solver_hyper_params["stop_criterion_value"])
    else:
        raise ValueError(f"Stop criterion must be one of ['no_improvement', 'runtime']; not {solve_with_pyvrp_hgs['stop_criterion']}") # add 'iterations' to list

    # track solver runtime
    start_time = time.time()
    result = model.solve(stop=stopping_criterion, seed=solver_hyper_params["seed"], display=False)
    runtime = time.time() - start_time

    return format_pyvrp_output(instance, model, result), round(runtime, 2), result


def prepare_data_for_pyvrp(instance, multiplier=100):
    """
    Function to prepare the data for the pyvrp model based on the instance data.

    Parameters:
    ----------
    instance: VRP_OBJECT
        Instance object containing the instance data
    model: Model
        Pyvrp model object

    Returns:
    ----------
    model: Model
        Pyvrp model object with the data prepared
    """
    model = Model()
    d_id = instance.depot_identifier
    # add depot to the model
    depot = model.add_depot(
        x=instance.stop_df["x_coord"][instance.stop_df["stop_id"] == d_id].values[0]
        * multiplier,
        y=instance.stop_df["y_coord"][instance.stop_df["stop_id"] == d_id].values[0]
        * multiplier,
        tw_early=instance.stop_df["tw_start"][
            instance.stop_df["stop_id"] == d_id
        ].values[0]
        * multiplier,
        tw_late=instance.stop_df["tw_end"][instance.stop_df["stop_id"] == d_id].values[
            0
        ]
        * multiplier,
    )
    # add clients to the model
    clients = [
        model.add_client(
            x=instance.stop_df["x_coord"][i] * multiplier,
            y=instance.stop_df["y_coord"][i] * multiplier,
            delivery=instance.stop_df["demand"][i],
            tw_early=instance.stop_df["tw_start"][i] * multiplier,
            tw_late=instance.stop_df["tw_end"][i] * multiplier,
            service_duration=instance.stop_df["service_time"][i] * multiplier,
        )
        for i in range(len(instance.stop_df))
        if instance.stop_df["stop_id"][i] != d_id
    ]
    # add edges to the model based on distance matrix
    locations = [depot, *clients]
    for f_idx, frm in enumerate(locations):
        for t_idx, to in enumerate(locations):
            model.add_edge(
                frm,
                to,
                distance=instance.distance_matrix[f_idx, t_idx] * multiplier,
                duration=instance.distance_matrix[f_idx, t_idx] * multiplier,
            )
    # add vehicle types to the model
    for veh_type in instance.veh_type_df["veh_type"]:
        model.add_vehicle_type(
            name=veh_type,
            num_available=max(int(
                instance.veh_type_df["no_of_available"][
                    instance.veh_type_df["veh_type"] == veh_type
                ].values[0]
            ), 1),
            capacity=int(
                instance.veh_type_df["capacity"][
                    instance.veh_type_df["veh_type"] == veh_type
                ].values[0]
            ),
            fixed_cost=int(
                instance.veh_type_df["costs"][
                    instance.veh_type_df["veh_type"] == veh_type
                ].values[0] * multiplier
            ),
        )
    return model


def format_pyvrp_output(instance, model, result):
    """
    Function to format the output of the pyvrp model to a dictionary containing the routes.

    Parameters:
    ----------
    instance: VRP_OBJECT
        Instance object containing the instance data
    model: Model
        Pyvrp model object
    result: Result
        Pyvrp result object

    Returns:   
    ----------
    result_route_dict: dict
        Dictionary containing the routes of the solution
    """
    result_route_dict = {}
    if result.best.is_feasible():
        for veh_idx, route in enumerate(result.best.routes()):
            r_veh = model._vehicle_types[route.vehicle_type()].name
            r_v = data_cleansing_route(route.visits(), instance.depot_identifier)
            result_route_dict[str(veh_idx)] = {"veh_type": r_veh, "route": r_v}
    return result_route_dict