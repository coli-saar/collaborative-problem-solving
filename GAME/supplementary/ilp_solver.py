import networkx as nx
from gurobipy import GRB, Env, Model
from numpy import argmax

import tsp_utils


def solve_ilp(
    g: nx.Graph, partial_path: list[str] = ["L"], get_all_tours: bool = False
) -> tuple[list[str], int] | tuple[list[list[str]], int]:
    nodelist = list(g.nodes())

    n = g.number_of_nodes()
    weight_mat = nx.adjacency_matrix(g).todense()

    with Env(empty=True) as env:
        env.setParam("OutputFlag", 0)
        env.start()

        model = Model("TSP", env=env)

        # Create distance variable and set objective (maximizing distance)
        D = model.addVar(vtype=GRB.INTEGER, name="D")
        model.setObjective(D, GRB.MAXIMIZE)

        # Create variables for each edge (both directions)
        edges = model.addMVar((n, n), vtype=GRB.BINARY, name="edges")

        # No self-loops
        model.addConstr(edges.diagonal().sum() == 0, name="no_self_loops")

        # Each node must be arrived at and left from exactly once
        model.addConstr(edges.sum(axis=0) == 1, name="one_arrival_per_node")
        model.addConstr(edges.sum(axis=1) == 1, name="one_departure_per_node")

        # Partial path constraints
        if partial_path:
            for i in range(len(partial_path) - 1):
                model.addConstr(
                    edges[
                        nodelist.index(partial_path[i]),
                        nodelist.index(partial_path[i + 1]),
                    ]
                    == 1
                )

        # Subtour elimination constraints (Miller-Tucker-Zemlin formulation: https://en.wikipedia.org/wiki/Travelling_salesman_problem#Miller%E2%80%93Tucker%E2%80%93Zemlin_formulation)
        counters = model.addMVar(n, vtype=GRB.INTEGER, name="counters")
        model.addConstrs(
            counters[i] - counters[j] + 1 <= (n - 1) * (1 - edges[i, j])
            for i in range(1, n)
            for j in range(1, n)
            if i != j
        )
        model.addConstrs(2 <= counters[i] for i in range(1, n))
        model.addConstrs(counters[i] <= n for i in range(1, n))

        # Distance variable must equal the sum of the weights of the edges
        model.addConstr(
            (
                sum(  # type: ignore
                    [
                        edges[source, target] * weight_mat[source, target]
                        for source in range(n)
                        for target in range(n)
                    ]
                )
                == D
            ),
            name="calculate_coins",
        )

        model.optimize()

        # Code below writes model info to files
        # model.write("tsp.lp")  # the variables, bounds, constraints, and objective
        # model.write("tsp.sol")  # the solution (values of all variables)

        tour_matrix = edges.getAttr("X")

        node_sequence = (
            [nodelist.index(label) for label in partial_path] if partial_path else [0]
        )
        while len(node_sequence) < n:
            # print(tour_matrix)
            last_node = node_sequence[-1]
            next_node = int(argmax(tour_matrix[last_node]))
            node_sequence.append(next_node)
            tour_matrix[last_node][next_node] = 0
            # tour_matrix[next_node][last_node] = 0

        ordering = [nodelist[i] for i in node_sequence]

        return ordering, model.getObjective().getValue()
