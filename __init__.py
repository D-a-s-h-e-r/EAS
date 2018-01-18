# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EAS
                                 A QGIS plugin
 This plug-in calculates the equal area slope of a line based on its underlying topography raster
                             -------------------
        begin                : 2018-01-14
        copyright            : (C) 2018 by Andrew Campbell
        email                : andrew.j.campbell@aecom.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load EAS class from file EAS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .EAS import EAS
    return EAS(iface)
