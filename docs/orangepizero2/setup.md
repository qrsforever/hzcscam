
# download
    https://drive.google.com/drive/folders/1ohxfoxWJ0sv8yEHbrXL1Bu2RkBhuCMup

# default login:
  `orangepi:orangepi` change to `root: 123456`

# apt & pip
    apt update
    apt install make cmake libssl-dev
    apt install -y dnsmasq
    apt install -y python3-dev python3-pip libx264-dev libjpeg-dev
    apt install -y gstreamer1.0-tools gstreamer1.0-alsa \
         gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
         gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
         gstreamer1.0-libav gstreamer1.0-x
    apt install -y python3-gst-1.0

    pip3 install psutil pyudev paho-mqtt quart PyEmail

# gst

    gst-launch-1.0 v4l2src device=/dev/video1 io-mode=4 ! \
    video/x-raw, width=640, height=480, framerate=25/1 ! videoconvert ! \
    x264enc bframes=0 speed-preset=veryfast key-int-max=30 ! \
    flvmux streamable=true ! rtmpsink location=rtmp://srs.hzcsdata.com/live/orangepizero2?vhost=seg.30s

# issues

1. failed to create listening socket for port 53: Address already in use

```
systemctl stop systemd-resolved
systemctl disable systemd-resolved
systemctl mask systemd-resolved
```

2. No such element or plugin 'clockoverlay'

```
    apt install -y gstreamer1.0-x
```
