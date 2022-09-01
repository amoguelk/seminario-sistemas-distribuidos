#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 rzavalet <rzavalet@noemail.com>
#
# Distributed under terms of the MIT license.


"""
This class represents a Resource (or a record) that is stored in one of the
nodes of the datastore.
"""
class Resource:
    def __init__(self, name):
        self.name = name


"""
This class represents a Node, the place were resources (or records) are stored
in the datastore.
"""
class Node:
    def __init__(self, name):
        self.name = name
        self.resources = []


"""
The class Store represents a distributed datastore. Each datastore stores a
number of resources. Resources are assigned to nodes based on a hash schema.
"""
class Store:
    def __init__(self, hash_generator):
        self.nodes = {}
        self.hash_generator = hash_generator

    def dump(self):
        """
        Prints the contents of each of the nodes that make up the distributed
        datastore.
        """
        print("===== STORE =====")
        print("Using scheme: {0}".format(self.hash_generator.get_name()))
        self.hash_generator.dump()
        for node in self.nodes.keys():
            print('[{0} ({1} items)]'.format(self.nodes[node].name, len(self.nodes[node].resources)))
            for resource in self.nodes[node].resources:
                print('    - {0}'.format(resource))

    def add_node(self, new_node):
        """
        Creates a new node in the datastore. Once the node is created, a number
        of resources have to be migrated to conform to the hash schema.

        Important: Notice that this method is designed to work with a
        consistent hash. You may need to adjust it to make it work with modular
        hash. Hash_generator has a member "scheme_name" that you can use.
        """
        generator = self.hash_generator.get_name()
        dataMovedCounter = 0
        nodeExists = False
        # ---  CHash ---
        if(generator == "Consistent_Hash"):
            prev_node = self.hash_generator.hash(new_node)

            rc = self.hash_generator.add_node(new_node)
            if rc == 0:
                self.nodes[new_node] = Node(new_node)

                """
                If there is a node in the counter clockwise direction, then the
                resources stored in that node need to be rebalanced (removed from a
                node and added to another one).
                """
                if prev_node is not None:
                    resources = self.nodes[prev_node].resources.copy()

                    for element in resources:
                        target_node = self.hash_generator.hash(element)

                        if target_node is not None and target_node != prev_node:
                            # Data has to be moved
                            self.nodes[prev_node].resources.remove(element)
                            self.nodes[target_node].resources.append(element)
                            dataMovedCounter += 1
        # --- ModHash ---
        elif(generator == "Modular_Hash"):
            # Check if it already exists
            for n in self.nodes.values():
                nodeExists = n.name == new_node
                if nodeExists:
                    break
            
            # We can only add if it doesn't exist
            if (not nodeExists):
                self.hash_generator.add_node(new_node)
                currentResources = []
                currentNodes = []

                for n in self.nodes.values():
                    currentResources += n.resources                

                for n in self.nodes.values():
                    currentNodes.append(n.name)
                # Add the new node
                currentNodes.append(new_node)

                # Empty node dictionary to reorganize
                self.nodes = {}
                for key, n in enumerate(currentNodes):
                    self.nodes[key] = Node(n)
                # Add all resources again
                dataMovedCounter = len(currentResources)
                for r in currentResources:
                    self.add_resource(r)

        # --- Opción por defecto para proteger de errores ---
        else:
            pass
        
        return dataMovedCounter

    def remove_node(self, node):
        """
        Removes a node from the datastore. When a node is removed, a number
        of resources (that were stored in that node) have to be migrated to
        conform to the hash schema.

        Important: Notice that this method is designed to work with a
        consistent hash. You may need to adjust it to make it work with modular
        hash. Hash_generator has a member "scheme_name" that you can use.
        """
        generator = self.hash_generator.get_name()
        dataMovedCounter = 0
        nodeExists = False

        # --- CHash ---
        if(generator == "Consistent_Hash"):
            rc = self.hash_generator.remove_node(node)
            if rc == 0:
                for element in self.nodes[node].resources:
                    # Data that needs to be relocated
                    self.add_resource(element)
                    dataMovedCounter += 1
                del self.nodes[node]
        # --- ModHash ---
        elif(generator == "Modular_Hash"):
             # Check if it already exists
            for n in self.nodes.values():
                nodeExists = n.name == node
                if nodeExists:
                    break
            
            # Can only be removed if it exists
            if (nodeExists):
                self.hash_generator.remove_node(node)
                currentResources = []
                currentNodes = []

                # Save all existing resources
                for n in self.nodes.values():
                    currentResources += n.resources                

                for n in self.nodes.values():
                    # Save all existing nodes except the one being removed
                    if(n.name != node):
                        currentNodes.append(n.name)
                
                # Empty node dictionary to reorganize
                self.nodes = {}
                for key, n in enumerate(currentNodes):
                    self.nodes[key] = Node(n)
                # Add all resources again
                dataMovedCounter = len(currentResources)
                for r in currentResources:
                    self.add_resource(r)
        # --- Opción por defecto para proteger de errores ---
        else:
            pass
        
        return dataMovedCounter


    def add_resource(self, res):
        """
        Add a new resource (record) to the distributed datastore. The record is
        added to a node that is selected using the hash strategy.
        """
        target_node = self.hash_generator.hash(res)

        if target_node is not None:
            self.nodes[target_node].resources.append(res)
