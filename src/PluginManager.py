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

from plugins.HelloWorldPlugin import HelloWorldPlugin
from lib.common import USER_PLUGIN_PATH
from PluginInfo import PluginInfo
import os

# The purpose of this class is handle all plugin lifecycle operations
class PluginManager:

    def __init__(self, notification, eventSubscriber, provider, cfgProvider, mediator, tooltip, pluginMenu):
        self.notification = notification
        self.eventSubscriber = eventSubscriber
        self.provider = provider
        self.cfgProvider = cfgProvider
        self.mediator = mediator
        self.tooltip = tooltip
        self.plugins = [HelloWorldPlugin()]
        self.pluginMenu = pluginMenu
        self.pluginInfos = []


    def activatePlugins(self):

        for plugin in self.plugins:
            
            plugin.initialize("Hello World", self.notification, self.eventSubscriber, self.provider, self.cfgProvider, self.mediator, self.tooltip)

            plugin.start()
            self.pluginMenu.append(plugin.getMenuItem())            
           

            
            
    def discoverPlugins(self):

        pluginFiles = []
        if os.path.exists(USER_PLUGIN_PATH):
            files = os.listdir(USER_PLUGIN_PATH)
            for possible_plugin in files:
                if possible_plugin.endswith('.plugin'):
                    pluginFiles.append(os.path.join(USER_PLUGIN_PATH, possible_plugin))
        else:
            print "plugin dir does not exist"

            
        self.pluginInfos = self.parsePluginInfo(pluginFiles)
        for info in self.pluginInfos:
            print info.name + ", " + info.desc + ", " + info.script + ", " + info.author
            execfile(os.path.join(USER_PLUGIN_PATH,info.script))


    def parsePluginInfo(self, plugins):

        infos = []

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

            infos.append(pInfo)
        return infos
