# orangepi3-lts (`cat /etc/orangepi-release | grep "BOARD"`)

## ubuntu os

[google drive](https://drive.google.com/drive/folders/1KzyzyByev-fpZat7yvgYz1omOqFFqt1k)
[image download](http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-3-LTS.html)

## server

1. login user: `root` login password: `orangepi` change to `123456`

2. nand-sata-install (sdcard os to emmc) -- run after install all softwares is good idea

3. set wifi dhcp and reboot

    auto wlan0
    iface wlan0 inet dhcp
    wpa-ssid hzcsdata
    wpa-psk Hzcsai@123

~~4. china source `/etc/apt/sources.list`~~

    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy main restricted universe multiverse
    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-security main restricted universe multiverse
    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-updates main restricted universe multiverse
    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-backports main restricted universe multiverse

~~5. lcd~~

   apt-get install python3-smbus

~~6. systemctl service~~

   cp xxx.service /etc/systemd/system/
   systemctl enable xxx.service
   systemctl restart xxx.service

7. install apt / pip

    apt install python3-dev python3-pip libx264-dev libjpeg-dev
    
    apt install -y gstreamer1.0-tools gstreamer1.0-alsa \
         gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
         gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
         gstreamer1.0-libav

    apt install python3-gst-1.0

    test:
       gst-launch-1.0 v4l2src device=/dev/video1 io-mode=4 ! queue ! videoconvert ! x264enc bframes=0 speed-preset=veryfast key-int-max=30 ! flvmux streamable=true ! queue ! rtmpsink location=rtmp://srs.hzcsdata.com/live/orangepi3?vhost=seg.30s

8. setup wifi ap

    IFNAME="wlan0" && CON_NAME="testap" && PASSWD="test1234" \
        && nmcli connection add type wifi ifname $IFNAME con-name $CON_NAME autoconnect yes ssid $CON_NAME \
        802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PASSWD"
    nmcli connection up id testap

    journalctl  -f -u wpa_supplicant -u NetworkManager -u systemd-networkd 
    systemctl stop systemd-resolved
    systemctl disable systemd-resolved
    systemctl mask systemd-resolved
    systemctl disable systemd-resolved

# References

- https://gstreamer.freedesktop.org/documentation/tutorials/index.html?gi-language=python
- https://github.com/brettviren/pygst-tutorial-org/
- https://lazka.github.io/pgi-docs/#Gst-1.0
- https://www.cnblogs.com/xleng/tag/gstreamer/
- http://www.francescpinyol.cat/gstreamer.html

# Issues

-  [A start job is running for Raise network interface（5min 13s ）问题解决方法][3]
    /etc/systemd/system/network-online.target.wants/networking.service
        TimeoutStartSec=5min --> TimeoutStartSec=2sec

[3]: https://www.cnblogs.com/pipci/p/8537274.html

