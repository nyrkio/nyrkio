"""
Challenge Publish Handshake

We want to allow any logged in Github user use Nyrkiö with zero effort needed to subscribe or register to anything.

At the start of a GitHub action, the action code running at github.com initiates a handshake protocol with
nyrkio.com. It claims to be a certain github username. The nyrkio.com side verifies that such a workflow is
currently running and was triggered by the given username. nyrkio.com then returns  a random string to the action.
When the action prints this challenge into its log, this is observed by the nyrkio.com side. This proves that
the connection was indeed iniitiated by the code running that specific workflow, triggered by the github user
that is associated with the workflow run in numerous json files returned by github.
"""
from typing import Optional, Dict
import logging
import uuid
import os

import httpx
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import zipfile
import io

from backend.db.db import (
    UserCreate,
)

from backend.auth.common import (
    get_user_manager,
    jwt_backend,
    get_jwt_strategy,
)



cph_router = APIRouter(prefix="/challenge_publish")


async def get_user_by_github_username(github_username: str):
    manager = get_user_manager()
    return await manager.get_by_github_username(github_username)


async def create_cph_user(github_username: str, is_repo_owner: bool = False):
    manager = get_user_manager()
    user = UserCreate(
        github_username=github_username,
        email=f"{github_username}@ChallengeResponseHandshake.github.nyrkio.com",
        password=uuid.uuid4(),
        is_active=True,
        is_verified=True,
        is_cph_user=True,
        is_repo_owner=is_repo_owner,
    )

    return await manager.create(user)


class ChallengePublishSession(BaseModel):
    username: str
    client_secret: str
    server_secret: str


class ChallengePublishClaim(BaseModel):
    username: str
    client_secret: str

    repo_owner: str
    repo_name: str
    repo_owner_email: Optional[str] = None
    repo_owner_full_name: Optional[str] = None
    workflow_name: str
    event_name: str
    run_number: int
    run_id: int
    run_attempt: Optional[int] = None


class ChallengePublishChallenge(BaseModel):
    session: ChallengePublishSession
    public_challenge: str
    artifact_id: Optional[str] = None
    public_message: str
    claimed_identity: ChallengePublishClaim


class ChallengePublishHandshakeComplete(BaseModel):
    session: ChallengePublishSession
    artifact_id: int


# TODO: Store in Mongodb some other day ;-)
handshake_ongoing_map = {}


@cph_router.post("/github/claim")
async def challenge_publish_claim(
    claim: ChallengePublishClaim,
) -> ChallengePublishChallenge:
    """
    First part of a "ChallengePublish Github Action Authentication Handshake".

    Note that this is like a login end point, so coming here, user is unknown and unauthenticated
    """
    claim.run_attempt = await verify_workflow_run(claim)
    public_challenge, public_message = create_challenge(claim)
    server_secret = create_secret()
    session = ChallengePublishSession(
        username=claim.username,
        client_secret=claim.client_secret,
        server_secret=server_secret,
    )
    challenge = ChallengePublishChallenge(
        session=session,
        public_challenge=public_challenge,
        public_message=public_message,
        claimed_identity=claim,
    )
    if session.username not in handshake_ongoing_map:
        handshake_ongoing_map[session.username] = {}
    if session.client_secret in handshake_ongoing_map[session.username]:
        raise HTTPException(
            status_code=409,
            detail=f"This username ({session.username}) and client_secret is already in use by another handshake, or alternatively you mistakenly POSTed the same request twice.",
        )
    handshake_ongoing_map[session.username][session.client_secret] = challenge

    return challenge


