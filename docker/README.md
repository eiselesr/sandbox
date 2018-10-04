#-d, --detach Run container in background and print container ID
# --name string Assign a name to the container
# --rm Automatically remove the container when it exits
# --mount mount Attach a filesystem mount to the container
sudo docker run -d --name test --rm --mount source=input,target=/app nginx:latest

# Check status of container
sudo docker inspect test

#FULL NFS EXAMPLE
# 1.CREATE NFS Directory
sudo docker volume create --driver local --opt type=nfs --opt o=addr=129.59.105.23,rw --opt device=:/nfs/MODiCuM Directory
# 2. BUILD DOCKER IMAGE
sudo docker build --no-cache -t nfs_test .
# 3. Run Docker image with Directory mounted
sudo docker run -it --name test --mount source=Directory,target=/Directory nfs_test
