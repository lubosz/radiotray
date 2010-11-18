##########################################################################
# Copyright 2010 Edward G. Bruck <ed.bruck1@gmail.com>
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


class XmlDataProvider:

    def __init__(self, filename):

        if(os.access(filename, os.W_OK|os.R_OK) == False):
            raise Exception('Bookmarks file not found: ' + filename)
        else:
            self.filename = filename

    def loadFromFile(self):
        self.root = etree.parse(self.filename).getroot()
        
        # this is necessary for the transition from the old xml to the new one
        groupRoot = self.root.xpath("//group[@name='root']")
        if len(groupRoot) == 0:

            new_group = etree.Element('group')
            new_group.set("name", "root")
            
            for child in self.root:
                child.getparent().remove(child)
                new_group.append(child)
                
            self.root.append(new_group)
            self.saveToFile()

    def saveToFile(self):
        out_file = open(self.filename, "w")
        out_file.write(etree.tostring(self.root, method='xml', encoding='UTF-8', pretty_print=True))
        out_file.close()

    def listRadioNames(self):

        return self.root.xpath("//bookmark/@name")
        
    def listGroupNames(self):
    
    	return self.root.xpath("//group/@name")

    def getRadioUrl(self, name):

        result = self.root.xpath("//bookmark[@name=$var]/@url", var=name)
        if(len(result) >= 1):
            return result[0]

    def addGroup(self, parent_group_name, new_group_name):
    
        # gettting parent group
        print "parent group : " + parent_group_name
        parent_group = self.root.xpath("//group[@name=$var]", var=parent_group_name)
        
        if parent_group != None:
            group = self.root.xpath("//group[@name=$var]", var=new_group_name)
            
            if group == None or len(group) == 0:
                print "Group is new. Saving with name " + new_group_name
                new_group = etree.SubElement(parent_group[0], 'group')
                new_group.set("name", unicode(new_group_name))
                self.saveToFile()                
                return True        
            
            print "A group with the name \"%s\" already exists." % new_group_name
            return False
        
        print "A group with the name \"%s\" does not exist." % parent_group_name
        return False


    def addRadio(self, rawName, url, group_name='root'):

        group = self.root.xpath("//group[@name=$var]", var=group_name)

        name = unicode(rawName)

        if group != None:
            # First, let us check this name hasn't been used yet.
            result = self._radioExists(name)
    
            if result is None:
                radio = etree.SubElement(group[0], 'bookmark')
                radio.set("name", unicode(name))
                radio.set("url", unicode(url))
                self.saveToFile()
                return True
            
            print "A radio with the name \"%s\" already exists." % name            
        else:
            print "A group with the name \"%s\" does not exist." % group_name
        
        return False


    def updateRadio(self, oldName, newName, url):

        # Flag used to determine if a radio gets added or not
        radioAdded = None

        result = self._radioExists(oldName)

        if result is None:
            print "Could not find a radio with the name \"%s\"." % oldName
            radioAdded = False
        else:
            if oldName == newName:
                result.set("url", unicode(url))
                self.saveToFile()
                radioAdded = True
            else:
                radioXml = self._radioExists(newName)
                if radioXml is not None:
                    print "A radio with the name \"%s\" already exists." % newName
                    radioAdded = False
                else:
                    result.set("name", unicode(newName))
                    result.set("url", unicode(url))
                    self.saveToFile()
                    radioAdded = True

        return radioAdded
        
        
    def updateGroup(self, oldName, newName):
    
        groupAdded = None
        newNameStr = unicode(newName)
        
        result = self._groupExists(oldName)
        
        if result is None:
            print "Could not find a group with the name \"%s\"." % oldName
            groupAdded = False
        else:
            if oldName != newNameStr:
                groupEx = self._groupExists(newNameStr)
                if groupEx is not None:
                    print "A group with the name \"%s\" already exists." % newName
                    groupAdded = False
                else:
                    result.set("name", unicode(newNameStr))
                    self.saveToFile()
                    groupAdded = True

        return groupAdded
                    


    def removeRadio(self, name):                
        radio = self._radioExists(name)
        
        if radio != None:
            radio.getparent().remove(radio)            
            
        else:
            group = self._groupExists(name)
            
            if group != None:
                group.getparent().remove(group)
                
        self.saveToFile()


    def moveRadio(self, name, old_group_name, new_group_name):
        old_group = self.root.xpath("//group[@name=$var]", var=old_group_name)
        new_group = self.root.xpath("//group[@name=$var]", var=new_group_name)

        if old_group != None and new_group != None:
            radioXml = self._radioExists(name)
    
            if radioXml is None:
                print "Could not find a radio with the name \"%s\"." % name
            else:                                          
                old_group[0].remove(radioXml)
                radio = etree.SubElement(new_group[0], 'bookmark')
                radio.set("name", name)
                radio.set("url", radioXml.get('url'))
                self.saveToFile()
                return True
        
        return False


    def moveUp(self, name):        
        radio = self._radioExists(name)          

        if radio != None:
            group = radio.getparent()
            previous = radio.getprevious()

            if previous != None:
                index=self.root.xpath("count(//bookmark[@name=$var]/preceding-sibling::*)+1", var=name)                       
                group.remove(radio)
                group.insert(int(index)-2,radio)
                self.saveToFile()    
                return True
        else:
            # could be a group?
            group = self.root.xpath("//group[@name=$var]", var=name)
            if group:
                parent_group = group[0].getparent()                                
                index=self.root.xpath("count(//group[@name=$var]/preceding-sibling::*)+1", var=name)                                       
                parent_group.remove(group[0])
                parent_group.insert(int(index)-2,group[0])                
                self.saveToFile()    
                return True

        return False


    def moveDown(self, name):        
        radio = self._radioExists(name)
            
        if radio != None:
            next = radio.getnext()        
            if next != None:
                group = radio.getparent()
                index=self.root.xpath("count(//bookmark[@name=$var]/preceding-sibling::*)+1", var=name)
                group.remove(radio)
                group.insert(int(index),radio)
                self.saveToFile()
                return True
        else:
            # could be a group?
            group = self.root.xpath("//group[@name=$var]", var=name)
            if group:
                parent_group = group[0].getparent()                                
                index=self.root.xpath("count(//group[@name=$var]/preceding-sibling::*)+1", var=name)                       
                parent_group.remove(group[0])
                parent_group.insert(int(index),group[0])                
                self.saveToFile()    
                return True
                        
        return False
    
    
    def _radioExists(self, name):
        radio = None

        try:
            radio = self.root.xpath("//bookmark[@name=$var]", var=name)[0]
        except IndexError, e:
            # No radio was found
            print "Could not find a radio with the name \"%s\"." % name

        return radio
        
    def _groupExists(self, name):
        group = None

        try:
            group = self.root.xpath("//group[@name=$var]", var=name)[0]
        except IndexError, e:
            # No group was found
            print "Could not find a group with the name \"%s\"." % name

        return group


    def walk_bookmarks(self, group_func, bookmark_func, user_data, group=""):
        
        children = self.root.xpath("/bookmarks" + group + "/group | " + "/bookmarks" + group + "/bookmark")
                
        for child in children:                    
            child_name  = child.get('name')
                       
            if  child.tag == 'group':                
                new_user_data = group_func(child_name, user_data)
                self.walk_bookmarks(group_func, bookmark_func, new_user_data, group + "/group[@name='"+ child_name +"']")                
            else:
                bookmark_func(child_name, user_data)
        

    def getRootGroup(self):
        return self.root.xpath("//group[@name='root']")[0]
        
        
    def updateElementGroup(self, element, group_name):
        
        group = self._groupExists(group_name)
        
        if group != None:
            old_group = element.getparent()
            old_group.remove(element)
            group.append(element)
            self.saveToFile()
        else:
            print "Could not move element group"
