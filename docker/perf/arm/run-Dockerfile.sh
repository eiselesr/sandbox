sudo docker build -t perf .
sudo docker run --privileged --name perf_priv -it perf
