from itertools import permutations

import networkx as nx


def board_to_graph(board: list[tuple[str, str, int]]) -> nx.Graph:
    """Converts a board (list of edges) to a graph."""
    graph = nx.Graph()
    for edge in board:
        graph.add_edge(edge[0], edge[1], weight=edge[2])
    return graph


def is_complete(g: nx.Graph) -> bool:
    """Checks whether g is a complete graph."""
    n = len(g.nodes)
    return g.number_of_edges() == n * (n - 1) // 2


def validate_graph(g: nx.Graph):
    """
    Checks that the graph is valid for TSP.
    In other words, checks that it is complete and has positive edge weights.
    """
    if not is_complete(g):
        raise ValueError("Graph must be complete")
    for _, _, weight in g.edges(data="weight"):
        if weight <= 0:
            raise ValueError("Edge weights must be positive")


def solve(
    g: nx.Graph, partial_path: list[str] = ["L"], get_all_tours: bool = False
) -> tuple[list[str], int] | tuple[list[list[str]], int]:
    """Find the longest path in a complete graph that starts with partial_path."""
    start_node = partial_path[0] if partial_path else "L"
    remaining_nodes = [
        node for node in g.nodes if node not in partial_path and node != start_node
    ]

    best_tours: list[list[str]] = []
    best_distance = 0

    weight_dict = {
        (e[1], e[0]) if flip else e: w
        for e, w in nx.get_edge_attributes(g, "weight").items()
        for flip in range(2)
    }

    for perm in permutations(remaining_nodes):
        ordering = partial_path + list(perm) + [start_node]
        distance = sum(
            [
                weight_dict[ordering[i], ordering[i + 1]]
                for i in range(len(ordering) - 1)
            ]
        )

        if distance > best_distance:
            best_distance = distance
            best_tours = [ordering[:-1]]
        elif get_all_tours and distance == best_distance:
            best_tours.append(ordering)

    if best_tours == []:
        raise RuntimeError("No valid tour found")

    return best_tours if get_all_tours else best_tours[0], best_distance
