import random

runsh_wrapper = """#!/bin/bash

# wrap around run.sh so we can
# - add logging
# - shutdown the ec2 instance after it exits
#   - it will exit if we used --ephemeral for config.sh. This was passed in bashrc
#
source /home/runner/.bashrc
./run.sh | tee -a runsh.stdout.log

echo "$(date) Done with run.sh. (It returned $?)" >> /home/runner/done
"""


wrapper_wrapper = """#!/bin/bash

# wrap around run.sh so we can
# - add logging
# - shutdown the ec2 instance after it exits
#   - it will exit if we used --ephemeral for config.sh

cd /home/runner
source /home/runner/.bashrc
screen  -dmS nyrkioGhRunner /home/runner/runsh_wrapper.sh
"""

provisioning = """#!/bin/bash

# MIT licensed
# (c) Nyrkiö Oy, 2025


echo "Enable sshd (This image has it off by default)"
sudo systemctl enable ssh
sudo systemctl start ssh

# Note: The above must be executed from user-data / userscripts.
# The below you could then ssh into the box and execute.


# configuration area:
FORMAT_EBS=TRUE
EPHEMERAL="--ephemeral"
#EPHEMERAL=""


echo "Fixes and patches"
echo "https://github.com/runs-on/runner-images-for-aws/issues/31"

# "should be"...
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
echo "PATH=/home/runner/.local/bin:/opt/pipx_bin:/home/runner/.cargo/bin:/home/runner/.config/composer/vendor/bin:/home/runner/.dotnet/tools:/snap/bin:/opt/pipx_bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin" | sudo tee -a /etc/environment

echo "export EPHEMERAL=\"$EPHEMERAL\""  | sudo tee -a /home/runner/.bashrc

sudo chown -R runner:runner /home/runner



# TODO Remove from sudoers




echo
echo "Optimize for stable and repeatable performance"
echo

# echo "Note: It's 2025, please only use single socket machines. More than 1 socket not supported."
# echo "Turn off HyperThread CPUs."
# echo "...So we turn off the upper half."
# VCPUS=$(grep "core id" /proc/cpuinfo | wc -l)
# CORES=$(grep "core id" /proc/cpuinfo | sort | uniq | wc -l)
# ON_CPUS=$(seq $(($CORES - 1)) )
# OFF_CPUS=$(seq $CORES $(($VCPUS - 1)))
#
# for N in $OFF_CPUS
# do
#    echo 0 | sudo tee /sys/devices/system/cpu/cpu$N/online
# done
echo "Using c7a instance family, it doesn't have hyper threading."

echo "Disable processor C-states"
sudo cpupower idle-set -d 2
sudo cpupower monitor
#     | Mperf              || Idle_Stats
#  CPU| C0   | Cx   | Freq  || POLL | C1   | C2
#    0|  0.50| 99.50|  3697||  0.01| 99.63|  0.00
#    1|  0.34| 99.66|  3697||  0.01| 99.80|  0.00

# TODO: For larger instances, maybe around 8xlarge or so, more options become available
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/processor_state_control.html



# More
echo 'never' | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
echo 'never' | sudo tee /sys/kernel/mm/transparent_hugepage/defrag > /dev/null

echo "Unset or set all ulimit to the max"
echo "runner           soft    nofile          65536"     | sudo tee -a /etc/security/limits.conf > /dev/null
echo "runner           hard    nofile          65536"     | sudo tee -a /etc/security/limits.conf > /dev/null
echo "runner           soft    nproc           65536"     | sudo tee -a /etc/security/limits.conf > /dev/null
echo "runner           hard    nproc           65536"     | sudo tee -a /etc/security/limits.conf > /dev/null
echo "runner           soft    core            unlimited" | sudo tee -a /etc/security/limits.conf > /dev/null
echo "runner           hard    core            unlimited" | sudo tee -a /etc/security/limits.conf > /dev/null

echo vm.max_map_count = 262144 | sudo tee -a /etc/sysctl.d/99-dsi.conf > /dev/null
sudo sysctl -w vm.max_map_count=262144


echo "/home/runner/_diag/core_files/core.\%\e.%p.%h.%t" |sudo tee -a  /proc/sys/kernel/core_pattern > /dev/null
sudo mkdir -p "/home/runner/_diag/core_files"
sudo chown -R runner:runner /home/runner



##########################################################333
LABELS=nyrkio-perf,nyrkio-perf-4vcpu,nyrkio-perf-4vcpu-ubuntu2404,ephemeral
NAME=nyrkio-perf-$\{RANDOM\}e
GROUP=nyrkio
NYRKIO_CONFIG="$EPHEMERAL --unattended --name $NAME --runnergroup $GROUP --labels $LABELS"
# GITHUB_CONFIG=$(cat /tmp/github-config-cmd.sh)
# ./config.sh --url https://github.com/nyrkio --token AAS56YW2OPRUUJJTAOZGAZDIXIM3O --ephemeral --name test4-ephemeral --runner-group nyrkio --labels nyrkio-perf,nyrkio-perf-4vcpu,nyrkio-perf-4vcpu-ubuntu2404

if [ "$EPHEMERAL" == "--ephemeral" ]
then
    echo "# This is an --ephemeral instance. Writing to crontab a check to shut doiwn the instance when run.sh marks itself as done." | sudo tee /etc/cron.d/nyrkio-github-runner-done-check

    echo "* * * * * root if [ -e /home/runner/done ]; then shutdown now; fi" | sudo tee /etc/cron.d/nyrkio-github-runner-done-check
    echo "* * * * * root sleep 3600; if [ wc -l /home/runner/runsh.stdout.log -gt 10 ]; then /bin/true; else shutdown now; fi" | sudo tee /etc/cron.d/nyrkio-github-runner-startup-check
fi

#sudo mv /tmp/runsh_wrapper.sh /home/runner/runsh_wrapper.sh
sudo chmod a+x /home/runner/runsh_wrapper.sh
#sudo mv /tmp/wrapper_wrapper.sh /home/runner/wrapper_wrapper.sh
sudo chmod a+x /home/runner/wrapper_wrapper.sh


cd /home/runner
"""


def configsh(label, repo_owner, token):
    number = random.randint(1, 99999)
    EPHEMERAL = "--ephemeral"
    # LABELS = "nyrkio-perf,nyrkio-perf-4vcpu,nyrkio-perf-4vcpu-ubuntu2404,ephemeral"
    NAME = f"nyrkio-perf-{number}"
    GROUP = "nyrkio"
    NYRKIO_CONFIG = (
        f"{EPHEMERAL} --unattended --name {NAME} --runnergroup {GROUP} --labels {label}"
    )
    return f"""cd /home/runner; sudo -u runner /home/runner/config.sh {NYRKIO_CONFIG} --url https://github.com/{repo_owner} --token {token}"""


# Append something like this in runner.py before uploading the script
# Then do: `sudo su runner -c /home/runner/wrapper_wrapper.sh`


all_scripts = {
    "/home/runner/runsh_wrapper.sh": runsh_wrapper,
    "/home/runner/wrapper_wrapper.sh": wrapper_wrapper,
    "/tmp/provisioning.sh": provisioning,
}
