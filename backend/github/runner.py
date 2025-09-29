import boto3
import datetime
import time
import logging
from fabric import Connection


from backend.github.runner_configs import gh_runner_config
from backend.github.gh_runner_ip_list import gh_runner_allowed_ips


class RunnerLauncher(object):
    def __init__(
        self, nyrkio_user_id, nyrkio_org_id, gh_event, instance_type=None, registration_token=None
    ):
        self.registration_token = registration_token
        self.nyrkio_user_id = nyrkio_user_id
        self.nyrkio_org_id = nyrkio_org_id
        self.gh_event = gh_event
        self.instance_type = instance_type
        self.config = gh_runner_config(self.instance_type)
        self.tags = self.gh_event_to_aws_tags(self.gh_event)
        logging.info(
            f"RunnerLauncher initialized for user {self.nyrkio_user_id} with instance_type={self.instance_type}"
        )

    def gh_event_to_aws_tags(
        self, gh_event, launched_by="nyrkio/nyrkio/backend/github/runner.py"
    ):
        """
        Converts a GitHub workflow_job event JSON to AWS tag dictionaries.

        --- Example usage: ---
        Suppose you get `gh_event` from a webhook:
        tags = gh_event_to_aws_tags(gh_event, launched_by="henrikingo")
        Then, add these to your resource TagSpecifications:
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": f"nyrkio-gh-runner-{i}"},
                {"Key": "owner", "Value": OWNER},
                *tags
            ]
        }]
        """
        job = gh_event["workflow_job"]
        repo = gh_event["repository"]
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        tags = [
            {
                "Key": "github_sender",
                "Value": str(job.get("sender", {}).get("login", "")),
            },
            {"Key": "github_repo", "Value": str(repo.get("full_name", ""))},
            {"Key": "github_job_id", "Value": str(job.get("id", ""))},
            {"Key": "github_job_name", "Value": job.get("name", "")},
            {"Key": "github_job_run_id", "Value": str(job.get("run_id", ""))},
            {"Key": "github_job_run_number", "Value": str(job.get("run_number", ""))},
            {"Key": "github_job_status", "Value": job.get("status", "")},
            {"Key": "github_job_conclusion", "Value": job.get("conclusion", "")},
            {"Key": "github_job_html_url", "Value": job.get("html_url", "")},
            {"Key": "github_job_labels", "Value": ",".join(job.get("labels", []))},
            {"Key": "github_event_action", "Value": gh_event.get("action", "")},
            {
                "Key": "github_event_id",
                "Value": gh_event.get("workflow_job", {}).get("id", ""),
            },
            {
                "Key": "github_event_type",
                "Value": str(gh_event.get("workflow_job", {}).get("event", "")),
            },
            {"Key": "repo_owner", "Value": repo.get("owner", {}).get("login", "")},
            {"Key": "job_created_at", "Value": job.get("created_at", "")},
            {"Key": "launched_at", "Value": str(now)},
            {"Key": "group", "Value": "nyrkio-gh-runner"},
            {"Key": "owner", "Value": str(self.nyrkio_user_id)},
            {"Key": "billing_user", "Value": str(self.nyrkio_user_id)},
        ]
        tags = [{"Key": str(t["Key"]), "Value": str(t["Value"])} for t in tags]
        return tags

    def create_vpc(self, ec2, vpc_cidr, owner):
        vpc = ec2.create_vpc(
            CidrBlock=vpc_cidr,
            TagSpecifications=[{"ResourceType": "vpc", "Tags": self.tags}],
        )
        vpc_id = vpc["Vpc"]["VpcId"]
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={"Value": True})
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})
        return vpc_id

    def get_this_host_public_ip(self):
        response = boto3.client("ipify").get_ip_address()
        return response["ip"]

    def create_internet_gateway(self, ec2, vpc_id):
        igw = ec2.create_internet_gateway()
        igw_id = igw["InternetGateway"]["InternetGatewayId"]
        ec2.attach_internet_gateway(
            VpcId=vpc_id,
            InternetGatewayId=igw_id,
            TagSpecifications=[{"Tags": self.tags}],
        )
        return igw_id

    def create_subnet(self, ec2, vpc_id, subnet_cidr, az, owner):
        subnet = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=subnet_cidr,
            AvailabilityZone=az,
            TagSpecifications=[{"ResourceType": "subnet", "Tags": self.tags}],
        )
        return subnet["Subnet"]["SubnetId"], subnet["Subnet"]["NetworkAclAssociationId"]

    def create_route_table(self, ec2, vpc_id, igw_id, subnet_id, owner):
        rt = ec2.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[{"ResourceType": "route-table", "Tags": self.tags}],
        )
        rt_id = rt["RouteTable"]["RouteTableId"]
        ec2.create_route(
            RouteTableId=rt_id, DestinationCidrBlock="0.0.0.0/0", GatewayId=igw_id
        )
        ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
        return rt_id

    def create_network_acl(self, ec2, vpc_id, vpc_cidr, nacl_assoc_id):
        nacl = ec2.create_network_acl(
            VpcId=vpc_id,
            TagSpecifications=[{"ResourceType": "network-acl", "Tags": self.tags}],
        )
        nyrkio_com_ip = self.get_this_host_public_ip()
        allow_egress = gh_runner_allowed_ips

        nacl_id = nacl["NetworkAcl"]["NetworkAclId"]
        # Egress TCP
        for ip in allow_egress:
            ec2.create_network_acl_entry(
                NetworkAclId=nacl_id,
                RuleNumber=300,
                Protocol="6",
                RuleAction="allow",
                Egress=True,
                CidrBlock=f"{ip}/32",
                PortRange={"From": 22, "To": 22},
            )

        # Ingress
        ec2.create_network_acl_entry(
            NetworkAclId=nacl_id,
            RuleNumber=100,
            Protocol="6",
            RuleAction="allow",
            Egress=False,
            CidrBlock="{}/32".format(nyrkio_com_ip),
            PortRange={"From": 22, "To": 22},
        )
        ec2.replace_network_acl_association(
            AssociationId=nacl_assoc_id, NetworkAclId=nacl_id
        )
        return nacl_id

    def create_security_group(self, ec2, vpc_id, vpc_cidr, owner):
        sg = ec2.create_security_group(
            GroupName="nyrkio-gh-runner",
            Description="Nyrkio GitHub runner(s)",
            VpcId=vpc_id,
        )
        sg_id = sg["GroupId"]
        ec2.create_tags(Resources=[sg_id], Tags=self.tags)
        # Ingress SSH and 8080 from anywhere
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 8080,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                {
                    "IpProtocol": "-1",
                    "FromPort": 0,
                    "ToPort": 0,
                    "IpRanges": [{"CidrIp": vpc_cidr}],
                },
            ],
        )
        # Egress all
        # TODO: Monitor what is used (github motership) and then deny everything else
        ec2.authorize_security_group_egress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "-1",
                    "FromPort": 0,
                    "ToPort": 0,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        )
        return sg_id

    def request_spot_instance(
        self,
        ec2,
        ec2r,
        ami_id,
        key_name,
        instance_type,
        subnet_id,
        private_ip,
        sg_id,
        ebs_size,
        ebs_iops,
        user_data,
        owner,
        spot_price,
        instance_idx,
    ):
        launch_spec = {
            "ImageId": ami_id,
            "KeyName": key_name,
            "InstanceType": instance_type,
            "SubnetId": subnet_id,
            "PrivateIpAddress": private_ip,
            "SecurityGroupIds": [sg_id],
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "VolumeSize": ebs_size,
                        "Iops": ebs_iops,
                        "DeleteOnTermination": True,
                        "Encrypted": True,
                        "VolumeType": "gp3",
                    },
                }
            ],
            "UserData": user_data,
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": f"nyrkio-gh-runner-{instance_idx}"},
                        {"Key": "owner", "Value": owner},
                    ],
                }
            ],
        }

        response = ec2.request_spot_instances(
            SpotPrice=spot_price,
            InstanceCount=1,
            Type="one-time",
            LaunchSpecification=launch_spec,
        )
        sir_id = response["SpotInstanceRequests"][0]["SpotInstanceRequestId"]
        logging.debug(f"SpotInstanceRequestId: {sir_id}")
        # Wait for fulfillment (very basic)
        instance_id = None
        sleep_seconds = 5
        for offer_price in spot_price:
            res = ec2.describe_spot_instance_requests(SpotInstanceRequestIds=[sir_id])
            req = res["SpotInstanceRequests"][0]
            if req["State"] == "active" and "InstanceId" in req:
                instance_id = req["InstanceId"]
                logging.debug(f"Instance launched: {instance_id}")
            else:
                logging.debug(
                    f"Waiting {sleep_seconds} for spot request {sir_id} to be fulfilled..."
                )
                time.sleep(sleep_seconds)
                if req["State"] == "active" and "InstanceId" in req:
                    instance_id = req["InstanceId"]
                    logging.debug(f"Instance launched: {instance_id}")
        if instance_id is None:
            # Cancel the spot request, deploy regular on-demand instance instead
            logging.warning(
                f"Spot request {sir_id} not fulfilled, cancelling and launching on-demand instance instead..."
            )
            ec2.cancel_spot_instance_requests(SpotInstanceRequestIds=[sir_id])
            response = ec2.run_instances(launch_spec)
            if "Instances" not in response or len(response["Instances"]) == 0:
                time.sleep(5)
                raise Exception(
                    "Failed to launch on-demand instance {self.instance_type} for user {self.nyrkio_user_id}"
                )

            instance_id = response["Instances"][0]["InstanceId"]

        instance = ec2r.Instance(instance_id)
        logging.debug(
            "Waiting for instance to be in 'running' state and have a public IP address..."
        )
        instance.wait_until_running()
        for sleep_secs in [1, 5, 10, 15, 20]:
            time.sleep(sleep_seconds)
            instance.load()
            if instance.public_ip_address:
                break
            logging.debug(
                f"Waiting {sleep_seconds} for instance {instance_id} to get a public IP address..."
            )

        if not instance.public_ip_address:
            logging.warning(
                f"Instance {instance_id}, launched for {self.nyrkio_user_id} public IP is {instance.public_ip_address}"
            )

        return instance_id, instance.public_ip_address

    def provision_instance_with_fabric(
        self,
        ip_address,
        ssh_user,
        ssh_key_file,
        all_files,
        repo_owner,
        registration_token,
    ):
        logging.debug(f"Using Fabric to provision instance {ip_address} ...")
        conn = Connection(
            host=ip_address,
            user=ssh_user,
            connect_kwargs={"key_filename": ssh_key_file},
        )
        # Upload all files
        for file_name, content in all_files.items():
            logging.debug(f"Uploading {file_name} to {ip_address}")
            # Use repr to preserve newlines and special characters
            conn.run(f"echo {repr(content)} > {file_name}")
            conn.run(f"chmod +x {file_name}")
            if file_name == "provisioning.sh":
                conn.run(
                    f"echo '{repo_owner} --token {registration_token}' >> {file_name}"
                )

        # Run provisioning script
        logging.debug("Running provisioning.sh ...")
        result = conn.run("./provisioning.sh", warn=True)
        logging.debug(result.stdout)
        logging.debug("Starting run.sh in a detached screen session ...")
        result = conn.run(
            "sudo su runner -c /home/runner/wrapper_wrapper.sh", warn=True
        )
        logging.debug(result.stdout)
        return result

    def launch(self, registration_token=None):
        if registration_token:
            self.registration_token = registration_token

        REGION = self.config.get(
            "region", "eu-central-1"
        )  # Set default region if not in config

        aws_access_key_id=self.config.get("aws_access_key_id"),
        aws_secret_access_key=self.config.get("aws_secret_access_key"),
        logging.info(f"aws_access_key_id: {aws_access_key_id}")
        logging.info(f"aws_secret_access_key: {aws_secret_access_key}")
        logging.info(f"region: {REGION}")
        logging.info(f"profile: {self.config.get('profile')}")
        logging.info(f"nyrkio_user and org: {self.nyrkio_user_id}, {self.nyrkio_org_id}")

        session = boto3.Session(
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
            profile_name=self.config.get("profile"),
            region_name=REGION,
        )
        ec2 = session.client("ec2")
        ec2r = session.resource("ec2")

        vpc_id = self.create_vpc(ec2, self.config["vpc_cidr"], self.config["owner"])
        igw_id = self.create_internet_gateway(ec2, vpc_id)
        subnet_id, nacl_assoc_id = self.create_subnet(
            ec2,
            vpc_id,
            self.config["subnet_cidr"],
            self.config["availability_zone"],
            self.config["owner"],
        )
        self.create_route_table(ec2, vpc_id, igw_id, subnet_id, self.config["owner"])
        self.create_network_acl(ec2, vpc_id, self.config["vpc_cidr"], nacl_assoc_id)

        sg_id = self.create_security_group(
            ec2, vpc_id, self.config["vpc_cidr"], self.config["owner"]
        )

        all_instances = []
        for i in range(self.config["instance_count"]):
            instance_id, public_ip = self.request_spot_instance(
                ec2,
                ec2r,
                self.config["ami_id"],
                self.config["key_name"],
                self.config["instance_type"],
                subnet_id,
                self.config["private_ips"][i],
                sg_id,
                self.config["ebs_size"],
                self.config["ebs_iops"],
                self.config["user_data"],
                self.config["owner"],
                self.config["spot_price"],
                i,
            )
            self.provision_instance_with_fabric(
                public_ip,
                self.config["ssh_user"],
                self.config["ssh_key_file"],
                self.config["local_files"],
            )
            all_instances.append((instance_id, public_ip))
        self.all_instances = all_instances
        logging.info(
            f"RunnerLauncher: Successfully deployed {all_instances} of type {self.instance_type} for user {self.nyrkio_user_id}"
        )
        return all_instances


