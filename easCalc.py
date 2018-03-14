# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EASDialog
                                 A QGIS plugin
 This plug-in calculates the equal area slope of a line based on its underlying topography raster
                             -------------------
        begin                : 2018-01-14
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Andrew Campbell
        email                : andrew.j.campbell@aecom.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import math
from qgis.core import (QgsVectorLayer, QgsRasterLayer, QgsMapLayerRegistry, QgsGeometry, QgsPoint, QgsRaster, QgsFeature)

# TO DO LIST

# handle lines off the raster
# handle different projections OR if vcrs <> rcrs then raise warning and end
# handle non-line vector layer input

def samplepoint(d, geom, rlayer):
    p = QgsGeometry.fromPoint(geom.interpolate(d).asPoint())
    c = p.asPoint()
    return rlayer.dataProvider().identify(QgsPoint(c), QgsRaster.IdentifyFormatValue).results()[1]

def traparea(o, k, L):
    #trapezoidal rule calculation
    a = 0
    j = 0
    while j < k - 1:
        
        s1 = float(o[j].split(",")[0])
        s2 = float(o[j+1].split(",")[0])
        ds = abs(s2 - s1)
        
        z1 = float(o[j].split(",")[1])
        z2 = float(o[j+1].split(",")[1])
        az = (z1 + z2) /2
        
        a += ds * az
        j += 1
        
    z1 = min(float(o[k-1].split(",")[1]), float(o[0].split(",")[1]))
    z2 = ((2*a)/L) - z1
    return 100 * (z2 - z1)/L

def pass_1(geom, rlayer, rs):

    L = geom.length()

    # compile points
    o = []

    #start point
    z = samplepoint(0, geom, rlayer)
    o.append('%f, %f \n'%(0, z))
        
    #mid points
    d = 0
    k = 1
    while d < L:

        # ensure same cell is not being sampled twice
        p1 = QgsGeometry.fromPoint(geom.interpolate(d).asPoint())
        x1 = p1.centroid().asPoint().x()
        y1 = p1.centroid().asPoint().y()
        
        p2 = QgsGeometry.fromPoint(geom.interpolate(d + rs).asPoint())
        x2 = p2.centroid().asPoint().x()
        y2 = p2.centroid().asPoint().y()
        
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        ds = math.sqrt(dx**2 + dy**2)

        s = rs * ds / max(dx, dy)

        if d + s >= L:
            break

        z = samplepoint(d + s, geom, rlayer)
        o.append('%f, %f \n'%(d + s, z))

        d += s
        k += 1

    #end point
    z = samplepoint(L, geom, rlayer)
    o.append('%f, %f \n'%(L, z))
    k += 1

    return traparea(o, k, L)

def pass_2(geom, rlayer, rs):

    L = geom.length()

    # compile points
    o = []

    #start point
    z = samplepoint(L, geom, rlayer)
    o.append('%f, %f \n'%(L, z))
        
    #mid points
    d = L
    k = 1
    while d > 0:

        # ensure same cell is not being sampled twice
        p1 = QgsGeometry.fromPoint(geom.interpolate(d).asPoint())
        x1 = p1.centroid().asPoint().x()
        y1 = p1.centroid().asPoint().y()
        
        p2 = QgsGeometry.fromPoint(geom.interpolate(d - rs).asPoint())
        x2 = p2.centroid().asPoint().x()
        y2 = p2.centroid().asPoint().y()
        
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        ds = math.sqrt(dx**2 + dy**2)

        s = rs * ds / max(dx, dy)

        if d - s <= 0:
            break

        z = samplepoint(d - s, geom, rlayer)
        o.append('%f, %f \n'%(d - s, z))

        d -= s
        k += 1

    #end point
    z = samplepoint(0, geom, rlayer)
    o.append('%f, %f \n'%(0, z))
    k += 1

    return traparea(o, k, L)

def main(vlayer, rlayer):

    #raster resolution
    rx = rlayer.rasterUnitsPerPixelX()
    ry = rlayer.rasterUnitsPerPixelY()
    rs = min(rx, ry)

    #layer coordinate reference systems
    vcrs = vlayer.crs().authid()
    rcrs = rlayer.crs().authid()

    # establish inputs for virtual layer (olayer)
    uri = 'linestring?crs='+vcrs+'&field=id:integer&field=eas_percent:double(10,5)'
    olayer = QgsVectorLayer(uri,  vlayer.name()+'_eas', "memory")
    pr= olayer.dataProvider()
    h = QgsFeature()
        
    i = 0
    # loops through all the features in vector layer
    for f in vlayer.getFeatures():

        geom = f.geometry()
        pl = geom.asPolyline()

        #equal area slope is an average of a forward pass and backward pass along the line
        eas1 = pass_1(geom, rlayer, rs)
        eas2 = pass_2(geom, rlayer, rs)
        eas = (eas1 + eas2) / 2
        
        # creates new geometries and populates attribute table
        h.setAttributes([i, eas])
        h.setGeometry(QgsGeometry.fromPolyline(pl))
        pr.addFeatures([h])
        
        i += 1
  
    QgsMapLayerRegistry.instance().addMapLayer(olayer)   
