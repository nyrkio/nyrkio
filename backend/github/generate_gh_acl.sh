function getip () {
    nslookup $1 | grep Address |grep -v 127.0.0 | cut -c 10-30 | grep -v \:\:
}

echo gh_runner_allowed_ips = \"\"\"

getip github.com | grep Address |grep -v 127.0.0 | cut -c 10-30
getip api.github.com
getip *.actions.githubusercontent.com
getip codeload.github.com
getip pkg.actions.githubusercontent.com
getip ghcr.io
getip results-receiver.actions.githubusercontent.com
getip *.blob.core.windows.net
getip objects.githubusercontent.com
getip objects-origin.githubusercontent.com
getip github-releases.githubusercontent.com
getip github-registry-files.githubusercontent.com
getip *.actions.githubusercontent.com
getip *.pkg.github.com
getip pkg-containers.githubusercontent.com
getip ghcr.io
getip github-cloud.githubusercontent.com
getip github-cloud.s3.amazonaws.com
getip dependabot-actions.githubapp.com
getip release-assets.githubusercontent.com
getip api.snapcraft.io

echo \"\"\"
