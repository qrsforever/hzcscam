# Source

videotestsrc

# UDP

## sender

```
gst-launch-1.0 -v v4l2src device=/dev/video1 num-buffers=-1 \
    ! video/x-raw, width=640, height=480, framerate=30/1 \
    ! videoconvert ! jpegenc ! rtpjpegpay ! udpsink host=172.19.76.163 port=5200
```

```
gst-launch-1.0 v4l2src device=/dev/video1 io-mode=4 brightness=0 contrast=0 hue=0 saturation=0 \
    ! videoflip method=vertical-flip ! videoscale \
    ! video/x-raw, width=640, height=480, framerate=15/1 ! videoconvert \
    ! clockoverlay time-format="%Y/%m/%d %H:%M:%S" halignment=right valignment=top font-desc="normal 12" \
    ! textoverlay text="0200519f3bab" halignment=left valignment=top font-desc="normal 12" \
    ! x264enc bframes=0 bitrate=128 ! rtph264pay ! udpsink host=172.19.76.163 port=5200
```


## reciever

```
gst-launch-1.0 -v udpsrc port=5200 \
    ! application/x-rtp, media=video, clock-rate=90000, payload=96 \
    ! rtpjpegdepay ! jpegdec ! videoconvert ! autovideosink
```

```
gst-launch-1.0 -v udpsrc port=5200 \
    ! application/x-rtp, media=video, clock-rate=90000, payload=96 \
    ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink
```


# TCP

## server

```
gst-launch-1.0 -v v4l2src device=/dev/video1 num-buffers=-1 \
    ! video/x-raw,width=640,height=480, framerate=30/1 \
    ! videoconvert ! jpegenc ! tcpserversink host=172.19.77.100 port=5000

gst-launch-1.0 v4l2src device=/dev/video1 io-mode=4 brightness=0 contrast=0 hue=0 saturation=0 \
    ! videoflip method=vertical-flip ! videoscale ! video/x-raw, width=640, height=480, framerate=15/1 \
    ! videoconvert ! clockoverlay time-format="%Y/%m/%d %H:%M:%S" halignment=right valignment=top font-desc="normal 12" \
    ! textoverlay text="orangezero2" halignment=left valignment=top font-desc="normal 12" ! jpegenc \
    ! tcpserversink host=172.19.77.100 port=5000
```

## client

```
gst-launch-1.0 tcpclientsrc host=172.19.77.100 port=5000 ! jpegdec ! videoconvert ! autovideosink
```

# RTMP

```
gst-launch-1.0 v4l2src device=/dev/video1 io-mode=4 brightness=0 contrast=0 hue=0 saturation=0 \
    ! videoflip method=vertical-flip ! videoscale ! video/x-raw, width=640, height=480, framerate=15/1 \
    ! videoconvert ! clockoverlay time-format="%Y/%m/%d %H:%M:%S" halignment=right valignment=top font-desc="normal 12" \
    ! x264enc bframes=0 speed-preset=veryfast key-int-max=30 ! flvmux streamable=true \
    ! rtmpsink location=rtmp://srs.hzcsdata.com/live/orangezero2?vhost=seg.300s
```
