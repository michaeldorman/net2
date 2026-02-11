#!/usr/bin/python3
import numpy as np
import geopandas as gpd
import shapely
import networkx as nx

# Prepare network
def prepare(G, ids_to_int=True):
    # IDs to 'int'
    if ids_to_int:
        mapping = {i: int(i) for i in G.nodes()}
        G = nx.relabel_nodes(G, mapping)
    # nodes
    for i in G.nodes:
    # 'geometry' to 'shapely'
        if 'geometry' in G.nodes[i]:
            if isinstance(G.nodes[i]['geometry'], str):
                G.nodes[i]['geometry'] = shapely.from_wkt((G.nodes[i]['geometry']))
    # edges
    for u,v in G.edges:
        # 'geometry' to 'shapely'
        if 'geometry' in G[u][v]:
            if isinstance(G[u][v]['geometry'], str):
                G[u][v]['geometry'] = shapely.from_wkt((G[u][v]['geometry']))
        # 'length' to 'float'
        if 'length' in G[u][v]:
            G[u][v]['length'] = float(G[u][v]['length'])
        # rename 'travel_time' to 'time'
        if 'travel_time' in G[u][v]:
            G[u][v]['time'] = G[u][v]['travel_time']
            del G[u][v]['travel_time']
        # 'time' to 'float'
        if 'time' in G[u][v]:
            G[u][v]['time'] = float(G[u][v]['time'])
    return G

# Calculate 'pos' dictionary with node 'x' and 'y'
def pos(G):
    return {i: [G.nodes[i]['geometry'].x, G.nodes[i]['geometry'].y] for i in G.nodes}

# Network nodes to 'GeoDataFrame'
def nodes_to_gdf(network, crs=None):
    geom = []
    node_id = []
    for i in network.nodes:
        geom.append(network.nodes[i]['geometry'])
        node_id.append(i)
    nodes = gpd.GeoDataFrame({'id':node_id, 'geometry':geom}, crs=crs)
    return nodes

# Network edges to 'GeoDataFrame'
def edges_to_gdf(network, crs=None):
    edges = nx.to_pandas_edgelist(network)
    edges = gpd.GeoDataFrame(edges, crs=crs)
    return edges

# Nearest node to given point
def nearest_node(G: nx.Graph, pnt: shapely.geometry.Point) -> tuple:
    """
    Find the nearest network node to the specified point
    
    :param G: `networkx` Network
    :param pnt: `shapely` geometry of type 'Point'
    """
    min_distance = float('inf')
    nearest_node = None
    for i in G.nodes:
        distance = pnt.distance(G.nodes[i]['geometry'])
        if distance < min_distance:
            min_distance = distance
            nearest_node = i
    return nearest_node, min_distance

# Nearest edge to given point
def nearest_edge(G: nx.Graph, pnt: shapely.geometry.Point) -> tuple:
    """
    Find the nearest network edge to the specified point
    
    :param G: `networkx` Network
    :param pnt: `shapely` geometry of type 'Point'
    """
    min_distance = float('inf')
    nearest_edge = None
    for i in G.edges:
        geom_edge = G.edges[i]['geometry']
        distance = pnt.distance(geom_edge)
        if distance < min_distance:
            min_distance = distance
            nearest_edge = i
    return nearest_edge, min_distance

# Split edge by point
def split_edge(G, node_id, e, pnt_on_line, buffer_size):
    pnt_on_line_b = pnt_on_line.buffer(buffer_size)
    first_seg, buff_seg, last_seg = shapely.ops.split(G.edges[e]['geometry'], pnt_on_line_b).geoms
    G.edges[e]['geometry'] = shapely.LineString(list(first_seg.coords) + list(pnt_on_line.coords) + list(last_seg.coords))
    lines = shapely.ops.split(G.edges[e]['geometry'], pnt_on_line)
    p = G.nodes[e[0]]['geometry']
    line1 = filter(shapely.prepared.prep(p).intersects, lines.geoms)
    line1 = list(line1)[0]
    p = G.nodes[e[1]]['geometry']
    line2 = filter(shapely.prepared.prep(p).intersects, lines.geoms)
    line2 = list(line2)[0]
    G.add_edge(e[0], node_id, geometry=line1, length=line1.length, time=G.edges[e]['time'] * (line1.length / G.edges[e]['geometry'].length))
    G.add_edge(node_id, e[1], geometry=line2, length=line2.length, time=G.edges[e]['time'] * (line2.length / G.edges[e]['geometry'].length))
    G.remove_edge(*e)
    return G
