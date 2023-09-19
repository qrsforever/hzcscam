for id in $(cat ../neza/neza.txt | cut -d\  -f1)
do
    ID=${id} ./reboot.sh
done
