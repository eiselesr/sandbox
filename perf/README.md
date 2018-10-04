On the beaglebones we were using the image by this guy: 
https://github.com/RobertCNelson/ti-linux-kernel-dev

On his readme he states:
     By default this script will clone the linux-stable tree: https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git to: ${DIR}/ignore/linux-src:

So I found our kernel version there. 
https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/tag/?h=v4.9.38

did wget on the tar
$wget https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/snapshot/linux-stable-4.9.38.tar.gz

untar-ed
$tar -xvf linux-stable-4.9.38.tar.gz

then compile, this was my reference : http://jireren.github.io/blog/2016/09/19/Compile-Perf/
cd linux-stable-4.9.38

make ARCH=arm -C tools/perf/

Instructions will work with sudo

An alternative is to use 
\cat\pro\cpuinfo 
which will give BogoMIPS
