INCLUDES=-I. -I$(srcdir) \
	$(GNOME_APPLETS_CFLAGS) \
	-DGNOMEICONDIR=\""$(prefix)/share/pixmaps"\"
	-DGNOMELOCALEDIR=\""$(prefix)/$(DATADIRNAME)/locale"\"

bin_PROGRAMS=tp-batt-stat-applet

tp-batt-stat-applet_SOURCES=tp-batt-stat-applet.c

tp-batt-stat-applet_LDADD=$(GNOME_APPLETS_LIBS)
