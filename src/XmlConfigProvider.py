##########################################################################
# Copyright 2009 Carlos Ribeiro
#
# This file is part of Radio Tray
#
# Radio Tray is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 1 of the License, or
# (at your option) any later version.
#
# Radio Tray is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radio Tray.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################
import os
from lxml import etree
from lxml import objectify


class XmlConfigProvider:

    def __init__(self, filename):
        if(os.access(filename, os.W_OK|os.R_OK) == False):
            raise Exception('Configuration file not found: ' + filename)
        else:
            self.filename = filename


    def loadFromFile(self):
        self.root = etree.parse(self.filename).getroot()


    def saveToFile(self):
        out_file = open(self.filename, "w")
        out_file.write(etree.tostring(self.root, method='xml', encoding='UTF-8', pretty_print=True))
        out_file.close()


    def getConfigValue(self, name):
        result = self.root.xpath("//option[@name=$var]/@value", var=name)
        if(len(result) >= 1):
            return result[0]


    def setConfigValue(self, name, value):
        
        setting = self._settingExists(name)

        if (setting == None):
            setting = etree.SubElement(self.root, 'option')
            setting.set("name", name)
            setting.set("value", value)
        else:
            setting.set("value", value)
            
        self.saveToFile()


    def _settingExists(self, name):
        setting = None

        try:
            setting = self.root.xpath("//option[@name=$var]", var=name)[0]
        except IndexError, e:
            # Setting wasn't found
            print "Could not find setting with the name \"%s\"." % name

        return setting
