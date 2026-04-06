# `net2`


## Overview

`net2` is a Python package for working with spatial networks.

## Data structures

`net2` is intended to work with spatial network data represented using
`networkx.DiGraph` object, with the following conventions:

- The network is associated with:
  - `'crs'` (`None` or `int`)
- Node IDs are `int`
- The nodes are associated with:
  - `'geometry'` (`shapely`)
- The edges are associated with:
  - `'geometry'` (`shapely`)
  - `'length'` (`float`, in $m$)
  - `'time'` (`float`, in $sec$)
