udevadm info --attribute-walk /dev/video1
udevadm test -a add $(udevadm info -q path -n /dev/vidoe1)
