# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGYF
                                 A QGIS plugin
 Green Space Factor
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-03-01
        copyright            : (C) 2019 by C/O City
        email                : info@cocity.se
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
    """Load QGYF class from file QGYF.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgyf import QGYF
    return QGYF(iface)