@cph_router.post("/github/complete")
async def challenge_publish_complete(
    sessionplus: ChallengePublishHandshakeComplete,
) -> Dict:
    """
    second part

    Can't trust the incoming data anymore: Just use the username and client secret
    to lookup and match corresponding server_secret.

    At this point client should have printed public_message into its main log, aka stdout.
    Our job is to read the log and find the public_challenge in it.

    """
    # Note: user is still unauthenticated as handshake isn't co
    session = sessionplus.session

    if session.username not in handshake_ongoing_map:
        raise HTTPException(
            status_code=401,
            detail=f"Username {session.username} doesn't have any ChallengePublish handshakes ongoing.",
        )
    challenge = handshake_ongoing_map[session.username].get(session.client_secret, None)
    if challenge is None:
        # Makes it a bit harder to brute force (but doesn't prevent parallellism)
        # await asyncio.sleep(25)
        raise HTTPException(
            status_code=401,
            detail="ChallengePublish handshake failed: wrong client_secret",
        )
    # Make sure to never reuse the secrets (replay attacks and what have you)
    del handshake_ongoing_map[session.username][session.client_secret]
    challenge.artifact_id = sessionplus.artifact_id

    if await validate_public_challenge(challenge):
        github_username = challenge.session.username
        # This user may be a real / full on user that first created a user account on nyrkio.com
        # Or it may be a CPH user that never visited nyrkio.com in person
        # We use user.is_cph_user and user.is_repo_owner to restrict some functionality appropriately
        # TODO: also restrict `user.is_cph_user and user.is_admin`
        user = get_user_by_github_username(github_username)
        if not user:
            # User doesn't exist at all, create now a lightweight CphUser
            # TODO: For the repo owner...
            user = create_cph_user(github_username, is_repo_owner=False)

        # Give the user a short lived JWT token. After this, it will look like a regular user logging in and using JWT tokens.
        jwt_token = await jwt_backend.login(get_jwt_strategy(), user)

        return {
            "message": "ChallengePublish Handshake completed. Please keep the supplied JWT token secret and use it to authenticate going forward.",
            "github_username": challenge.session.username,
            "jwt_token": jwt_token,
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Didn't find the challenge in your log output. Challenge Publish Handshake failed!",
        )


async def verify_workflow_run(claim: ChallengePublishClaim) -> int:
    """
    Verify that a workflow run exists where repo_owner and run_id match what we were given.

    Note: repo_owner isn't necessarily the username we are authenticating.
    Note: This also checks early that we can read the workflow APIs, e.g. this is not a private repo.
    """
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)
    HTTP_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    client = httpx.AsyncClient()
    uri = f"https://api.github.com/repos/{claim.repo_owner}/{claim.repo_name}/actions/runs/{claim.run_id}"
    response = await client.get(uri, headers=HTTP_HEADERS)
    if response.status_code != 200:
        logging.error(
            f"ChallengePublishHandshake: Failed to fetch the given workflow run from GitHub: {response.status_code}: {response.text}"
        )
        logging.error(dict(claim))
        raise HTTPException(
            status_code=424,
            detail=f"ChallengePublishHandshake: Could not find the Github workflow you claim to be running: {uri}",
        )
    # For pull requests, username is not the same as repo owner, so check that (for both, while at it)
    workflow = response.json()
    if workflow["event"] == "pull_request":
        workflow_username = workflow["actor"]["login"]
        if workflow_username != claim.username:
            logging.error(
                f"ChallengePublishHandshake failed: claim has username {claim.username} and PR has {workflow_username}"
            )
            raise HTTPException(
                status_code=401,
                detail=f"ChallengePublishHandshake failed. You claimed to be github user {claim.username} but that was not confirmed by {uri}",
            )

    if workflow["event"] == "push":
        workflow_username = workflow["repository"]["owner"]["login"]
        if workflow_username != claim.username:
            logging.error(
                f"ChallengePublishHandshake failed: claim has username {claim.username} and PR has {workflow_username}"
            )
            raise HTTPException(
                status_code=401,
                detail=f"ChallengePublishHandshake failed. You claimed to be github user {claim.username} but that was not confirmed by {uri}",
            )

    # We need the exact run_attempt in part 2, might as well get it while we have it in our hands
    return workflow["run_attempt"]


def create_secret() -> str:
    return str(uuid.uuid4())


def create_challenge(claim: ChallengePublishClaim) -> str:
    randomstr = str(uuid.uuid4())
    workflowstr = f"/{claim.repo_owner}/{claim.repo_name}/actions/runs/{claim.run_id}"

    line1 = "ChallengePublishHandshake between github.com and nyrkio.com:\n"
    line2 = f"I am {claim.username} and this is proof that I am currently running {workflowstr}: {randomstr}"

    return randomstr, line1 + line2


