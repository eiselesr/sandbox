import os
import docker
import requests
import logging
import tqdm


def get_docker_client():
    docker_client = docker.from_env(timeout=300)
    return docker_client


def get_docker_api_client():
    docker_api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
    return docker_api_client


def login(client, username, password):
    try:
        client.login(username, password)
    except requests.exceptions.ConnectionError as e:
        logging.info(f"Try with sudo? Error is: {e}")


def build_image(client, path, tag):
    """Build docker image called <tag> from Dockerfile at <path>"""
    image = client.images.build(path=path, tag=tag)[0]
    return image


def save_image(path, tag, image):
    """Documentation is a bit flaky on this: https://github.com/docker/docker-py/issues/1595
    https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.Image.save"""
    os.makedirs(path, exist_ok=True)
    filepath = path+tag

    image_data_stream = image.save(chunk_size=None, named=True)
    with open(filepath, 'w+b') as tar_file:
        for chunk in tqdm.tqdm(image_data_stream.stream(), leave=True, miniters=1):
            tar_file.write(chunk)
    # os.system("sudo docker image save -o %s %s" %(path, tag))


def load_image(client, path):
    with open(path, 'rb', ) as tar_file:
        images = client.images.load(tar_file)
        return images


def get_image_hash(image):
    job_hash = image.id.split(":")[1]  # strip off sha256 prefix
    job_hash_int = int(job_hash, 16)
    return job_hash_int


def run_container(client, tag, name, xdict):
    container = client.containers.run(image=tag, name=name, volumes=xdict["mounts"],
                                      environment=xdict["env"], auto_remove=True,
                                      detach=True, command=xdict["command"])
    return container


def run_container_old(client, tag, name, host_input, host_output,
                      container_input, container_output, perf_enabled=False):
    if perf_enabled:
        os.system("sudo perf stat \
                    docker run --rm \
                    --mount type=bind,source=%s,target=%s\
                    --mount type=bind,source=%s,target=%s\
                    -e \"MODICUM_INPUT=%s\" \
                    -e \"MODICUM_OUTPUT=%s\" \
                    %s >> perf.log" % (host_input, container_input,
                                       host_output, container_output,
                                       container_input, container_output,
                                       tag))
    else:
        mounts = {
                    host_input: {'bind': container_input, 'mode': 'ro'},
                    host_output: {'bind': container_output, 'mode': 'rw'}
                }

        env = {
                'MODICUM_INPUT': container_input,
                'MODICUM_OUTPUT': container_output
            }
        container = client.containers.run(image=tag, name=name, volumes=mounts,
                                          environment=env, auto_remove=True,
                                          detach=True, command=["python3", "matrix.py"])
        return container


def publish_image(client, tag):
    """Publish image to Docker Trusted Registry"""
    for line in client.images.push(tag, stream=True):
        logging.info(line)


def get_image_digest(api_client, tag):
    """Get data from image. Not sure which hash to use: https://github.com/docker/distribution/issues/1662"""
    image_dict = api_client.inspect_image(tag)
    print(image_dict)
    # repoDigestSha = image_dict["RepoDigests"][0]
    image_id = image_dict["Id"].split(":")[1]
    # "Id": "sha256:bf756fb1ae65adf866bd8c456593cd24beb6a0a061dedf42b26a993176745f6b"
    # id_int = int(image_id, 16)
    # Convert image_id string into base 16 integer (e.g. 10=>16, 1f=31, 20=32)
    size = image_dict["Size"]  # in bytes
    # image_os = image_dict["Os"]
    arch = image_dict["Architecture"]
    digest = {"hash": image_id, "size": size, "arch": arch}
    return digest


def pull_image(client, tag):
    """Get Docker image from Registry"""
    try:
        image = client.images.pull(tag)
        return image
    except requests.exceptions.HTTPError as e:
        logging.info(e)
