from typing import List


def get_yaml_template(nodes: int, user: str, master: str, slaves: List[str], singularity1: str, singularity2: str):
    assert nodes == 1 + len(slaves)
    slave_str = ''
    for slave in slaves:
        slave_str += slave + ','
    slave_str = '[' + slave_str[:-1] + ']'
    empty = '{}'
    curly_l = '{'
    curly_r = '}'
    return f'''# An unique identifier for the head node and workers of this cluster.
cluster_name: default

## NOTE: Typically for local clusters, min_workers == initial_workers == max_workers == len(worker_ips).

# The minimum number of workers nodes to launch in addition to the head
# node. This number should be >= 0.
# Typically, min_workers == initial_workers == max_workers == len(worker_ips).
min_workers: {nodes-1}
# The initial number of worker nodes to launch in addition to the head node.
# Typically, min_workers == initial_workers == max_workers == len(worker_ips).
initial_workers: {nodes-1}

# The maximum number of workers nodes to launch in addition to the head node.
# This takes precedence over min_workers.
# Typically, min_workers == initial_workers == max_workers == len(worker_ips).
max_workers: {nodes-1}

# Autoscaling parameters.
# Ignore this if min_workers == initial_workers == max_workers.
autoscaling_mode: default
target_utilization_fraction: 0.8
idle_timeout_minutes: 5

# This executes all commands on all nodes in the docker container,
# and opens all the necessary ports to support the Ray cluster.
# Empty string means disabled. Assumes Docker is installed.
docker:
    image: "" # e.g., tensorflow/tensorflow:1.5.0-py3
    container_name: "" # e.g. ray_docker
    # If true, pulls latest version of image. Otherwise, `docker run` will only pull the image
    # if no cached version is present.
    pull_before_run: True
    run_options: []  # Extra options to pass into "docker run"

# Local specific configuration.
provider:
    type: local
    head_ip: {master}
    worker_ips: {slave_str}

# How Ray will authenticate with newly launched nodes.
auth:
    ssh_user: {user}
    ssh_private_key: ~/.ssh/id_rsa

# Leave this empty.
head_node: {empty}

# Leave this empty.
worker_nodes: {empty}

# Files or directories to copy to the head and worker nodes. The format is a
# dictionary from REMOTE_PATH: LOCAL_PATH, e.g.
file_mounts: {curly_l}
#    "/path1/on/remote/machine": "/path1/on/local/machine",
#    "/path2/on/remote/machine": "/path2/on/local/machine",
{curly_r}

# List of commands that will be run before `setup_commands`. If docker is
# enabled, these commands will run outside the container and before docker
# is setup.
initialization_commands: []

# List of shell commands to run to set up each nodes.
setup_commands: []

# Custom commands that will be run on the head node after common setup.
head_setup_commands: []

# Custom commands that will be run on worker nodes after common setup.
worker_setup_commands: []

# Command to start ray on the head node. You don't need to change this.
head_start_ray_commands:
    - {singularity1} ray stop"
    - {singularity2} ulimit -c unlimited && ray start --head --port=6379 --autoscaling-config=~/ray_bootstrap_config.yaml"

# Command to start ray on worker nodes. You don't need to change this.
worker_start_ray_commands:
    - {singularity1} ray stop"
    - {singularity2} ray start --address={master}:6379"
'''
