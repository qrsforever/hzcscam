
# Compiler settings
CC = gcc
CFLAGS = -Wall -Wextra -Werror
# Source files
SRCS = emqx_client.c
# Object files
OBJS = $(SRCS:.c=.o)
# Executable name
TARGET = myprogram
# Build rules
all: $(TARGET)
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET)
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
clean:
	rm -f $(OBJS) $(TARGET)
