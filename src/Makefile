DIRS = gui

all:
	for i in $(DIRS); do \
	    $(MAKE) all -C $$i; \
	done

clean:
	for i in $(DIRS); do \
	    $(MAKE) clean -C $$i; \
	done
	rm -f *.pyc
