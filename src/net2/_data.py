#!/usr/bin/python3
# Sample data
from networkx import parse_graphml
from net2._net2 import prepare
x = '''<?xml version='1.0' encoding='utf-8'?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d5" for="edge" attr.name="time" attr.type="double" />
  <key id="d4" for="edge" attr.name="speed" attr.type="long" />
  <key id="d3" for="edge" attr.name="length" attr.type="double" />
  <key id="d2" for="edge" attr.name="geometry" attr.type="string" />
  <key id="d1" for="node" attr.name="geometry" attr.type="string" />
  <key id="d0" for="graph" attr.name="crs" attr.type="string" />
  <graph edgedefault="directed">
    <node id="0">
      <data key="d1">POINT (2000 0)</data>
    </node>
    <node id="1">
      <data key="d1">POINT (2000 1000)</data>
    </node>
    <node id="2">
      <data key="d1">POINT (3000 1000)</data>
    </node>
    <node id="3">
      <data key="d1">POINT (4000 1000)</data>
    </node>
    <node id="4">
      <data key="d1">POINT (2000 2000)</data>
    </node>
    <node id="5">
      <data key="d1">POINT (3000 2000)</data>
    </node>
    <node id="6">
      <data key="d1">POINT (0 2000)</data>
    </node>
    <node id="7">
      <data key="d1">POINT (1000 2000)</data>
    </node>
    <node id="8">
      <data key="d1">POINT (4000 2000)</data>
    </node>
    <node id="9">
      <data key="d1">POINT (2000 3000)</data>
    </node>
    <node id="10">
      <data key="d1">POINT (3000 3000)</data>
    </node>
    <node id="11">
      <data key="d1">POINT (4000 3000)</data>
    </node>
    <node id="12">
      <data key="d1">POINT (2000 3500)</data>
    </node>
    <node id="13">
      <data key="d1">POINT (500 3500)</data>
    </node>
    <node id="14">
      <data key="d1">POINT (3500 2300)</data>
    </node>
    <node id="15">
      <data key="d1">POINT (3500 4000)</data>
    </node>
    <node id="16">
      <data key="d1">POINT (2000 4000)</data>
    </node>
    <edge source="0" target="1">
      <data key="d2">LINESTRING (2000 0, 2000 1000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="1" target="0">
      <data key="d2">LINESTRING (2000 0, 2000 1000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="1" target="4">
      <data key="d2">LINESTRING (2000 1000, 2000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="2" target="1">
      <data key="d2">LINESTRING (2000 1000, 3000 1000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">30</data>
      <data key="d5">120.00000000000001</data>
    </edge>
    <edge source="2" target="5">
      <data key="d2">LINESTRING (3000 1000, 3000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">30</data>
      <data key="d5">120.00000000000001</data>
    </edge>
    <edge source="3" target="2">
      <data key="d2">LINESTRING (3000 1000, 4000 1000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">30</data>
      <data key="d5">120.00000000000001</data>
    </edge>
    <edge source="3" target="8">
      <data key="d2">LINESTRING (4000 1000, 4000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">50</data>
      <data key="d5">72.0</data>
    </edge>
    <edge source="4" target="1">
      <data key="d2">LINESTRING (2000 1000, 2000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="4" target="7">
      <data key="d2">LINESTRING (1000 2000, 2000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="4" target="5">
      <data key="d2">LINESTRING (2000 2000, 3000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="4" target="9">
      <data key="d2">LINESTRING (2000 2000, 2000 3000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="5" target="4">
      <data key="d2">LINESTRING (2000 2000, 3000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="5" target="8">
      <data key="d2">LINESTRING (3000 2000, 4000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="5" target="10">
      <data key="d2">LINESTRING (3000 2000, 3000 3000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">50</data>
      <data key="d5">72.0</data>
    </edge>
    <edge source="6" target="7">
      <data key="d2">LINESTRING (0 2000, 1000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="7" target="4">
      <data key="d2">LINESTRING (1000 2000, 2000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="7" target="6">
      <data key="d2">LINESTRING (0 2000, 1000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="8" target="3">
      <data key="d2">LINESTRING (4000 1000, 4000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">50</data>
      <data key="d5">72.0</data>
    </edge>
    <edge source="8" target="5">
      <data key="d2">LINESTRING (3000 2000, 4000 2000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="8" target="11">
      <data key="d2">LINESTRING (4000 2000, 4000 3000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">50</data>
      <data key="d5">72.0</data>
    </edge>
    <edge source="9" target="4">
      <data key="d2">LINESTRING (2000 2000, 2000 3000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">90</data>
      <data key="d5">40.0</data>
    </edge>
    <edge source="9" target="10">
      <data key="d2">LINESTRING (2000 3000, 3000 3000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">50</data>
      <data key="d5">72.0</data>
    </edge>
    <edge source="9" target="12">
      <data key="d2">LINESTRING (2000 3000, 2000 3500)</data>
      <data key="d3">500.0</data>
      <data key="d4">90</data>
      <data key="d5">20.0</data>
    </edge>
    <edge source="10" target="11">
      <data key="d2">LINESTRING (3000 3000, 4000 3000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">50</data>
      <data key="d5">72.0</data>
    </edge>
    <edge source="11" target="8">
      <data key="d2">LINESTRING (4000 2000, 4000 3000)</data>
      <data key="d3">1000.0</data>
      <data key="d4">50</data>
      <data key="d5">72.0</data>
    </edge>
    <edge source="12" target="9">
      <data key="d2">LINESTRING (2000 3000, 2000 3500)</data>
      <data key="d3">500.0</data>
      <data key="d4">90</data>
      <data key="d5">20.0</data>
    </edge>
    <edge source="12" target="13">
      <data key="d2">LINESTRING (2000 3500, 500 3500)</data>
      <data key="d3">1500.0</data>
      <data key="d4">50</data>
      <data key="d5">108.0</data>
    </edge>
    <edge source="12" target="16">
      <data key="d2">LINESTRING (2000 3500, 2000 4000)</data>
      <data key="d3">500.0</data>
      <data key="d4">90</data>
      <data key="d5">20.0</data>
    </edge>
    <edge source="13" target="12">
      <data key="d2">LINESTRING (2000 3500, 500 3500)</data>
      <data key="d3">1500.0</data>
      <data key="d4">50</data>
      <data key="d5">108.0</data>
    </edge>
    <edge source="14" target="15">
      <data key="d2">LINESTRING (3500 2300, 3500 4000)</data>
      <data key="d3">1700.0</data>
      <data key="d4">50</data>
      <data key="d5">122.4</data>
    </edge>
    <edge source="15" target="14">
      <data key="d2">LINESTRING (3500 2300, 3500 4000)</data>
      <data key="d3">1700.0</data>
      <data key="d4">50</data>
      <data key="d5">122.4</data>
    </edge>
    <edge source="16" target="12">
      <data key="d2">LINESTRING (2000 3500, 2000 4000)</data>
      <data key="d3">500.0</data>
      <data key="d4">90</data>
      <data key="d5">20.0</data>
    </edge>
    <data key="d0">None</data>
  </graph>
</graphml>'''
G = parse_graphml(x)
G = prepare(G)
data = {'roads': G}