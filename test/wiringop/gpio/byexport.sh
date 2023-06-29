
echo 75 > /sys/class/gpio/export 2>/dev/null
cd /sys/class/gpio/gpio75
echo in > direction

while true
do
    val=$(cat value)
    if [ $val -eq 0 ]
    then
        # motion detect
        am start -a android.intent.action.VIEW -d file:///system/88love99_ok.mp4 -t video/mp4
        i=0
        while true
        do
            sleep 1
            val=$(cat value)
            if [ $val -eq 1 ]
            then
                i=`expr $i + 1`
            else
                i=0
            fi
            if [ $i -gt 3 ]
            then
                break
            fi
        done
        input keyevent 4
    fi
    sleep 5
done
