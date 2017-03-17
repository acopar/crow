help:
	@echo "  install         install CPU version"
	@echo "  install-gpu     install GPU version"
	@echo "  uninstall       remove unwanted files"

install:
	./INSTALL_CPU.sh

install-gpu:
	./INSTALL_GPU.sh

uninstall:
	cd /usr/local/bin/ && rm crow crow-test crow-conv crow-exec crow-ssh
