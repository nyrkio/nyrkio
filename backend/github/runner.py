import base64
import boto3
import datetime
import asyncio
import logging
from fabric import Connection
from paramiko.ssh_exception import NoValidConnectionsError
import httpx
from fastapi import HTTPException

from backend.github.runner_configs import gh_runner_config
from backend.github.remote_scripts import (
    configsh,
    render_remote_files,
)
from backend.notifiers.github import fetch_access_token
from backend.github.runner_configs import supported_instance_types
from backend.db.db import DBStore

logger = logging.getLogger(__file__)


async def check_work_queue():
    store = DBStore()
    task = await store.check_work_queue("workflow_job")
    if task:
        await workflow_job_event(task["task"])
        await store.work_task_done(task)
        return task
    return None


async def workflow_job_event(queued_gh_event):
    store = DBStore()

    repo_owner = queued_gh_event["repository"]["owner"]["login"]
    repo_name = queued_gh_event["repository"]["name"]
    sender = queued_gh_event["sender"]["login"]
    org_name = None
    if "organization" in queued_gh_event and queued_gh_event["organization"]:
        org_name = queued_gh_event["organization"]["login"]
    else:
        org_name = repo_owner
    installation_id = queued_gh_event["installation"]["id"]
    labels = queued_gh_event["workflow_job"]["labels"]
    supported = supported_instance_types()
    runs_on = [lab for lab in labels if lab in supported]

    try:
        (
            runner_registration_token,
            org_or_user_repo,
        ) = await get_github_runner_registration_token(
            org_name=org_name,
            installation_id=installation_id,
            repo_full_name=f"{repo_owner}/{repo_name}",
        )
    except Exception as e:
        # Error was already logged
        logger.debug(e)
        return {
            "status": "error",
            "message": str(e),
        }

    # repo_owner is either the user or an org
    nyrkio_user = await store.get_user_by_github_username(repo_owner)
    nyrkio_org = None
    if nyrkio_user is not None:
        nyrkio_user = nyrkio_user.id
    else:
        nyrkio_user = await store.get_user_by_github_username(sender)
        if nyrkio_user is not None:
            nyrkio_user = nyrkio_user.id

    if org_name:
        nyrkio_org = await store.get_org_by_github_org(org_name, sender)
        if nyrkio_org is not None:
            nyrkio_org = nyrkio_org["organization"]["id"]
    nyrkio_billing_user = nyrkio_org if nyrkio_org else nyrkio_user

    # FIXME: Add a check for quota
    if (not nyrkio_user) and (not nyrkio_org):
        logger.warning(f"User {repo_owner} not found in Nyrkio. ({nyrkio_user})")
        raise HTTPException(
            status_code=401,
            detail="None of {org_name}/{repo_owner}/{sender} were found in Nyrkio. ({nyrkio_org}/{nyrkio_user})",
        )

    launcher = RunnerLauncher(
        nyrkio_user,
        nyrkio_org,
        nyrkio_billing_user,
        queued_gh_event,
        runs_on,
        runner_registration_token,
        org_or_user_repo,
    )
    launched_runners = await launcher.launch()
    if launched_runners:
        return_message = f"Launched an instance of type {labels}"
        return {
            "status": "success",
            "message": return_message,
            "instances": str(launched_runners),
        }
    else:
        default_message = "Thank you for using Nyrkiö. For Faster Software!"
        return {
            "status": "nothing to do",
            "message": default_message,
        }


