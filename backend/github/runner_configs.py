from collections import OrderedDict
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Defaults:
# PROFILE = ("nyrkio-gh-runners",)
PROFILE = None  # Ended up using env vars and default profile
REGION = "eu-central-1"
AVAILABILITY_ZONE = "eu-central-1b"
OWNER = "henrik@nyrkio.com"
VPC_CIDR = "10.2.0.0/16"
SUBNET_CIDR = "10.2.0.0/24"
AMI_ID = "ami-0650ffa1687d270fc"
INSTANCE_TYPE = "c7a.large"
INSTANCE_COUNT = 1
PRIVATE_IPS = ["10.2.0.100", "10.2.0.2", "10.2.0.3", "10.2.0.4"]
SPOT_PRICE = [0.02, 0.025, 0.03, 0.035, 0.04, 0.041, 0.043, 0.045, 0.05]
KEY_NAME = "nyrkio-gh-runner-user"
SSH_KEY_FILE = "/usr/src/backend/keys/nyrkio-gh-runner-user"
SSH_USER = "ubuntu"
EBS_SIZE = 50
EBS_IOPS = 5000
LOCAL_FILES = {
    "./provisioning.sh": "/tmp/provisioning.sh",
    "github-config-command.sh": "/tmp/github-config-cmd.sh",
    "runsh_wrapper.sh": "/tmp/runsh_wrapper.sh",
    "wrapper_wrapper.sh": "/tmp/wrapper_wrapper.sh",
}
USER_DATA = "#!/bin/bash\nsudo systemctl enable ssh\nsudo systemctl start ssh\n"

INSTANCE_TYPE_NAME = "nyrkio_perf_server_2cpu_ubuntu2404"


template = {
    "profile": PROFILE,
    "region": REGION,
    "availability_zone": AVAILABILITY_ZONE,
    "owner": OWNER,
    "vpc_cidr": VPC_CIDR,
    "subnet_cidr": SUBNET_CIDR,
    "ami_id": AMI_ID,
    "instance_type": INSTANCE_TYPE,
    "instance_count": INSTANCE_COUNT,
    "private_ips": PRIVATE_IPS,
    "spot_price": SPOT_PRICE,
    "key_name": KEY_NAME,
    "ssh_key_file": SSH_KEY_FILE,
    "ssh_user": SSH_USER,
    "ebs_size": EBS_SIZE,
    "ebs_iops": EBS_IOPS,
    "local_files": LOCAL_FILES,
    "user_data": USER_DATA,
    "instance_type_name": INSTANCE_TYPE_NAME,
    "aws_access_key_id": AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
}

instance_types = OrderedDict(
    {
        INSTANCE_TYPE_NAME: {},  # Default
        "nyrkio_perf_server_4cpu_ubuntu2404": {
            "instance_type": "c7a.xlarge",
            "spot_price": "0.083",
        },
    }
)

aliases = OrderedDict(
    {
        "nyrkio_small": INSTANCE_TYPE_NAME,
        "nyrkio_perf_server_small": INSTANCE_TYPE_NAME,
        "nyrkio_perf_server": INSTANCE_TYPE_NAME,
        "nyrkio": INSTANCE_TYPE_NAME,
        "nyrkio_perf_server_medium": "nyrkio_perf_server_4cpu_ubuntu2404",
        "nyrkio_medium": "nyrkio_perf_server_4cpu_ubuntu2404",
    }
)


def gh_runner_config(instance_type=None):
    if not instance_type:
        instance_type = INSTANCE_TYPE_NAME
    if instance_type in aliases and instance_type not in instance_types:
        instance_type = aliases[instance_type]

    config = template.copy()
    config.update(instance_types[instance_type])
    return config


def supported_instance_types():
    # Order matters. We use first one to match. So we return most specific first, and smallest/cheapest instance first.
    return list(instance_types.keys()) + list(aliases.keys())
