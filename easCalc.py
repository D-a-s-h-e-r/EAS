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

# TO DO
# handle lines off the raster
# handle different projections VS if vcrs <> rcrs then raise warning and end
# calculate eas regardless of direction line was drawn
# handle non-line vector layer input
# add field

def main(vlayer, rlayer):

    #raster resolution
    rx = rlayer.rasterUnitsPerPixelX()
    ry = rlayer.rasterUnitsPerPixelY()

    #layer coordinate reference systems
    vcrs = vlayer.crs().authid()
    rcrs = rlayer.crs().authid()

    # establish inputs for virtual layer (olayer)
    uri = 'linestring?crs='+vcrs+'&field=id:integer&field=eas:double(10,5)'
    olayer = QgsVectorLayer(uri,  vlayer.name()+'_eas', "memory")
    pr= olayer.dataProvider()
    g = QgsFeature()

    i = 0
    # loops through all the features in vector layer
    for f in vlayer.getFeatures():

        geom = f.geometry()
        L = geom.length()
    
        pl = f.geometry().asPolyline()
    
        # compile points
        o = []

        #start point
        p = QgsGeometry.fromPoint(geom.interpolate(0).asPoint())
        c = p.asPoint()
        z = rlayer.dataProvider().identify(QgsPoint(c), QgsRaster.IdentifyFormatValue).results()[1]
        o.append('%f, %f \n'%(0, z))
    
        #mid points
        d = 0
        k = 1
        while d + min(rx, ry) < L:

            # ensure same cell is not being sampled twice
            p1 = QgsGeometry.fromPoint(geom.interpolate(d).asPoint())
            x1 = p1.centroid().asPoint().x()
            y1 = p1.centroid().asPoint().y()
        
            p2 = QgsGeometry.fromPoint(geom.interpolate(d+min(rx, ry)).asPoint())
            x2 = p2.centroid().asPoint().x()
            y2 = p2.centroid().asPoint().y()
        
            dx = abs(x1 - x2)
            dy = abs(y1 - y2)
            ds = math.sqrt(dx**2 + dy**2)

            s = min(rx, ry) * ds / max(dx, dy)

            p = QgsGeometry.fromPoint(geom.interpolate(d+s).asPoint())
            c = p.asPoint()
            z = rlayer.dataProvider().identify(QgsPoint(c), QgsRaster.IdentifyFormatValue).results()[1]
            o.append('%f, %f \n'%(d+s, z))

            d += s
            k += 1

        #end point
        p = QgsGeometry.fromPoint(geom.interpolate(L).asPoint())
        c = p.asPoint()
        z = rlayer.dataProvider().identify(QgsPoint(c), QgsRaster.IdentifyFormatValue).results()[1]
        o.append('%f, %f \n'%(L, z))
        k += 1
    
        j = 0
        a = 0

        #trapezoidal rule calculation
        while j < k - 1:
            s1 = float(o[j].split(",")[0])
            s2 = float(o[j+1].split(",")[0])
            ds = s2 - s1
            z1 = float(o[j].split(",")[1])
            z2 = float(o[j+1].split(",")[1])
            az = (z1 + z2) /2
            a += ds * az
            j += 1

        z1 = float(o[k-1].split(",")[1])
        z2 = ((2*a)/L) - z1
    
        eas = 100 * (z2 - z1)/L
        print eas
        g.setAttributes([i, eas])
        g.setGeometry(QgsGeometry.fromPolyline(pl))
        pr.addFeatures([g])

        i += 1
  
    QgsMapLayerRegistry.instance().addMapLayer(olayer)   