class RunnerLauncher(object):
    def __init__(
        self,
        nyrkio_user_id,
        nyrkio_org_id,
        nyrkio_billing_user,
        gh_event,
        runs_on,
        registration_token,
        org_or_user_repo,
    ):
        self.registration_token = registration_token
        self.org_or_user_repo = org_or_user_repo
        self.nyrkio_user_id = nyrkio_user_id
        self.nyrkio_org_id = nyrkio_org_id
        self.nyrkio_billing_user = nyrkio_billing_user
        self.gh_event = gh_event
        self.runs_on = runs_on
        # Note: supported_instance_types() and therefore also runs_on is ordered by preference. We take the first one.
        self.instance_type = runs_on[0]
        self.config = gh_runner_config(self.instance_type)
        self.tags = self.gh_event_to_aws_tags(self.gh_event)
        logging.info(
            f"RunnerLauncher initialized for user {self.nyrkio_user_id} with instance_type={self.instance_type}"
        )

    async def ensure_runner_group(self):
        installation_access_token = await fetch_access_token(
            expiration_seconds=600, installation_id=self.gh_event["installation"]["id"]
        )
        client = httpx.AsyncClient()
        headers = {
            "Content-type": "application/json",
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {installation_access_token}",
        }

        gh_org = self.gh_event.get("organization", {}).get("login")
        repo_name = self.gh_event["repository"]["name"]
        response = await client.get(
            f"https://api.github.com/orgs/{gh_org}/actions/runner-groups?visible_to_repository={repo_name}",
            headers=headers,
        )
        if response.status_code != 200:
            logging.info(
                f"Could not fetch runner groups for org {gh_org} and repo {repo_name}: {response.status_code} {response.text}"
            )
            return False

        for rg in response.json()["runner_groups"]:
            if rg["name"] == "nyrkio":
                return True

        # If the group exists now, it means the specific repo has been disallowed from using nyrkio runners on purpose
        response = await client.get(
            f"https://api.github.com/orgs/{gh_org}/actions/runner-groups",
            headers=headers,
        )
        if response.status_code != 200:
            logging.info(
                f"Could not fetch runner groups for org {gh_org}: {response.status_code} {response.text}"
            )
            return False

        for rg in response.json()["runner_groups"]:
            if rg["name"] == "nyrkio":
                logging.info(
                    f"Repository {gh_org}/{repo_name} is not included in nyrkio runner group"
                )
                return False

        # If still here, we need to create it
        data_payload = {
            "name": "nyrkio",
            "allows_public_repositories": True,
            "visibility": "all",
        }
        response = await client.post(
            f"https://api.github.com/orgs/{gh_org}/actions/runner-groups",
            json=data_payload,
            headers=headers,
        )
        if response.status_code == 201:
            return True
        else:
            logging.warning(
                f"Tried but failed in creating a runner group at {gh_org} ({response.status_code} {response.text})"
            )
            logging.info(response.reason_phrase)
            logging.info(response.headers)
            logging.info(response.text)
            logging.info(response.request)
            logging.info(response.request.headers)
            logging.info(response.request.text)
            return False

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
                "Value": str(gh_event.get("sender", {}).get("login", "")),
            },
            {"Key": "github_repo", "Value": str(repo.get("full_name", ""))},
            {"Key": "github_job_id", "Value": str(job.get("id", ""))},
            {"Key": "github_job_name", "Value": job.get("name", "")},
            {"Key": "github_job_run_id", "Value": str(job.get("run_id", ""))},
            {"Key": "github_job_run_attempt", "Value": str(job.get("run_attempt", ""))},
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
                "Value": "workflow_job",  # Previous row already assumes this so why not
            },
            {"Key": "repo_owner", "Value": repo.get("owner", {}).get("login", "")},
            {"Key": "job_created_at", "Value": job.get("created_at", "")},
            {"Key": "launched_at", "Value": str(now)},
            {"Key": "group", "Value": "nyrkio-gh-runner"},
            {"Key": "nyrkio_user", "Value": str(self.nyrkio_user_id)},
            {"Key": "nyrkio_org", "Value": str(self.nyrkio_org_id)},
            {"Key": "owner", "Value": str(self.nyrkio_billing_user)},
            {"Key": "billing_user", "Value": str(self.nyrkio_billing_user)},
        ]
        tags = [
            {"Key": str(t["Key"]), "Value": str(t["Value"])[0:254]}
            for t in tags
            if t["Value"] is not None
        ]
        return tags

    async def request_spot_instance(
        self,
        ec2,
        ec2r,
        ami_id,
        key_name,
        instance_type,
        vpc_id,
        nacl_id,
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
        # all_request_ids = []
        sleep_seconds = 10
        logging.debug(
            f"Requesting spot instance {instance_type} in subnet {subnet_id}  ..."
        )
        if not isinstance(spot_price, list):
            spot_price = [spot_price]

        logging.info(user_data)
        user_data = base64.b64encode(user_data.encode("utf-8")).decode("utf-8")
        logging.info(user_data)
        """
        launch_spec = {
            "ImageId": ami_id,
            "KeyName": key_name,
            "InstanceType": instance_type,
            "SubnetId": subnet_id,
            # "PrivateIpAddress": private_ip,
            # "SecurityGroupIds": [sg_id],
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
        }
        instance_id = None

        for offer_price in spot_price:
            logging.info(f"Bidding spot price: {offer_price}")
            response = ec2.request_spot_instances(
                SpotPrice=str(offer_price),
                InstanceCount=1,
                Type="one-time",
                LaunchSpecification=launch_spec,
            )
            sir_id = response["SpotInstanceRequests"][0]["SpotInstanceRequestId"]
            all_request_ids.append(sir_id)
            logging.info(f"SpotInstanceRequestId: {sir_id}")
            # Wait for fulfillment (very basic)
            res = ec2.describe_spot_instance_requests()
            spot_request = None
            for req in res["SpotInstanceRequests"]:
                logging.info(req)
                if req["SpotInstanceRequestId"] in all_request_ids:
                    spot_request = req
                    break

            state = spot_request["State"] if spot_request else spot_request
            logging.info(f"{sir_id} state: {state}")
            if (
                spot_request
                and spot_request["State"] == "active"
                and "InstanceId" in spot_request
            ):
                instance_id = spot_request["InstanceId"]
                logging.info(f"Instance launched: {instance_id}")
                break

            else:
                logging.info(
                    f"Waiting {sleep_seconds} for spot request {sir_id} to be fulfilled..."
                )
                await asyncio.sleep(sleep_seconds)
                if (
                    spot_request is not None
                    and spot_request["State"] == "active"
                    and "InstanceId" in spot_request
                ):
                    instance_id = spot_request["InstanceId"]
                    logging.info(f"Instance launched: {instance_id}")
                    # One is enough. Higher level is responsive to queue length.
                    break

                elif spot_request is not None and spot_request["Status"]["Code"] in [
                    "price-too-low",
                    "canceled-before-fulfillment",
                ]:
                    ec2.cancel_spot_instance_requests(SpotInstanceRequestIds=[sir_id])
                    await asyncio.sleep(sleep_seconds)
                    # verify that we actually canceled in time:
                    res = ec2.describe_spot_instance_requests()
                    spot_request2 = None
                    for req in res["SpotInstanceRequests"]:
                        logging.info(req)
                        if req is not None and req["SpotInstanceRequestId"] == sir_id:
                            spot_request2 = req
                    if spot_request2 and spot_request2["Status"]["Code"] in [
                        "active",
                    ]:
                        logging.info(
                            f"'active' spot instance achieved, after all, for only {offer_price}"
                        )
                        break
                    elif spot_request2 and spot_request2["Status"]["Code"] in [
                        "canceled-before-fulfillment",
                    ]:
                        status = spot_request2["Status"]["Code"]
                        logging.info(
                            f"Spot request {sir_id} canceled, as it should. We can retry, bid higher. Status: {status}"
                        )
                    elif spot_request2 and spot_request2["Status"]["Code"] in [
                        "price-too-low",
                    ]:
                        status = spot_request2["Status"]["Code"]
                        logging.info(
                            f"Spot request {sir_id} not yet canceled. Let's get out of here and just do the regular instances. Status: {status}"
                        )
                        break
                else:
                    logging.info(
                        "Catch all. Not quite clear what this is, so dumping all. Break and go for on-demand."
                    )
                    logging.info(spot_request)
                    break

        if instance_id is None:
            # Cancel the spot request, deploy regular on-demand instance instead
            res = ec2.describe_spot_instance_requests()
            spot_request = None
            for req in res["SpotInstanceRequests"]:
                logging.info(req)
                if req is not None and req["SpotInstanceRequestId"] in all_request_ids:
                    state = req["State"] if req else req
                    sir_id = req["SpotInstanceRequestId"]
                    logging.info(f"{sir_id} state: {state}")
                    logging.warning(
                        f"Spot request {sir_id} not fulfilled, cancelling and launching on-demand instance instead..."
                    )
                    ec2.cancel_spot_instance_requests(SpotInstanceRequestIds=[sir_id])
            await asyncio.sleep(sleep_seconds)
            """
        if True:
            logging.info("Now launching regular on-demand instance...")
            response = ec2.run_instances(
                ImageId=ami_id,
                KeyName=key_name,
                InstanceType=instance_type,
                InstanceInitiatedShutdownBehavior="terminate",
                # PrivateIpAddress=private_ip,
                # SecurityGroupIds=[sg_id],
                # SubnetId=subnet_id,
                # BlockDeviceMappings=[
                #     {
                #         "DeviceName": "/dev/xvda",
                #         "Ebs": {
                #             "VolumeSize": ebs_size,
                #             "Iops": ebs_iops,
                #             "DeleteOnTermination": True,
                #             "Encrypted": True,
                #             "VolumeType": "gp3",
                #         },
                #     }
                # ],
                NetworkInterfaces=[
                    {
                        "DeviceIndex": 0,
                        "AssociatePublicIpAddress": True,
                        "DeleteOnTermination": True,
                        "SubnetId": "subnet-050d9ede5ba431ff6",
                        "Groups": ["sg-0cb149603b3fa1309"],
                    }
                ],
                UserData=user_data,
                MaxCount=1,
                MinCount=1,
            )
            if "Instances" not in response or len(response["Instances"]) == 0:
                logging.warning(
                    "Failed to launch on-demand instance {self.instance_type} for user {self.nyrkio_user_id}"
                )
                raise Exception(
                    "Failed to launch on-demand instance {self.instance_type} for user {self.nyrkio_user_id}"
                )

            instance_id = response["Instances"][0]["InstanceId"]

        instance = ec2r.Instance(instance_id)
        logging.debug(
            "Waiting for instance to be in 'running' state and have a public IP address..."
        )
        instance.wait_until_running()

        ec2.create_tags(
            Resources=[instance_id],
            Tags=self.tags,
        )

        for sleep_secs in [1, 5, 10, 15, 20]:
            await asyncio.sleep(sleep_seconds)
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
        else:
            logging.info(
                f"Instance {instance_id}, launched for {self.nyrkio_user_id} public IP is {instance.public_ip_address}"
            )

        return instance_id, instance.public_ip_address

    async def provision_instance_with_fabric(
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

        retries = [1, 5, 10, 15]
        for sleep_seconds in retries:
            try:
                conn.run("echo verify ssh connection works and is ready to use")
                break
            except NoValidConnectionsError as err:
                logging.info(err)
                await asyncio.sleep(sleep_seconds)

        # Upload all files
        for file_name, content in all_files.items():
            logging.info(f"Uploading {file_name} to {ip_address}")

            base = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            conn.run(f"echo '{base}' | sudo tee '{file_name}.base'")
            conn.run(f"sudo base64 -d {file_name}.base | sudo tee '{file_name}'")
            conn.run(f"sudo chmod a+rx '{file_name}'")

        # Run provisioning script
        logging.info("Running provisioning.sh ...")
        result = conn.run("/tmp/provisioning.sh", warn=True)
        logging.info(result.stdout)

        file_name == "/tmp/provisioning.sh"
        cmd = configsh(self.instance_type, repo_owner, registration_token)
        # cmd = f"echo '{configsh}{repo_owner} --token {registration_token}' | sudo tee -a '{file_name}'"
        logging.info("About to call home to mother ship...")
        logging.info(cmd)
        conn.run(cmd)

        logging.info("Starting run.sh in a detached screen session ...")
        result = conn.run(
            "sudo su runner -c /home/runner/wrapper_wrapper.sh", warn=True
        )
        logging.info(result.stdout)
        return result

    async def launch(self, registration_token=None):
        if registration_token:
            self.registration_token = registration_token

        REGION = self.config.get(
            "region", "eu-central-1"
        )  # Set default region if not in config
        subnet_id = self.config.get("subnet_id", "subnet-0a623bfe81108a1e4")
        sg_id = self.config.get("sg_id", "sg-01dc70c5a8dc24fda")
        nacl_id = self.config.get("nacl_id", "acl-08ec021289cebb343")
        vpc_id = self.config.get("vpc_id", "vpc-0052548c273580de6")

        aws_access_key_id = self.config.get("aws_access_key_id")
        aws_secret_access_key = self.config.get("aws_secret_access_key")
        logging.info(f"aws_access_key_id: {aws_access_key_id}")
        logging.info(f"aws_secret_access_key: {aws_secret_access_key}")
        logging.info(f"region: {REGION}")
        logging.info(f"profile: {self.config.get('profile')}")
        logging.info(
            f"nyrkio_user and org: {self.nyrkio_user_id}, {self.nyrkio_org_id}"
        )

        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            #               profile_name=self.config.get("profile"),
            region_name=REGION,
        )
        ec2 = session.client("ec2")
        ec2r = session.resource("ec2")

        if self.org_or_user_repo == "org" and not await self.ensure_runner_group():
            gh_org = self.gh_event.get("organization", {}).get("login")
            logging.warning(
                f"Couldn't find or create a runner group at http://github.com/{gh_org}"
            )
            return []

        all_instances = []
        for i in range(min(self.config["instance_count"], self.config["max_runners"])):
            instance_id, public_ip = await self.request_spot_instance(
                ec2,
                ec2r,
                self.config["ami_id"],
                self.config["key_name"],
                self.config["instance_type"],
                vpc_id,
                nacl_id,
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

            # labels used to register the runner with github
            labels = ",".join(self.runs_on)
            await self.provision_instance_with_fabric(
                public_ip,
                self.config["ssh_user"],
                self.config["ssh_key_file"],
                # self.config["local_files"],
                render_remote_files(labels=labels),
                self.gh_event["repository"]["owner"]["login"],
                self.registration_token,
            )
            all_instances.append((instance_id, public_ip))
        self.all_instances = all_instances
        logging.info(
            f"RunnerLauncher: Successfully deployed {all_instances} of type {self.instance_type} for user {self.nyrkio_user_id}"
        )
        return all_instances


# Get a one time token to register a new runner
async def get_github_runner_registration_token(
    org_name=None, repo_full_name=None, installation_id=None
):
    token = await fetch_access_token(
        token_url=None, expiration_seconds=600, installation_id=installation_id
    )
    if token:
        logging.info(
            f"Successfully fetched access token for installation_id {installation_id} at {repo_full_name}"
        )
    else:
        logging.info(
            f"Failed to fetch a app installation access token from GitHub for {repo_full_name}/{installation_id}. I can't deploy a runner without it."
        )
        raise Exception(
            f"Failed to fetch a app installation access token from GitHub for {repo_full_name}/{installation_id}. I can't deploy a runner without it."
        )

    client = httpx.AsyncClient()
    response = await client.post(
        f"https://api.github.com/orgs/{org_name}/actions/runners/registration-token",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
    )
    if response.status_code in [200, 201]:
        logging.debug(
            "Geting a runner registration token from github mothership succeeded. Now onto deploy some VMs."
        )
        return response.json()["token"], "org"

    # Could also be a personal repository, no org in the namespace.
    client = httpx.AsyncClient()
    response = await client.post(
        f"https://api.github.com/repos/{repo_full_name}/actions/runners/registration-token",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
    )
    if response.status_code in [200, 201]:
        logging.debug(
            "Geting a runner registration token for user repo succeeded. Now onto deploy some VMs."
        )
        return response.json()["token"], "user"

    # "else"
    logging.info(
        f"Failed to fetch a runner_configuration_token from GitHub for {org_name}. I can't deploy a runner without it."
    )
    # Skip known cases but want alerts for new ones
    if org_name not in ["pedrocarlo"]:
        raise Exception(
            f"Failed to fetch a runner_configuration_token from GitHub for {org_name}. I can't deploy a runner without it."
        )
