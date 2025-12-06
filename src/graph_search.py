from .utils import trace_path

def breadth_first_search(graph, start, goal):
    graph.init_graph()

    queue = [start]
    graph.nodes[start.i][start.j].visited = True
    graph.visited_cells.append(start)

    while queue:
        current = queue.pop(0)
        if current.i == goal.i and current.j == goal.j:
            return trace_path(current, graph)

        for nbr in graph.find_neighbors(current.i, current.j):
            node = graph.nodes[nbr.i][nbr.j]
            if not node.visited:
                node.visited = True
                node.parent = current
                graph.visited_cells.append(nbr)
                queue.append(nbr)

    return []
