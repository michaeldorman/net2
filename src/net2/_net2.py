#!/usr/bin/python3
import numpy as np
import geopandas as gpd
import pyproj
import shapely
import networkx as nx
import osmnx as ox

def prepare_ox(N: nx.Graph):
    """
    Pre-process network returned from `ox.graph_from_place` or similar `osmnx` function
    
    Parameters
    ----------
    network : `networkx` graph
        Network

    Returns
    -------
    `networkx` graph
        Modified network
    """
    N = N.copy()
    N = ox.add_edge_speeds(N)
    N = ox.add_edge_travel_times(N)
    N = ox.convert.to_digraph(N, weight='travel_time')
    N = prepare(N)
    for i in N.nodes:
        N.nodes[i]['geometry'] = shapely.Point(N.nodes[i]['x'], N.nodes[i]['y'])
    for u,v in N.edges:
        e = N.edges[u, v]
        if 'geometry' not in e:
            geom = shapely.LineString([N.nodes[u]['geometry'], N.nodes[v]['geometry']])
            N[u][v]['geometry'] = geom
    keep = ['geometry']
    for i in N.nodes:
        for attr in list(N.nodes[i].keys()):
            if attr not in keep: 
                del N.nodes[i][attr]
    keep = ['geometry', 'length', 'speed_kph', 'time']
    for u,v in N.edges:
        for attr in list(N.edges[u,v].keys()):
            if attr not in keep: 
                del N.edges[u,v][attr]
    for u,v in N.edges:
        N[u][v]['speed'] = N[u][v]['speed_kph']
        del N[u][v]['speed_kph']
    N = transform(N, 3857)
    return N

def prepare(N: nx.Graph, ids_to_int=True):
    """
    Standardize spatial `networkx` network object
    
    Parameters
    ----------
    network : `networkx` graph
        Network
    ids_to_int: `bool` 
        Whether to replace node IDs with `int`

    Returns
    -------
    `networkx` graph
        Modified network
    """
    N = N.copy()
    if 'crs' not in N.graph:
        N.graph['crs'] = None
    else:
        if isinstance(N.graph['crs'], str):
            if N.graph['crs'] == 'None':
                N.graph['crs'] = None
            else:
                try:
                    N.graph['crs'] = int(N.graph['crs'].replace('epsg:', ''))
                except Exception as e: 
                    print("'crs' graph attribute is invalid")
                    print(e)
    if ids_to_int:
        try:
            mapping = {i: int(i) for i in N.nodes}
            N = nx.relabel_nodes(N, mapping)
        except:
            N = nx.convert_node_labels_to_integers(N, first_label=0)
    for i in N.nodes:
        if 'geometry' in N.nodes[i]:
            if isinstance(N.nodes[i]['geometry'], str):
                N.nodes[i]['geometry'] = shapely.from_wkt((N.nodes[i]['geometry']))
    for u,v in N.edges:
        if 'geometry' in N[u][v]:
            if isinstance(N[u][v]['geometry'], str):
                N[u][v]['geometry'] = shapely.from_wkt((N[u][v]['geometry']))
        if 'length' in N[u][v]:
            N[u][v]['length'] = float(N[u][v]['length'])
        if 'travel_time' in N[u][v]:
            N[u][v]['time'] = N[u][v]['travel_time']
            del N[u][v]['travel_time']
        if 'time' in N[u][v]:
            N[u][v]['time'] = float(N[u][v]['time'])
    return N

def pos(N: nx.Graph):
    """
    Nenerate `dict` with node coordinates, to be passed to `pos` parameter of `nx.draw`
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    
    Returns
    -------
    `dict`
        Node `[x,y]` positions
    """
    return {i: [N.nodes[i]['geometry'].x, N.nodes[i]['geometry'].y] for i in N.nodes}

def nodes_to_gdf(N: nx.Graph):
    """
    Extract network nodes as a `GeoDataFrame`

    Parameters
    ----------
    N : `networkx` graph
        Network

    Returns
    -------
    `GeoDataFrame`
        Point layer of the network nodes
    """
    geom = []
    node_id = []
    for i in N.nodes:
        node_id.append(i)
        geom.append(N.nodes[i]['geometry'])
    nodes = gpd.GeoDataFrame({'id':node_id, 'geometry':geom}, crs=N.graph['crs'])
    return nodes

def edges_to_gdf(N: nx.Graph):
    """
    Extract network edges as a `GeoDataFrame`

    Parameters
    ----------
    N : `networkx` graph
        Network

    Returns
    -------
    `GeoDataFrame`
        Line layer of the network edges
    """
    edges = nx.to_pandas_edgelist(N)
    edges = gpd.GeoDataFrame(edges, crs=N.graph['crs'])
    return edges

def nearest_node(N: nx.Graph, geom: shapely.geometry.base.BaseGeometry) -> tuple:
    """
    Find the nearest network node to the specified geometry
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    geom : `shapely` geometry
        Point

    Returns
    -------
    `tuple`
        ID of the nearest node
    """
    min_distance = float('inf')
    nearest_node = None
    for i in N.nodes:
        distance = geom.distance(N.nodes[i]['geometry'])
        if distance < min_distance:
            min_distance = distance
            nearest_node = i
    return nearest_node, min_distance

