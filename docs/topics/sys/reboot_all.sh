ids=(02006893436a
02007cd6f4d4
02005ad1dd6c
02009aa1a989
0200b27901c5
02007d149ee3
020029a93773
020057b3d11a
0200ccb29ac7
02001c5293a6
0200975d66ba
02006d5aaab7
0200c0fd1022
0200d46a2374
02008d5bd837
0200fef465a5
0200b2e67081
020047048b2b
020054cf89d4
0200a13fc11f
0200423d7a6c)

for id in ${ids[@]}
do
    ID=${id} ./reboot.sh
done
