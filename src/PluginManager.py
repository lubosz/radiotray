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


    def activatePlugins(self):

        for plugin in self.plugins:
            
            plugin.initialize("Hello World", self.notification, self.eventSubscriber, self.provider, self.cfgProvider, self.mediator, self.tooltip)

            plugin.activate()
            
           
            self.pluginMenu.append(plugin.getMenuItem())
            
            

            