def nearest_edge(N: nx.Graph, geom: shapely.geometry.base.BaseGeometry) -> tuple:
    """
    Find the nearest network edge to the specified geometry
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    pnt : `shapely` geometry
        Point

    Returns
    -------
    `tuple`
        ID of the nearest edge
    """
    min_distance = float('inf')
    nearest_edge = None
    for i in N.edges:
        geom_edge = N.edges[i]['geometry']
        distance = geom.distance(geom_edge)
        if distance < min_distance:
            min_distance = distance
            nearest_edge = i
    return nearest_edge, min_distance

def split_edge(N: nx.Graph, node_id, e, pnt_on_line: shapely.geometry.Point, buffer_size):
    pnt_on_line_b = pnt_on_line.buffer(buffer_size)
    first_seg, buff_seg, last_seg = shapely.ops.split(N.edges[e]['geometry'], pnt_on_line_b).geoms
    N.edges[e]['geometry'] = shapely.LineString(list(first_seg.coords) + list(pnt_on_line.coords) + list(last_seg.coords))
    lines = shapely.ops.split(N.edges[e]['geometry'], pnt_on_line)
    p = N.nodes[e[0]]['geometry']
    line1 = filter(p.intersects, lines.geoms)
    line1 = list(line1)[0]
    p = N.nodes[e[1]]['geometry']
    line2 = filter(p.intersects, lines.geoms)
    line2 = list(line2)[0]
    N.add_edge(e[0], node_id, geometry=line1, length=line1.length, time=N.edges[e]['time'] * (line1.length / N.edges[e]['geometry'].length))
    N.add_edge(node_id, e[1], geometry=line2, length=line2.length, time=N.edges[e]['time'] * (line2.length / N.edges[e]['geometry'].length))
    N.remove_edge(*e)
    return N

def is_same(a, b, threshold=0.001):
    return abs(a - b) < threshold

def add_node(N: nx.Graph, pnt: shapely.geometry.Point, buffer_size=1e-8):
    """
    Insert new node into an edge
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    pnt : `shapely` point geometry
        Point indicating where to insert a new node on the nearest edge
    buffer_size: `int` or `float` 
        Buffer around snapped point on edge geometry

    Returns
    -------
    `networkx` graph
        Modified network
    """
    N = N.copy()
    # Detect nearest edge
    edge_id, dist_to_edge = nearest_edge(N, pnt)
    # Detect nearest node (from within the nearest edge)
    node_id, dist_to_node = nearest_node(N.subgraph(edge_id), pnt)
    # If 'pnt' is on existing node -> return that node
    if dist_to_node == 0:
        return N, node_id, dist_to_node
    # Detect nearest point on the edge
    pnt_on_line = shapely.ops.nearest_points(N.edges[edge_id]['geometry'], pnt)
    pnt_on_line = pnt_on_line[0]
    # If 'pnt_on_line' is on existing node -> return that node
    if is_same(pnt_on_line.x, N.nodes[node_id]['geometry'].x) and is_same(pnt_on_line.y, N.nodes[node_id]['geometry'].y):
        return N, node_id, dist_to_node
    # Else - create new node
    node_ids = [i for i in N.nodes if isinstance(i, (int, float))]
    if(len(node_ids) > 0):
        node_id = min(node_ids)-1
    else:
        node_id = -1
    if node_id >= 0:
        node_id = -1
    N.add_node(node_id, geometry=pnt_on_line)
    # Split edge
    N = split_edge(N, node_id, edge_id, pnt_on_line, buffer_size)
    edge_id = (edge_id[1], edge_id[0])
    if edge_id in N.edges and N.edges[edge_id]['geometry'].intersects(pnt_on_line.buffer(buffer_size)):
        N = split_edge(N, node_id, edge_id, pnt_on_line, buffer_size)
    return N, node_id, dist_to_edge

def route1(N: nx.graph, node_start, node_end, weight: str):
    """
    Find optimal route between specified nodes.
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    node_start : node
        Starting node for path
    node_end : node
        Ending node for path
    weight : `str`
        Edge attribute to use as weights

    Returns
    -------
    `dict`
        A dictionary with keys: 
        *   `route` : `list` or `np.nan` 
            The nodes along calculated route 
        *   `weight` : `float` or `np.nan`
            The summed weight
    """
    try:
        route = nx.shortest_path(N, node_start, node_end, weight)
        weight_sum = nx.path_weight(N, route, weight=weight)
        return {'route': route, 'weight': weight_sum}
    except:
        return {'route': np.nan, 'weight': np.nan}

