#!/usr/bin/env python3

from this import d
from turtle import speed
import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)
    """
    data_nodes = read_osm_data(nodes_filename)
    data_ways = read_osm_data(ways_filename)

    nodes = set()
    mapping = {}
    node_info = {}
    speed_info = {}

    
    for way in data_ways:
        # filter through to the highways
        highway = way['tags'].get('highway', 0)
        if highway != 0 and highway in ALLOWED_HIGHWAY_TYPES:
            # get speed limit on this way
            speed_limit = way['tags'].get('maxspeed_mph', DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']])
            path = way['nodes']
            # add all the nodes on this path to nodes
            for node in path:
                nodes.add(node)
                     
            # find mapping of nodes on the path
            for i in range(1, len(path)):
                # for one way, map only in one direction
                if way['tags'].get('oneway', 0) == 'yes':
                    if path[i-1] in mapping.keys():
                        mapping[path[i-1]].append(path[i])
                    else:
                        mapping[path[i-1]] = [path[i]]
                # for two way, map in both directions
                else:
                    # different scenarios
                    # if both have been mapped, add nodes on to list
                    if path[i-1] in mapping.keys() and path[i] in mapping.keys():
                        mapping[path[i-1]].append(path[i])
                        mapping[path[i]].append(path[i-1])
                    # if one has been mapped
                    elif path[i-1] in mapping.keys():
                        mapping[path[i-1]].append(path[i])
                        mapping[path[i]]=[path[i-1]]
                    # if one has been mapped
                    elif path[i] in mapping.keys():
                        mapping[path[i-1]]=[path[i]]
                        mapping[path[i]].append(path[i-1])
                    # if both has not been mapped, assign to a list
                    else:
                        mapping[path[i-1]]=[path[i]]
                        mapping[path[i]]=[path[i-1]]
                
                # dictionary for mapping each two node to a speed limit
                speed_info[(path[i-1], path[i])] = speed_limit
                speed_info[(path[i], path[i-1])] = speed_limit

    # dictionary for retrieving node location through node ID
    for node in data_nodes:
        if node['id'] in nodes:
            node_info[node['id']]=(node['lat'], node['lon'])     


    return [node_info, mapping, speed_info]







def find_short_path_nodes(map_rep, node1, node2, speed=False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    node_loc = map_rep[0]
    mapping = map_rep[1]
    node_speed = map_rep[2]

    # create agenda for list of paths to explore
    agenda = [{'nodes': [node1], 'cost': 0}]
    
    # create a list of visited so we do not explore it again
    visited = set()

    # loop through until explored all the paths
    while agenda:
        # find the path with shortest distance or least time
        current = min(agenda, key=lambda k: k['cost'])
        # remove the path from agenda after explored it
        agenda.remove(current)

        # take the last node of the current path
        term_node = current['nodes'][-1] 

        # only explore nodes not visited
        if term_node not in visited:
            # if reach destination, return node
            if term_node == node2:
                    return current['nodes']
            else:
                # mark node as visited
                visited.add(term_node)

                # find node mapping
                if mapping.get(term_node, 0) != 0:
                    # loop through its children
                    for children in set(mapping[term_node]):
                        # if children not visited yet, add it to agenda
                        if children not in visited:
                            distance = great_circle_distance(node_loc[term_node], node_loc[children])
                            # looking for fastest path, times = distance/speed
                            if speed:
                                agenda.append({'nodes': [*current['nodes'], children], 'cost': current['cost']+distance/node_speed[(term_node,children)]})
                            # looking for shortest path, distance
                            else:
                             agenda.append({'nodes': [*current['nodes'], children], 'cost': current['cost']+distance})

    return None




def find_short_path(map_rep, loc1, loc2, speed = False):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    shortest_1 = float('inf')
    shortest_2 = float('inf')
    node_1 = 0
    node_2 = 0
    node_info = map_rep[0]

    # loop through each node to see which one is closest to loc1 and loc2
    for node, loc in node_info.items():
        if great_circle_distance(loc, loc1) < shortest_1:
            shortest_1 = great_circle_distance(loc, loc1)
            node_1 = node
        if great_circle_distance(loc, loc2) < shortest_2:
            shortest_2 = great_circle_distance(loc, loc2)
            node_2 = node

    # call find_short_path_nodes with parameter speed to determine to find shortest or fastest path
    path_nodes = find_short_path_nodes(map_rep, node_1, node_2, speed)
    

    # return the latitude and longitude paths of the nodes
    result = []
    if path_nodes:
        for node in path_nodes:
            result.append(node_info[node])
        
        return result
    else:
        return None
    


def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    
    
    # call previous functions with speed parameter being True
    return find_short_path(map_rep, loc1, loc2, True)


if __name__ == '__main__':
 

    # for node in data_nodes:
    #     if node['id'] in nodes:
    #         node_info[node['id']]=(node['lat'], node['lon'])
    
    # print(node_info)
    # print(mapping)

    # data = read_osm_data('resources/midwest.ways')
    # data_nodes = read_osm_data('resources/midwest.nodes')

    # shortest_1 = float('inf')
    # map_rep = build_internal_representation('resources/midwest.nodes', 'resources/midwest.ways')
    # node_info = map_rep[0]
    # for node, loc in node_info.items():
    
    #     if great_circle_distance(loc,(41.4452463, -89.3161394) ) < shortest_1:
    #         shortest_1 = great_circle_distance(loc, (41.4452463, -89.3161394))
    #         node_1 = node
    # print(node_1)
    
    # map_rep = build_internal_representation('resources/cambridge.nodes', 'resources/cambridge.ways')
    # print(find_short_path(map_rep, (42.3858, -71.0783), (42.5465, -71.1787)))
    '''
    normal is 420578 steps
    heuristic is 102459 steps
    computed by calling heurisitc function
    '''

    print(build_internal_representation('resources/mit.nodes', 'resources/mit.ways')[1])

    '''
    checkoff
    I choose to use a list of three dictionaries to map
    I could use class and objects to represent nodes instead and retrieve information
    But I chose dictionary because it takes less time to look up the keys
    My representation did change a little in that I added a dictionary for the speed along the paths

    BFS is used for unweighted paths so it would only return the path that passes
    the least number of nodes instead of distance and shortest or fastest

    The heuristic sped up the search. Without heuristic it was 420578 and 
    with heuristic it was 102459
    
    search. Without heuristic it was 42055 and 
    with heuristic it was 50704
    find fast path uses time = distance over speed as the cost while find short path uses
    only distance as the cost

    shortest path from Waltham to Salem: almost a straight line that goes through city 
    fastest path from Waltham ot Salem: not a straight line but goes on highways
    because highways are faster
    '''