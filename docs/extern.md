## build wiringPi

1. modify Makefile

```
diff --git a/gpio/Makefile b/gpio/Makefile
index 2ac4070..e9090f4 100755
--- a/gpio/Makefile
+++ b/gpio/Makefile
@@ -23,8 +23,8 @@
 #    along with wiringPi.  If not, see <http://www.gnu.org/licenses/>.
 #################################################################################
 
-DESTDIR?=/usr
-PREFIX?=/local
+DESTDIR?=/campi/board/
+PREFIX?=/orangepizero2
 
 ifneq ($V,1)
 Q ?= @
diff --git a/wiringPi/Makefile b/wiringPi/Makefile
index 71c38df..6297475 100755
--- a/wiringPi/Makefile
+++ b/wiringPi/Makefile
@@ -22,8 +22,8 @@
 #################################################################################
 
 VERSION=$(shell cat ../VERSION)
-DESTDIR?=/usr
-PREFIX?=/local
+DESTDIR?=/campi/board
+PREFIX?=/orangepizero2
 
 LDCONFIG?=ldconfig
 
@@ -178,7 +178,7 @@ install:    $(DYNAMIC)
        $Q echo "[Install Dynamic Lib]"
        $Q install -m 0755 -d                                           $(DESTDIR)$(PREFIX)/lib
        $Q install -m 0755 libwiringPi.so.$(VERSION)                    $(DESTDIR)$(PREFIX)/lib/libwiringPi.so.$(VERSION)
-       $Q ln -sf $(DESTDIR)$(PREFIX)/lib/libwiringPi.so.$(VERSION)     $(DESTDIR)/lib/libwiringPi.so
+       $Q ln -sr $(DESTDIR)$(PREFIX)/lib/libwiringPi.so.$(VERSION)     $(DESTDIR)$(PREFIX)/lib/libwiringPi.so
        $Q $(LDCONFIG)
 
 .PHONY:        install-deb
```

2. ./build


## build paho.mqtt.c

```
mkdir build; cd build
cmake -DPAHO_WITH_SSL=FALSE -DPAHO_ENABLE_TESTING=FALSE -DCMAKE_PREFIX_PATH=/campi/board/orangepizero2 ../
make package
```

## cjson

```
mkdir build; cd build
cmake ../-DENABLE_CJSON_TEST=Off -DENABLE_CJSON_UTILS=Off -DBUILD_SHARED_AND_STATIC_LIBS=Off -DCMAKE_INSTALL_PREFIX=/campi/board/orangepizero2/ ../

```
