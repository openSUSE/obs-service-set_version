prefix = /usr

servicedir = ${prefix}/lib/obs/service

all:

install:
	install -d $(DESTDIR)$(servicedir)
	install -m 0755 set_version $(DESTDIR)$(servicedir)
	install -m 0644 set_version.service $(DESTDIR)$(servicedir)

.PHONY: all install