# Note: EC2 instances are provisioned to terminate on shutdown, and they will shutdwown immediately after finishing the workflow.
# Unfortunately, the VPC and related resources are not automatically deleted, so you have to periodically run a cleanup script to remove old resources.
# Example bash that uses AWS CLI:
"""
#!/bin/bash
set -e
# Cleanup old Nyrkio GH Runner VPCs and related network resources that are empty and older than 15 minutes
THRESHOLD_MINUTES=15
NOW=$(date -u +%s)
VPCS=$(aws ec2 describe-vpcs --filters "Name=tag:group,Values=nyrkio-gh-runner" --query "Vpcs[?Tags[?Key=='group' && Value=='nyrkio-gh-runner']].VpcId" --output text)
for VPC in $VPCS; do
    # Check if there are any instances in the VPC
    INSTANCE_COUNT=$(aws ec2 describe-instances --filters "Name=vpc-id,Values=$VPC" --query "Reservations[*].Instances[*].[InstanceId]" --output text | wc -l)
    if [ "$INSTANCE_COUNT" -eq 0 ]; then
        # Get the creation time of the VPC
        CREATION_TIME=$(aws ec2 describe-vpcs --vpc-ids $VPC --query "Vpcs[0].Tags[?Key=='launched_at'].Value" --output text)
        CREATION_TIMESTAMP=$(date -d "$CREATION_TIME" +%s)
        AGE_MINUTES=$(( (NOW - CREATION_TIMESTAMP) / 60 ))
        if [ "$AGE_MINUTES" -ge "$THRESHOLD_MINUTES" ]; then
            echo "Deleting VPC $VPC (age: $AGE_MINUTES minutes)"
            # Detach and delete Internet Gateway
            IGW_ID=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VPC" --query "InternetGateways[0].InternetGatewayId" --output text)
            if [ "$IGW_ID" != "None" ]; then
                aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC
                aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID
            fi
            # Delete subnets
            SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC" --query "Subnets[].SubnetId" --output text)
            for SUBNET in $SUBNETS; do
                aws ec2 delete-subnet --subnet-id $SUBNET
            done
            # Delete route tables
            RTBS=$(aws ec2 describe-route-tables --filters "Name=vpc-id           ,Values=$VPC" --query "RouteTables[].RouteTableId" --output text)
            for RTB in $RTBS; do
                aws ec2 delete-route-table --route-table-id $RTB
            done
            # Delete network ACLs
            NACLS=$(aws ec2 describe-network-acls --filters "Name=vpc-id,Values=$VPC" --query "NetworkAcls[].NetworkAclId" --output text)
            for NACL in $NACLS; do
                aws ec2 delete-network-acl --network-acl-id $NACL
            done
            # Delete security groups
            SGS=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC" --query "SecurityGroups[?GroupName!='default'].GroupId" --output text)
            for SG in $SGS; do 
               aws ec2 delete-security-group --group-id $SG; 
             done          
             # Finally, delete the VPC 
             aws ec2 delete-vpc --vpc-id $VPC
        else
            echo "VPC $VPC is only $AGE_MINUTES minutes old, skipping"
        fi
    else
        echo "VPC $VPC has $INSTANCE_COUNT instance(s), skipping"
    fi
done
"""
# Save this as cleanup_old_vpcs.sh and run it periodically, e.g. via cron
