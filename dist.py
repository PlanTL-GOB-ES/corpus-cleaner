from corpus_cleaner.dist_utils import get_yaml_template
import sys
import subprocess
import time
import os

if __name__ == '__main__':
    work_dir = sys.argv[1]
    hosts = sys.argv[2:]
    master = hosts[0]
    slaves = hosts[1:]
    timestamp = time.strftime("%Y-%m-%d-%H%M")
    yaml_path = os.path.join('output', f'config-{timestamp}.yaml')
    singularity = f'cd {work_dir}; module load singularity/3.5.2; ' \
                  f'singularity exec --writable-tmpfs --bind $(realpath data):/cc/data --bind ' \
                  f'$(realpath output):/cc/output corpuscleaner-singularity.sif bash -c "cd /cc/corpus-cleaner && '

    yaml = get_yaml_template(nodes=len(hosts), user=subprocess.getoutput('whoami'), master=master, slaves=slaves,
                             singularity=singularity)

    with open(yaml_path, 'w') as f:
        f.write(yaml)
    print(yaml_path)