# Check if number is similar
def is_same(a, b, treshold=0.001):
    return abs(a - b) < treshold
# Add node to network
def add_node(network, pnt, buffer_size=1e-8):
    G = network.copy()
    # Detect nearest edge
    e, dist = nearest_edge(G, pnt)
    # Detect nearest node (from within the nearest edge)
    node_id, dist = nearest_node(G.subgraph(e), pnt)
    # If 'pnt' is on edisting node -> return that node
    if dist == 0:
        return G, node_id, dist
    # Detect nearest point on the edge
    pnt_on_line = shapely.ops.nearest_points(G.edges[e]['geometry'], pnt)
    pnt_on_line = pnt_on_line[0]
    # If 'pnt_on_line' is on edisting node -> return that node
    if is_same(pnt_on_line.x, G.nodes[node_id]['geometry'].x) and is_same(pnt_on_line.y, G.nodes[node_id]['geometry'].y):
        return G, node_id, dist
    # Else - create new node
    node_ids = [i for i in G.nodes if isinstance(i, (int, float))]
    if(len(node_ids) > 0):
        node_id = min(node_ids)-1
    else:
        node_id = -1
    if node_id >= 0:
        node_id = -1
    G.add_node(node_id, geometry=pnt_on_line)
    # Split edge
    G = split_edge(G, node_id, e, pnt_on_line, buffer_size)
    e = (e[1], e[0])
    if e in G.edges and G.edges[e]['geometry'].intersects(pnt_on_line.buffer(buffer_size)):
        G = split_edge(G, node_id, e, pnt_on_line, buffer_size)
    return G, node_id, dist

# Shortest path 1 (between existing nodes)
def route1(network, node_start, node_end, weight):
    try:
        route = nx.shortest_path(network, node_start, node_end, weight)
        weight_sum = nx.path_weight(network, route, weight=weight)
        return {'route': route, 'weight': weight_sum}
    except:
        return {'route': np.nan, 'weight': np.nan}

# Shortest path 2 (inserting new nodes)
def route2(network, start, end, weight):
    network, node_start, dist_start = add_node(network, start)
    network, node_end, dist_end = add_node(network, end)
    try:
        route = nx.shortest_path(network, node_start, node_end, weight)
        weight_sum = nx.path_weight(network, route, weight=weight)
        return {'route': route, 'weight': weight_sum, 'dist_start': dist_start, 'dist_end': dist_end, 'network': network}
    except:
        return {'route': np.nan, 'weight': np.nan, 'dist_start': dist_start, 'dist_end': dist_end, 'network': network}

# Shortest path 3 (inserting new nodes + walk to nodes + comparison w/ walking mode)
def route3(network, start, end, time_weight, walking_speed=1.4): # m/s
    import math
    dist = math.sqrt(((start.x - end.x) ** 2) + ((start.y - end.y) ** 2))
    time_walking = dist / walking_speed
    try:
        result = route2(network, start, end, time_weight)
        time_driving_and_walking = result['dist_start']/walking_speed + result['weight'] + result['dist_end']/walking_speed
    except:
        return {'weight': np.nan}
    if time_driving_and_walking <= time_walking:
        return {'weight': time_driving_and_walking, 'mode': 'walking+driving'}
    else:
        return {'weight': time_walking, 'mode': 'walking'}

# Create regular grid
def create_grid(bounds, res, crs=None):
    xmin, ymin, xmax, ymax = bounds
    cols = list(np.arange(int(np.floor(xmin)), int(np.ceil(xmax+res)), res))
    rows = list(np.arange(int(np.floor(ymin)), int(np.ceil(ymax+res)), res))
    rows.reverse()
    polygons = []
    for x in cols:
        for y in rows:
            polygons.append(
                shapely.Polygon([(x,y), (x+res, y), (x+res, y-res), (x, y-res)])
            )
    grid = gpd.GeoDataFrame({'geometry': polygons}, crs=crs)
    sel = grid.intersects(shapely.box(*bounds))
    grid = grid[sel]
    return grid

