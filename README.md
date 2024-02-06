## Nyrkiö is an open source platform for analysing performance test results and detecting changes

- Submit results using a REST API
- Uses change point detection to find performance regressions and improvements in noisy data
- Integrates with GitHub to identify the git commit that caused a change in performance

## Contributing

We welcome all contributions!

The frontend is implemented using React and the backend is built on top of FastAPI and Pydantic.

If you want to hack on the frontend you can run `npm` directly from inside of the `frontend` directory.

```console
npm install
npm run dev
```

You can run a more realistic environment using the `docker-compose.dev.yml` file which will start services for the proxy (`nginx`), the frontend (`React`Single-page app) and the backend (`FastAPI` app).


```console
PACMAN=apt
#PACMAN=yum
#PACMAN=brew

git clone git@github.com:nyrkio/nyrkio.git
cd nyrkio
git submodule init
git submodule update

cat <<<END  > .env.backend
#DB_URL=mongodb://localhost:27017/nyrkiodb
DB_URL=mongodb+srv://nyrkio:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=nyrkiodb
POSTMARK_API_KEY=
GITHUB_CLIENT_SECRET=
SECRET_KEY=

#HUNTER_CONFIG=
#GRAFANA_USER=
#GRAFANA_PASSWORD=
END

sudo $PACMAN install docker.io docker-compose-v2
sudo usermod -a -G docker $USER
newgrp docker


docker compose -f docker-compose.dev.yml up --build
```

### Contributing Changes

Please open a pull request with your changes against the `main` branch. PRs allow us to run linters and tests against your modifications.

## References

- [The Use of Change Point Detection to Identify Software Performance Regressions in a Continuous Integration System](https://arxiv.org/pdf/2003.00584)
- [Hunter: Using Change Point Detection to Hunt for Performance](https://arxiv.org/pdf/2301.03034.pdf)

## License

Licensed under the [Apache License, Version 2.0](https://opensource.org/license/apache-2-0/) ("the license"); you may not use these files except in compliance with the License. You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0
