#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This package implements community detection.
Package name is community but refer to python-louvain on pypi
"""

from .community_louvain import (
    partition_at_level,
    modularity,
    best_partition,
    generate_dendrogram,
    induced_graph,
    load_binary,
)
