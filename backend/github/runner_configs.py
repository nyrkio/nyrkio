from collections import OrderedDict
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# Just to cap the damage of infinite loops...
MAX_RUNNERS = 7

# Defaults:
# PROFILE = ("nyrkio-gh-runners",)
PROFILE = None  # Ended up using env vars and default profile
REGION = "eu-central-1"
AVAILABILITY_ZONE = "eu-central-1b"
OWNER = "henrik@nyrkio.com"
VPC_CIDR = "10.88.0.0/16"
SUBNET_CIDR = "subnet-0a623bfe81108a1e4"
#AMI_ID = "ami-0f7a75cb49405fe04"  # Copied from runson owner id = 135269210855
AMI_ID = "ami-0d4880012d1591624"   # Jan 16
INSTANCE_TYPE = "c7a.large"
INSTANCE_COUNT = 1
PRIVATE_IPS = ["10.88.0.100", "10.88.0.2", "10.88.0.3", "10.8.0.4"]
SPOT_PRICE = [0.03, 0.035, 0.04, 0.041, 0.043, 0.045, 0.05]
KEY_NAME = "nyrkio-gh-runner-user"
SSH_KEY_FILE = "/usr/src/backend/keys/nyrkio-gh-runner-user"
SSH_USER = "ubuntu"
EBS_SIZE = 50
EBS_IOPS = 5000
# Note: The keys are actually keys in remote_scripts.all_files
LOCAL_FILES = {
    "provisioning.sh": "/tmp/provisioning.sh",
    "runsh_wrapper.sh": "/home/runner/runsh_wrapper.sh",
    "wrapper_wrapper.sh": "/home/runner/wrapper_wrapper.sh",
}
# This does two things: re-enable ssh because the base image turned it off
# Before we do anything else, schedule a shutdown to happen 60 odd minutes in the future.
# This is handy when it can be trusted to just work without any cron or message passing needed.
USER_DATA = "#!/bin/bash\nsudo systemctl enable ssh\nsudo systemctl start ssh\nsudo shutdown +62\n"

INSTANCE_TYPE_NAME = "nyrkio_perf_server_2cpu_ubuntu2404"


template = {
    "max_runners": MAX_RUNNERS,
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
        INSTANCE_TYPE_NAME: {
            "instance_type": "c7a.large",
            "price_per_hour": {"EUR": 0.2},
            "cpus": 2,
        },  # Default
        "nyrkio_perf_server_4cpu_ubuntu2404": {
            "instance_type": "c7a.xlarge",
            "price_per_hour": {"EUR": 0.4},
            "cpus": 4,
        },
        "nyrkio_perf_server_8cpu_ubuntu2404": {
            "instance_type": "c7a.2xlarge",
            "price_per_hour": {"EUR": 0.8},
            "cpus": 8,
        },
        "nyrkio_perf_server_16cpu_ubuntu2404": {
            "instance_type": "c7a.4xlarge",
            "price_per_hour": {"EUR": 1.6},
            "cpus": 16,
        },
        "nyrkio_perf_server_32cpu_ubuntu2404": {
            "instance_type": "c7a.8xlarge",
            "price_per_hour": {"EUR": 3.2},
            "cpus": 32,
        },
        "nyrkio_perf_server_64cpu_ubuntu2404": {
            "instance_type": "c7a.16xlarge",
            "price_per_hour": {"EUR": 6.4},
            "cpus": 64,
        },
        "nyrkio_perf_server_96cpu_ubuntu2404": {
            "instance_type": "c7a.24xlarge",
            "price_per_hour": {"EUR": 9.6},
            "cpus": 96,
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
        "nyrkio_perf_server_large": "nyrkio_perf_server_8cpu_ubuntu2404",
        "nyrkio_large": "nyrkio_perf_server_8cpu_ubuntu2404",
        "nyrkio_perf_server_xlarge": "nyrkio_perf_server_16cpu_ubuntu2404",
        "nyrkio_xlarge": "nyrkio_perf_server_16cpu_ubuntu2404",
        "nyrkio_perf_server_2": "nyrkio_perf_server_2cpu_ubuntu2404",
        "nyrkio_2": "nyrkio_perf_server_2cpu_ubuntu2404",
        "nyrkio_perf_server_4": "nyrkio_perf_server_4cpu_ubuntu2404",
        "nyrkio_4": "nyrkio_perf_server_4cpu_ubuntu2404",
        "nyrkio_perf_server_8": "nyrkio_perf_server_8cpu_ubuntu2404",
        "nyrkio_8": "nyrkio_perf_server_8cpu_ubuntu2404",
        "nyrkio_perf_server_16": "nyrkio_perf_server_16cpu_ubuntu2404",
        "nyrkio_16": "nyrkio_perf_server_16cpu_ubuntu2404",
        "nyrkio_perf_server_32": "nyrkio_perf_server_32cpu_ubuntu2404",
        "nyrkio_32": "nyrkio_perf_server_32cpu_ubuntu2404",
        "nyrkio_perf_server_64": "nyrkio_perf_server_64cpu_ubuntu2404",
        "nyrkio_64": "nyrkio_perf_server_64cpu_ubuntu2404",
        "nyrkio_perf_server_96": "nyrkio_perf_server_32cpu_ubuntu2404",
        "nyrkio_96": "nyrkio_perf_server_32cpu_ubuntu2404",
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
