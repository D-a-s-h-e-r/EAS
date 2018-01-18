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

import os
from easCalc import main
from PyQt4 import QtGui, uic
from qgis._gui import QgsMapLayerProxyModel

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'EAS_dialog_base.ui'))


class EASDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(EASDialog, self).__init__(parent)

        self.setupUi(self)
        self.setup_gui()

        self.VL = None
        self.RL = None

        self.buttonBox.accepted.connect(self.runEAS)

    def setup_gui(self):
        self.vlayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.rlayerComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)
    
    def runEAS(self):
        self.VL = self.vlayerComboBox.currentLayer()
        self.RL = self.rlayerComboBox.currentLayer()
        main(self.VL, self.RL)
