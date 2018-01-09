help:
	@echo "  install         install CPU version"
	@echo "  install-gpu     install GPU version"
	@echo "  uninstall       remove executable files"

install:
	./INSTALL.sh

install-gpu:
	./INSTALL_GPU.sh

uninstall:
	cd /usr/local/bin/ && rm crow crow-test crow-conv crow-exec crow-ssh crow-sudo crow-start crow-stop crow-set-uid crow-set-sshkey
