INCLUDES=-I. -I$(srcdir) \
	$(GNOME_APPLETS_CFLAGS) \
	-DGNOMEICONDIR=\""$(prefix)/share/pixmaps"\"
	-DGNOMELOCALEDIR=\""$(prefix)/$(DATADIRNAME)/locale"\"

bin_PROGRAMS=tpbattstat-applet

tpbattstat-applet_SOURCES=tpbattstat-applet.c

tpbattstat-applet_LDADD=$(GNOME_APPLETS_LIBS)
