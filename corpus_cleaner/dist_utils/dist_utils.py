import subprocess
import os
from .yaml_template import get_yaml_template


def prepare_dist(output_dir: str):

    user = subprocess.getoutput('whoami')
    with open(os.path.join(output_dir, 'hostnames.txt'), 'r') as f:
        hosts = f.readlines()
    hosts = [l.strip() for l in hosts]
    master = hosts[0]
    slaves = hosts[1:]
    yaml = get_yaml_template(nodes=len(hosts), user=user, master=master, slaves=slaves)
    yaml_path = os.path.join(output_dir, 'ray.yaml')
    with open(yaml_path, 'w') as f:
        f.write(yaml)
    os.system(f'ray up {yaml_path}')
    for slave in slaves:
        
