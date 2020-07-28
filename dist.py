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
    singularity1 = f'cd {work_dir}; module load singularity/3.5.2; ' \
                  f'singularity instance start --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif cc' \
                  f'singularity exec instance://cc bash -c "cd /cc/corpus-cleaner && '
    singularity2 = f'cd {work_dir}; module load singularity/3.5.2; ' \
                  f'singularity exec instance://cc bash -c "cd /cc/corpus-cleaner && '
    yaml = get_yaml_template(nodes=len(hosts), user=subprocess.getoutput('whoami'), master=master, slaves=slaves,
                             singularity1=singularity1, singularity2=singularity2)
    # singularity instance start corpuscleaner-singularity.sif prova --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output
    with open(yaml_path, 'w') as f:
        f.write(yaml)
    print(yaml_path)
