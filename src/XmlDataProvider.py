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


class XmlDataProvider:

	def __init__(self, filename):
		
		if(os.access(filename, os.W_OK|os.R_OK) == False):
			raise Exception('Bookmarks file not found: ' + filename)
		else:
			self.filename = filename


	def loadFromFile(self):

		self.root = etree.parse(self.filename).getroot()

	def saveToFile(self):
		out_file = open(self.filename, "w")
		out_file.write(etree.tostring(self.root, method='xml', encoding='UTF-8'))
		out_file.close()

	def listRadioNames(self):

		return self.root.xpath("//bookmark/@name")

	def getRadioUrl(self, name):

		result = self.root.xpath("//bookmark[@name=$var]/@url", var=name)
		if(len(result) == 1):
			return result[0]

	def addRadio(self, name, url):

		radio = etree.SubElement(self.root, 'bookmark')
		radio.set("name", name)
        	radio.set("url", url)
        	self.saveToFile()

	def updateRadio(self, oldName, newName, url):	

		radioXml = self.root.xpath("//bookmark[@name=$var]", var=oldName)[0]
		radioXml.set("name", unicode(newName))
		radioXml.set("url", url)
		self.saveToFile()

	def removeRadio(self, name):

		radio = self.root.xpath("//bookmark[@name=$var]", var=name)[0]
		self.root.remove(radio)
		self.saveToFile()

	def moveUp(self, name):

		radio = self.root.xpath("//bookmark[@name=$var]", var=name)[0]
		previous = radio.getprevious()
		if ( previous != None):
			index=self.root.xpath("count(//bookmark[@name=$var]/preceding-sibling::*)+1", var=name)
			self.root.remove(radio)
			self.root.insert(int(index)-2,radio)
			self.saveToFile()

			return True
		else:
			return False
		
	def moveDown(self, name):

		radio = self.root.xpath("//bookmark[@name=$var]", var=name)[0]
		next = radio.getnext()
		if ( next != None):
			index=self.root.xpath("count(//bookmark[@name=$var]/preceding-sibling::*)+1", var=name)
			self.root.remove(radio)
			self.root.insert(int(index),radio)
			self.saveToFile()

			return True
		else:
			return False
	