# def zipped_chunks(url):
#     GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)
#     HTTP_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
#     # Iterable that yields the bytes of a zip file
#     with httpx.stream("GET", url, headers=HTTP_HEADERS, follow_redirects=True) as r:
#         print("yielding chunks from the zip now")
#         yield from r.iter_bytes(chunk_size=65536)


def check_match(log_chunks, randomstr):
    if randomstr in log_chunks:
        return True
    return False


# async def validate_public_challenge_STREAM_OFF(
#     challenge: ChallengePublishChallenge,
# ) -> bool:
#     i = challenge.claimed_identity
#     log_url = f"https://api.github.com/repos/{i.repo_owner}/{i.repo_name}/actions/runs/{i.run_id}/attempts/{i.run_attempt}/logs"
#
#     found = False
#     previous_chunk = ""
#     try:
#         # Each step is a separate text file inside the zip archive
#         for file_name, file_size, unzipped_chunks in stream_unzip(
#             zipped_chunks(log_url)
#         ):
#             # unzipped_chunks must be iterated to completion or UnfinishedIterationError will be raised
#             # It's ok, what we are looking for is probably toward the end anyway
#             for chunk in unzipped_chunks:
#                 if check_match(previous_chunk + chunk, challenge.public_challenge):
#                     found = True
#                 previous_chunk = chunk
#     except Exception as any_exception:
#         print(any_exception)
#
#     return found
#

async def validate_public_challengeOFF(challenge: ChallengePublishChallenge) -> bool:
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)
    HTTP_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    i = challenge.claimed_identity
    log_url = f"https://api.github.com/repos/{i.repo_owner}/{i.repo_name}/actions/runs/{i.run_id}/attempts/{i.run_attempt}/logs"

    challenge_as_bytes = challenge.public_challenge.encode("utf-8")
    found = False
    client = httpx.AsyncClient()
    response = await client.get(log_url, headers=HTTP_HEADERS, follow_redirects=True)
    print(response)
    if response.status_code != 200:
        logging.error(
            f"ChallengePublishHandshake: Failed to fetch the log file from run_id {i.run_id}/{i.run_attempt} from GitHub: {response.status_code}: {response.text}"
        )
        raise HTTPException(
            status_code=424,
            detail=f"ChallengePublishHandshake: Failed to fetch the log file from run_id {i.run_id}/{i.run_attempt} from GitHub: {log_url}",
        )
    log_contents_zipped = response.content
    z = zipfile.ZipFile(io.BytesIO(log_contents_zipped))
    print(z.namelist())
    for filename in z.namelist():
        print(filename)
        log = z.read(filename)
        if check_match(log, challenge_as_bytes):
            logging.info(
                f"Challenge Publish Handshake: Found the public_challenge for {i.username} in {filename} of {log_url}(.zip)"
            )
            found = True

    return found


async def validate_public_challenge(challenge: ChallengePublishChallenge) -> bool:
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)
    HTTP_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    # https://api.github.com/repos/henrikingo/change-detection/actions/runs/16852427913/artifacts
    artifact_url = f"https://api.github.com/repos/{challenge.claimed_identity.repo_owner}/{challenge.claimed_identity.repo_name}/actions/runs/{challenge.claimed_identity.run_id}/artifacts"
    logging.info(f"GET: {artifact_url}")
    client = httpx.AsyncClient()
    response = await client.get(artifact_url, headers=HTTP_HEADERS, follow_redirects=True)
    if response.status_code != 200:
        logging.error(
            f"ChallengePublishHandshake: Failed to fetch the list of artifact files from GitHub: {response.status_code}: {response.text}"
        )
        raise HTTPException(
            status_code=424,
            detail=f"ChallengePublishHandshake: Failed to fetch the list of artifact files from GitHub: {artifact_url}",
        )
    artifact_list = response.json()
    for one_artifact in artifact_list["artifacts"]:
        if one_artifact["id"] == challenge.artifact_id:
            parts = one_artifact["name"].split(".")
            if len(parts) == 2 and parts[0] == "ChallengePublishHandshake" and parts[1] == challenge.public_challenge:
                # FOUND IT!
                # Note we put the challenge in the artifact name already, no need to get the contents...
                return True

    raise HTTPException(
        status_code=401,
        detail=f"Didn't find the public_challenge {challenge.public_challenge} in any of the artifacts for your workflow run: {artifact_url}",
    )
