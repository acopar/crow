help:
	@echo "  install         install"
	@echo "  uninstall       remove executable files"

install:
	./INSTALL.sh

uninstall:
	cd /usr/local/bin/ && rm crow crow-test crow-conv crow-exec crow-sudo crow-start crow-stop crow-set-uid