# Route to 'GeoDataFrame'
def route_to_gdf(network, route, crs=None):
    route_edges = nx.path_graph(route).edges
    if len(route) == 1:
        result = []
        pnt = network.nodes[route[0]]['geometry']
        line = shapely.LineString([pnt, pnt])
        result = gpd.GeoDataFrame([{'from': route[0], 'to': route[0], 'geometry': line}], crs=crs)
    if len(route) > 1:
        result = []
        for u,v in route_edges:
            x = network.edges[u,v]['geometry']
            result.append({'from': u, 'to': v, 'geometry': x})
        result = gpd.GeoDataFrame(result, crs=crs)
    return result

# Sample data
import networkx.readwrite
G = networkx.readwrite.json_graph.node_link_graph({'directed': False, 'multigraph': False, 'graph': {'node_default': {}, 'edge_default': {}}, 'nodes': [{'geometry': 'POINT(2000 0)', 'id': '0'}, {'geometry': 'POINT(2000 1000)', 'id': '1'}, {'geometry': 'POINT(3000 1000)', 'id': '2'}, {'geometry': 'POINT(4000 1000)', 'id': '3'}, {'geometry': 'POINT(2000 2000)', 'id': '4'}, {'geometry': 'POINT(3000 2000)', 'id': '5'}, {'geometry': 'POINT(0 2000)', 'id': '6'}, {'geometry': 'POINT(1000 2000)', 'id': '7'}, {'geometry': 'POINT(4000 2000)', 'id': '8'}, {'geometry': 'POINT(2000 3000)', 'id': '9'}, {'geometry': 'POINT(3000 3000)', 'id': '10'}, {'geometry': 'POINT(4000 3000)', 'id': '11'}, {'geometry': 'POINT(2000 3500)', 'id': '12'}, {'geometry': 'POINT(500 3500)', 'id': '13'}, {'geometry': 'POINT(3500 2300)', 'id': '14'}, {'geometry': 'POINT(3500 4000)', 'id': '15'}, {'geometry': 'POINT(2000 4000)', 'id': '16'}], 'links': [{'geometry': 'LINESTRING (2000 0, 2000 1000)', 'length': 1000.0, 'source': '0', 'target': '1'}, {'geometry': 'LINESTRING (2000 1000, 3000 1000)', 'length': 1000.0, 'source': '1', 'target': '2'}, {'geometry': 'LINESTRING (2000 1000, 2000 2000)', 'length': 1000.0, 'source': '1', 'target': '4'}, {'geometry': 'LINESTRING (3000 1000, 4000 1000)', 'length': 1000.0, 'source': '2', 'target': '3'}, {'geometry': 'LINESTRING (3000 1000, 3000 2000)', 'length': 1000.0, 'source': '2', 'target': '5'}, {'geometry': 'LINESTRING (4000 1000, 4000 2000)', 'length': 1000.0, 'source': '3', 'target': '8'}, {'geometry': 'LINESTRING (1000 2000, 2000 2000)', 'length': 1000.0, 'source': '4', 'target': '7'}, {'geometry': 'LINESTRING (2000 2000, 3000 2000)', 'length': 1000.0, 'source': '4', 'target': '5'}, {'geometry': 'LINESTRING (2000 2000, 2000 3000)', 'length': 1000.0, 'source': '4', 'target': '9'}, {'geometry': 'LINESTRING (3000 2000, 4000 2000)', 'length': 1000.0, 'source': '5', 'target': '8'}, {'geometry': 'LINESTRING (3000 2000, 3000 3000)', 'length': 1000.0, 'source': '5', 'target': '10'}, {'geometry': 'LINESTRING (0 2000, 1000 2000)', 'length': 1000.0, 'source': '6', 'target': '7'}, {'geometry': 'LINESTRING (4000 2000, 4000 3000)', 'length': 1000.0, 'source': '8', 'target': '11'}, {'geometry': 'LINESTRING (2000 3000, 3000 3000)', 'length': 1000.0, 'source': '9', 'target': '10'}, {'geometry': 'LINESTRING (2000 3000, 2000 3500)', 'length': 500.0, 'source': '9', 'target': '12'}, {'geometry': 'LINESTRING (3000 3000, 4000 3000)', 'length': 1000.0, 'source': '10', 'target': '11'}, {'geometry': 'LINESTRING (2000 3500, 500 3500)', 'length': 1500.0, 'source': '12', 'target': '13'}, {'geometry': 'LINESTRING (2000 3500, 2000 4000)', 'length': 500.0, 'source': '12', 'target': '16'}, {'geometry': 'LINESTRING (3500 2300, 3500 4000)', 'length': 1700.0, 'source': '14', 'target': '15'}]})
G = prepare(G)
data = {'roads': G}