def route2(N: nx.graph, start: shapely.geometry.Point, end: shapely.geometry.Point, weight: str):
    """
    Find optimal route between specified point locations, while inserting new nodes into existing edges when necessary.
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    start : `shapely` point geometry
        Starting point for path
    end : `shapely` point geometry
        Ending point for path
    weight : `str`
        Edge attribute to use as weights

    Returns
    -------
    `dict`
        A dictionary with keys: 
        *   `route` : `list` or `np.nan` 
            The nodes along calculated route 
        *   `weight` : `float` or `np.nan`
            The summed weight
        *   `dist_start` : `float`
            The distance from `node_start` to the newly inserted node (`0` if no new nodes was inserted)
        *   `dist_end` : `float`
            The distance from `node_end` to the newly inserted node (`0` if no new nodes was inserted)
        *   `network` : `networkx` graph
            The modified network (identical to `network` if no new nodes were inserted)
    """
    network, node_start, dist_start = add_node(N, start)
    network, node_end, dist_end = add_node(network, end)
    try:
        route = nx.shortest_path(network, node_start, node_end, weight)
        weight_sum = nx.path_weight(network, route, weight=weight)
    except:
        route = np.nan
        weight_sum = np.nan
    return {
            'route': route, 
            'weight': weight_sum, 
            'dist_start': dist_start, 
            'dist_end': dist_end, 
            'network': network
        }

def route3(N: nx.graph, start: shapely.geometry.Point, end: shapely.geometry.Point, time_weight: str, walking_speed=1.4):
    """
    Find optimal route between specified point locations, while inserting new nodes into existing edges when necessary, while choosing between 'walking' (in a straight line) or 'walking+driving' (walking to and from network, then driving along network).
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    start : `shapely` point geometry
        Starting point for path
    end : `shapely` point geometry
        Ending point for path
    time_weight : `str`
        Edge attribute to use as time weights, in $sec$
    walking_speed: `float`
        Walking speed in $m/s$

    Returns
    -------
    `dict`
        A dictionary with keys: 
        *   `weight` : `float` or `np.nan`
            The summed travel time, in $sec$
        *   `mode` : `str`
            The selected travel mode, either `'walking+driving'` or `'walking'`
    """
    import math
    dist = math.sqrt(((start.x - end.x) ** 2) + ((start.y - end.y) ** 2))
    time_walking = dist / walking_speed
    try:
        result = route2(N, start, end, time_weight)
        time_driving_and_walking = result['dist_start']/walking_speed + result['weight'] + result['dist_end']/walking_speed
    except:
        return {'weight': np.nan, 'mode': np.nan}
    if time_driving_and_walking <= time_walking:
        return {'weight': time_driving_and_walking, 'mode': 'walking+driving'}
    else:
        return {'weight': time_walking, 'mode': 'walking'}

def create_grid(bounds, res, crs=None):
    """
    Create a regular grid of rectangles of size `res*res`, covering the given `bounds`

    Parameters
    ----------
    bounds : `list` or `tuple` of the form `[xmin,ymin,xmax,ymax]`, e.g., as returned by `shapely` method `.bounds`
        Network
    res : `int`
        Resolution
    crs : object, optional
        Coordinate Reference System (CRS). Can be anything accepted by `pyproj.CRS.from_user_input()`, or `None`

    Returns
    -------
    `GeoDataFrame`
        Polygonal layer of squares with side length `res`, covering the extent defined by `bounds`
    """
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

def route_to_gdf(N: nx.graph, route: list):
    """
    Convert route (`list` of node IDs) to `GeoDataFrame` with `'LineString'` geometries
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    route : `list` 
        The sequence of nodes along a route
 
    Returns
    -------
    `GeoDataFrame`
        Line layer representing the route
    """
    route_edges = nx.path_graph(route).edges
    if len(route) == 1:
        result = []
        pnt = N.nodes[route[0]]['geometry']
        line = shapely.LineString([pnt, pnt])
        result = gpd.GeoDataFrame([{'from': route[0], 'to': route[0], 'geometry': line}], crs=N.graph['crs'])
    if len(route) > 1:
        result = []
        for u,v in route_edges:
            x = N.edges[u,v]['geometry']
            result.append({'from': u, 'to': v, 'geometry': x})
        result = gpd.GeoDataFrame(result, crs=N.graph['crs'])
    return result

def transform(N: nx.graph, to_crs: int):
    """
    Transform (i.e., reproject) network to the specified Coordinate Reference System (CRS)
    
    Parameters
    ----------
    N : `networkx` graph
        Network
    to_crs : `int` 
        EPSG code of target CRS
 
    Returns
    -------
    `networkx` graph
        The transformed network
    """
    N = N.copy()
    from_crs = N.graph['crs']
    transformer = pyproj.Transformer.from_crs(from_crs, to_crs, always_xy=True)
    for i in N.nodes:
        N.nodes[i]['geometry'] = shapely.transform(N.nodes[i]['geometry'], transformer.transform, interleaved=False)
    for u,v in N.edges:
        N.edges[u, v]['geometry'] = shapely.transform(N.edges[u, v]['geometry'], transformer.transform, interleaved=False)
    N.graph['crs'] = to_crs
    return N
