https://resin.io/blog/building-arm-containers-on-any-x86-machine-even-dockerhub/

build docker arm containers 

https://blog.hypriot.com/post/setup-simple-ci-pipeline-for-arm-images/
	1. 
COPY qemu-arm-static /usr/bin/qemu-arm-static
	2. 
docker run --rm --privileged multiarch/qemu-user-static:register --reset



http://www.hotblackrobotics.com/en/blog/2018/01/22/docker-images-arm/
FROM armv7/armhf-ubuntu:16.04
