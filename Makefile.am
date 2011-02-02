SUBDIRS=src

serverdir	= $(libdir)/bonobo/servers
server_in_files	= TPBattStatApplet_Factory.server.in
server_DATA	= $(server_in_files:.server.in=.server)
$(server_DATA):	$(server_in_files)
	sed -e "s|\@BINDIR\@|$(bindir)|" $< > $@

pixmapdir = $(datadir)/pixmaps
pixmap_DATA = myicon.svg

EXTRA_DIST = \
	$(pixmap_DATA) \
	TPBattStatApplet_Factory.server.in
