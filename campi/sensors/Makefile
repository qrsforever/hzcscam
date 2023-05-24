swmain:
	gcc -o /usr/local/bin/campi_swmain swmain.c -lpthread -lwiringPi

photoele:
	gcc -o /usr/local/bin/campi_photoele  diffuse_reflection_photoelectric.c -lpthread -lwiringPi

run:swmain
	/usr/local/bin/campi_swmain

run_photoele:photoele
	/usr/local/bin/campi_photoele

clean:
	rm -rf /usr/local/bin/campi_swmain
