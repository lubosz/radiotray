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
import sys

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
    import gobject
    import os
except:
    sys.exit(1)

from XmlDataProvider import XmlDataProvider
from lib import utils
from lib import i18n


class BookmarkConfiguration:

    def __init__(self, dataProvider, updateFunc):

        self.dataProvider = dataProvider
        self.updateFunc = updateFunc

        # get gui objects
        gladefile = utils.load_ui_file("configBookmarks.glade")
        self.wTree = gladefile
        self.window = self.wTree.get_object("window1")
        self.list = self.wTree.get_object("treeview1")
        self.nameEntry = self.wTree.get_object("nameEntry")
        self.urlEntry = self.wTree.get_object("urlEntry")
        self.config = self.wTree.get_object("editBookmark")

        # populate list of radios
        liststore = gtk.ListStore(str)
        for radio in self.dataProvider.listRadioNames():
            liststore.append([radio])
        self.list.set_model(liststore)
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn(_('Radio Name'), cell)
        self.list.append_column(tvcolumn)
        tvcolumn.add_attribute(cell, 'text', 0)

        # connect events
        if (self.window):
            dic = { "on_newBookmarkButton_clicked" : self.on_add_bookmark_clicked,
                "on_editBookmarkButton_clicked" : self.on_edit_bookmark_clicked,
                "on_delBookmarkButton_clicked" : self.on_remove_bookmark_clicked,
                "on_moveUpButton_clicked" : self.on_moveup_bookmark_clicked,
                "on_moveDownButton_clicked" : self.on_movedown_bookmark_clicked,
                "on_close_clickedButton_clicked" : self.on_close_clicked}
            self.wTree.connect_signals(self)

    def on_add_bookmark_clicked(self, widget):

        # reset old dialog values
        self.nameEntry.set_text('')
        self.urlEntry.set_text('')

        # show dialog
        result = self.config.run()
        if result == 2:
            name = self.nameEntry.get_text()
            url = self.urlEntry.get_text()

            if len(name) > 0 and len(url) > 0:
                self.dataProvider.addRadio(name, url)
                self.list.get_model().append([name])
            else:
                print 'No radio information provided!'
        self.config.hide()

    def on_edit_bookmark_clicked(self, widget):

        #get current selected element
        selection = self.list.get_selection()
        (model, iter) = selection.get_selected()

        if type(iter).__name__=='TreeIter':

            selectedRadioName = model.get_value(iter,0)

            #get radio bookmark details
            selectedRadioUrl = self.dataProvider.getRadioUrl(selectedRadioName)

            # populate dialog with radio information
            self.nameEntry.set_text(selectedRadioName)
            self.urlEntry.set_text(selectedRadioUrl)
            oldName = selectedRadioName

            # show dialog
            result = self.config.run()

            if result == 2:
                name = self.nameEntry.get_text()
                url = self.urlEntry.get_text()

                if len(name) > 0 and len(url) > 0:
                    model.set_value(iter,0,name)
                    self.dataProvider.updateRadio(oldName, name, url)
                else:
                    print 'No radio information provided!'
        self.config.hide()

    def on_remove_bookmark_clicked(self, widget):

        #get current selected element
        selection = self.list.get_selection()
        (model, iter) = selection.get_selected()
        print type(iter).__name__
        if type(iter).__name__=='TreeIter':

            selectedRadioName = model.get_value(iter,0)
            print selectedRadioName
            confirmation = gtk.MessageDialog(
                self.window,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_YES_NO,
                _("Are you sure you want to delete \"%s\"?") % selectedRadioName
            )

            result = confirmation.run()

            if result == -8:
                # remove from data provider
                self.dataProvider.removeRadio(selectedRadioName)

                # remove from gui
                model.remove(iter)

            confirmation.hide()

    def on_moveup_bookmark_clicked(self, widget):

        #get current selected element
        selection = self.list.get_selection()
        (model, iter) = selection.get_selected()

        if type(iter).__name__=='TreeIter':

            selectedRadioName = model.get_value(iter,0)

            if (self.dataProvider.moveUp(selectedRadioName) == True):

                path = model.get_path(iter)
                row = path[0]
                previous = model.get_iter(row -1)
                model.move_before(iter, previous)

    def on_movedown_bookmark_clicked(self, widget):

        #get current selected element
        selection = self.list.get_selection()
        (model, iter) = selection.get_selected()

        if type(iter).__name__=='TreeIter':

            selectedRadioName = model.get_value(iter,0)

            if (self.dataProvider.moveDown(selectedRadioName) == True):

                path = model.get_path(iter)
                row = path[0]
                next = model.get_iter(row + 1)
                model.move_after(iter, next)


    def on_close_clicked(self, widget):

        self.updateFunc()
        self.window.hide()

    # close the window and quit
    def on_delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

if __name__ == "__main__":
    provider = XmlDataProvider('lixo.xml')
    provider.loadFromFile()
    config = BookmarkConfiguration(provider)
    gtk.main()
