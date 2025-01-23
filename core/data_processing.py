import vrplib

def read_gh_instance(file_path):
    """
    Function to read an instance file in the format of the Solomon/ Gehring Homberger benchmark format.
    Note: This instance file assumes a HOMOGENOUS fleet with a constant capacity and no fixed vehicle costs.
    
    Parameters:
    ----------
    file_path: str
        Path to the instance file

    Returns:
    ----------
    instance: dict
        Dictionary containing the instance information
    """
    if file_path.split(".")[-1] == "TXT":
        # Read instance file
        return vrplib.read_instance(file_path, instance_format="solomon")
    else:
        raise Exception("File format not supported, must be .TXT")
    

def read_gh_solution(file_path):
    """
    Function to read a solution file in the format of the Solomon/ Gehring Homberger benchmark format.
    Note: This solution is based on a HOMOGENOUS fleet and only optimzes the total travel time (neglecting waiting and service times)

    Parameters:
    ----------
    file_path: str
        Path to the solution file

    Returns:
    ----------
    solution: dict
        Dictionary containing the solution information
    """
    if file_path.split(".")[-1] == "sol":
        # Read solution file
        return vrplib.read_solution(file_path)
    else:
        raise Exception("File format not supported, must be .sol")
    
def data_cleansing_gh_bks_solution(gh_bks_solution_routes: list, depot_identifier, veh_type = "small") -> dict:
    """

    """
    gh_solution_dict = {}
    # check if stop_id in routes are of type str otherwise convert
    for veh_idx, route in enumerate(gh_bks_solution_routes):
        route = data_cleansing_route(route, depot_identifier)
        # add the route to the solution_dict, the key is the vehicle index as str
        gh_solution_dict[str(veh_idx)] = {"veh_type": veh_type, "route": route}
    return gh_solution_dict

def data_cleansing_route(route: list, depot_identifier: str) -> list:
    """
    Function to cleanse a route by adding the depot as the first and last stop if it is not already there.

    Parameters:
    ----------
    route: list
        List of stop_ids in the route
    depot_identifier: str
        Identifier of the depot

    Returns:
    ----------
    route: list
        List of stop_ids in the route with the depot as the first and last stop
    """
    # check if stop_id in routes are of type str otherwise convert
    route = list(map(str, route))
    # check if depot is the first stop in the route
    if route[0] != depot_identifier:
        route.insert(0, depot_identifier)
    # check if depot is the last stop in the route
    if route[-1] != depot_identifier:
        route.append(depot_identifier)
    return route