all: callstub

callstub: callstub.o
	./encode.py callstub.o -r callstub.raw

callstub.o: callstub.s
	arm-linux-androideabi-as callstub.s -o callstub.o

.PHONY: clean
clean:
	rm -f callstub.o callstub.c callstub.js callstub.raw
