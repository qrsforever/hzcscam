# Build

    git clone https://github.com/emqx/nanomq.git 
    cd nanomq
    git submodule update --init --recursive
    mkdir build && cd build
    cmake .. 
    make

# Run

    nanomq start


# Client

    pip3 install paho-mqtt

# Demo

    ${TOP_DIR}/test/nanomq
