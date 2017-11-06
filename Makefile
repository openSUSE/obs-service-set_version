prefix = /usr

servicedir = ${prefix}/lib/obs/service

all:

install:
	install -d $(DESTDIR)$(servicedir)
	install -m 0755 set_version $(DESTDIR)$(servicedir)
	install -m 0644 set_version.service $(DESTDIR)$(servicedir)

test:
	flake8 set_version tests/
	python -m unittest discover tests/

.PHONY: all install test
