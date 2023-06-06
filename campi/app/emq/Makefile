main:
	rm -rf out
	mkdir -p out/target
	gcc -I. \
		-I ../../../extern/wiringOP/wiringPi \
		-O2 -Wall -Wno-unused -Wno-format -DDEBUG \
		-o out/target/campi_emq \
		main.c log.c emqc.c handler.c sensors.c \
		-lpthread -lpaho-mqtt3c

run: main
	out/target/campi_emq --emq_host aiot.hzcsdata.com --emq_port 1883 -c 123456 -u campi -p 123456

.PHONY: main
