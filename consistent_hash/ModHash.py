#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 rzavalet <rzavalet@noemail.com>
#
# Distributed under terms of the MIT license.

"""
An implementation of a Hash using mod.
Please implement the requiered methods.
"""

from HashScheme import HashScheme
import hashlib

class ModHash(HashScheme):

    def __init__(self):
        """
        You have to decide what members to add to the class
        """
        self.__scheme_name = 'Modular_Hash'
        self.nodes = []

    def get_name(self):
        return self.__scheme_name

    def dump(self):
        """
        Auxiliary method to print out information about the hash
        """
        print("Number of nodes: {0}".format(len(self.nodes)))
        for n in self.nodes:
            print("\t- {0}".format(n))

    def add_node(self, new_node):
        """
        Possibly just increment a counter of number of nodes. You may also
        need to update Store to react in certain way depending on the
        scheme_name.
        """
        self.nodes.append(new_node)

    def remove_node(self, node):
        """
        Possibly just decrement a counter of number of nodes. You may also
        need to update Store to react in certain way depending on the
        scheme_name.
        """
        self.nodes.remove(node)

    def hash(self, value):
        """
        Convert value to a number representation and then obtain mod(number_of_nodes)
        """
        # Función de hasheo MD5 con hexdigest y reducida con mod 10000
        hash = (int(hashlib.md5(value.encode()).hexdigest(),16) % 10000)
        # Se usa la cantidad de nodos para calcular el modHash
        modHash = hash % len(self.nodes)
        return modHash
