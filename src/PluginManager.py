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

from lib.common import USER_PLUGIN_PATH
from lib.common import SYSTEM_PLUGIN_PATH
from PluginInfo import PluginInfo
from XmlConfigProvider import XmlConfigProvider
import os
import sys

# The purpose of this class is handle all plugin lifecycle operations
class PluginManager:

    def __init__(self, notification, eventSubscriber, provider, cfgProvider, mediator, tooltip, pluginMenu):
        self.notification = notification
        self.eventSubscriber = eventSubscriber
        self.provider = provider
        self.cfgProvider = cfgProvider
        self.mediator = mediator
        self.tooltip = tooltip
        self.pluginMenu = pluginMenu
        self.pluginInfos = {}

    def getPlugins(self):
        return self.pluginInfos.values()

    def activatePlugins(self):

        active = self.cfgProvider.getConfigList('active_plugins')

        for info in self.pluginInfos.values():

            if info.name in active:
                plugin = info.instance
                #create custom config provider
                cfgProvider = None
                if(os.path.exists(info.configFile)):
                    cfgProvider = XmlConfigProvider(info.configFile)
                    cfgProvider.loadFromFile()

                plugin.initialize(info.name, self.notification, self.eventSubscriber, self.provider, cfgProvider, self.mediator, self.tooltip)

                plugin.start()
                if plugin.hasMenuItem():
                    self.pluginMenu.append(plugin.getMenuItem())            
           

            
    def activatePlugin(self, name):

        print 'activate'
        #info = self.pluginInfos[name]
        #if info != None:
        #    plugin = info.instance
            #create custom config provider
        #    cfgProvider = None
        #    if(os.path.exists(info.configFile)):
        #        cfgProvider = XmlConfigProvider(info.configFile)
        #        cfgProvider.loadFromFile()
        #    plugin.initialize(info.name, self.notification, self.eventSubscriber, self.provider, cfgProvider, self.mediator, self.tooltip)

        #    plugin.start()
        #    if plugin.hasMenuItem():
        #        self.pluginMenu.append(plugin.getMenuItem())            
            

    def deactivatePlugin(self, name):

        print 'deactivate'
        #info = self.pluginInfos[name]
        #if info != None:
        #    plugin = info.instance
        #    plugin.finalize()
        #    self.pluginMenu.remove(plugin.getMenuItem())


    def discoverPlugins(self):

        pluginFiles = []
        if os.path.exists(USER_PLUGIN_PATH):
            print "finding plugins in user plugin path"
            files = os.listdir(USER_PLUGIN_PATH)
            sys.path.insert(0,USER_PLUGIN_PATH)
            for possible_plugin in files:
                if possible_plugin.endswith('.plugin'):
                    pluginFiles.append(os.path.join(USER_PLUGIN_PATH, possible_plugin))
        else:
            print "user plugin dir does not exist. ignoring..."

        print SYSTEM_PLUGIN_PATH
        if os.path.exists(SYSTEM_PLUGIN_PATH):
            print "finding plugins in system plugin path"
            files = os.listdir(SYSTEM_PLUGIN_PATH)
            sys.path.insert(0,SYSTEM_PLUGIN_PATH)
            for possible_plugin in files:
                if possible_plugin.endswith('.plugin'):
                    pluginFiles.append(os.path.join(SYSTEM_PLUGIN_PATH, possible_plugin))
        else:
            print "system plugin dir does not exist. ignoring..."

            
        self.pluginInfos = self.parsePluginInfo(pluginFiles)


        for info in self.pluginInfos.values():
            print info.name + ", " + info.desc + ", " + info.script + ", " + info.author
            m = __import__(info.clazz)
            m2 = getattr(m, info.clazz)
            info.instance = m2()


    def parsePluginInfo(self, plugins):

        infos = {}

        for p in plugins:
            print p
            f = open(p,"r")
            text = f.read()
            lines = text.splitlines()
            pInfo = PluginInfo()

            for line in lines:
                if line.startswith('name') == True:
                    pInfo.name = line.split("=",1)[1]
                elif line.startswith('desc') == True:
                    pInfo.desc = line.split("=",1)[1]
                elif line.startswith('script') == True:
                    pInfo.script = line.split("=",1)[1]
                elif line.startswith('author') == True:
                    pInfo.author = line.split("=",1)[1]
                elif line.startswith('class') == True:
                    pInfo.clazz = line.split("=",1)[1]
            
            filename = os.path.basename(p)
            pInfo.configFile = os.path.join(os.path.dirname(p), filename[:filename.find('.')] + '.config')

            infos[pInfo.name] = pInfo
        return infos

