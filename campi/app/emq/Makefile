PREFIX = /campi/board/orangepizero2

main:
	rm -rf out
	mkdir -p out/target
	gcc -I$(PREFIX)/include -L$(PREFIX)/lib \
		-Wl,-rpath=$(PREFIX)/lib \
		-O2 -Wall -Wno-unused -Wno-format -DDEBUG \
		-o $(PREFIX)/bin/emqs \
		main.c log.c emqc.c syscall.c sensors.c \
		-lpthread -lpaho-mqtt3c -lwiringPi -lcjson

fifor:
	gcc -O2 -Wall -Wno-unused -Wno-format -DDEBUG fifor.c -o $(PREFIX)/bin/fifor

run: main
	$(PREFIX)/bin/emqs --emq_host aiot.hzcsdata.com --emq_port 1883 -c 123456 -u campi -p 123456

.PHONY: main
