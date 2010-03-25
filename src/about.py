# -*- coding: utf-8 -*-
import gtk
from lib import i18n
import lib.common as common


def on_email(about, mail):
    gtk.show_uri(gtk.gdk.Screen(), "mailto:%s" % mail, 0L)

def on_url(about, link):
    gtk.show_uri(gtk.gdk.Screen(), link, 0L)

gtk.about_dialog_set_email_hook(on_email)
gtk.about_dialog_set_url_hook(on_url)

TRANSLATORS = _("translator-credits")

class AboutDialog(gtk.AboutDialog):
    def __init__(self, parent = None):
        gtk.AboutDialog.__init__(self)
        self.set_icon_from_file(common.APP_ICON)

        self.set_name(common.APPNAME)
        self.set_version(common.APPVERSION)
        self.set_copyright(common.COPYRIGHTS)
        self.set_logo(gtk.gdk.pixbuf_new_from_file(common.APP_ICON))
        self.set_translator_credits(TRANSLATORS)
        self.set_license(common.LICENSE)
        self.set_website(common.WEBSITE)
        self.set_website_label(_("%s's Website") % common.APPNAME)
        self.set_authors(common.AUTHORS)
        self.set_artists(common.ARTISTS)

        self.connect("response", lambda self, *args: self.destroy())
        self.show_all()
