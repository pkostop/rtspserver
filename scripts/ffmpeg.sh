#RTP Generate traffic
ffmpeg -v trace -re -f lavfi -i testsrc=size=320x240:rate=25 -c:v libx264 -preset ultrafast -tune zerolatency -f rtsp rtsp://10.1.12.115:9003/push

#RTP RELAY
ffmpeg -protocol_whitelist file,udp,rtp -i test.sdp -c copy -f rtp rtp://10.1.12.115:6004?rtcpport=6005"&"localrtcpport=5005

#ffplay
ffplay -protocol_whitelist file,udp,rtp -analyzeduration 10000000 -probesize 10000000 -i test.sdp

#sdp
v=0
o=- 0 0 IN IP4 10.1.12.115
s=No Name
c=IN IP4 10.1.12.115
t=0 0
a=tool:libavformat 58.76.100
m=video 10000 RTP/AVP 96
a=rtpmap:96 H264/90000
a=fmtp:96 packetization-mode=1; sprop-parameter-sets=Z/QADZGWgUH7ARAAAAMAEAAAAwMo8UKq,aM4PGSA=; profile-level-id=F4000D
a=control:streamid=0

ffplay -v trace -protocol_whitelist file,udp,rtp,tcp -analyzeduration 10000000 -probesize 10000000 rtsp://10.1.12.115:9003/pull/1