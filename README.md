# [![nyrkio-logo]][product]

Nyrkiö is an open source platform for change detection in a *Continuous Performance Engineering*
workflow.

- Submit results using a [REST API][nyrkio-getting-started] or [GitHub Action][github-action]
- Uses state of the art change point detection algorithm to find performance regressions and improvements in noisy data.
  Nyrkiö can find even small regressions down to 0.5% - 1%.
- Integrates with GitHub to identify the git commit that caused a change in performance

## Using Nyrkiö Change Detection

This software runs [nyrkio.com][dotcom]. Some links to get you started:

[Getting Started with Nyrkiö in 3 easy steps][nyrkio-getting-started]

[Read more about how it works and who else is using it][product]

![nyrkio-footer-graph]

## Developers

### Apache Otava (incubating)

Nyrkiö is a web service around the 8 year old, battle tested [Apache Otava (incubating)][otava]
command line tool. Otava was created and open sourced by the performance teams at MongoDB (2017) and
Datastax (2020). It is used by technology companies large and small, such as Netflix, Dremio, Hazelcast...

### Nyrkiö (.com)

Also the web service itself is open source.

The frontend is implemented using React and the backend is built on top of FastAPI and Pydantic.

If you want to hack on the frontend you can run `npm` directly from inside of the `frontend` directory.
The configuration file `vite.config.js` can be pointing to the real nyrkio.com backend API.

```console
npm install
npm run dev
```

To run the full stack on your own, use the `docker-compose.dev.yml` file which will start services
for the proxy (`nginx`), the frontend (`React`Single-page app) and the backend (`FastAPI` app).


```console
PACMAN=apt
#PACMAN=yum
#PACMAN=brew

git clone git@github.com:nyrkio/nyrkio.git
cd nyrkio
git submodule init
git submodule update

cat > .env.backend << END
DB_URL=mongodb://mongodb.nyrkio.local:27017/mongodb
DB_NAME=nyrkiodb
POSTMARK_API_KEY=
GITHUB_CLIENT_SECRET=
SECRET_KEY=

#HUNTER_CONFIG=
#GRAFANA_USER=
#GRAFANA_PASSWORD=
END

export IMAGE_TAG=$(git rev-parse HEAD)

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


[product]: https://nyrkio.com/product
[dotcom]: https://nyrkio.com
[nyrkio-getting-started]: https://nyrkio.com/docs/getting-started
[nyrkio-logo]: https://nyrkio.com/p/logo/full/Brown/NyrkioLogo_Final_Full_Brown-200px.png
[nyrkio-footer-graph]: https://nyrkio.com/assets/footer-white-graphic-8R7Ap4-5.png
[github-action]: https://github.com/nyrkio/change-detection
[otava]: https://otava.apache.org

## License

Licensed under the [Apache License, Version 2.0](https://opensource.org/license/apache-2-0/) ("the license"); you may not use these files except in compliance with the License. You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0


Apache and Apache Otava are trademarks of the Apache Software Foundation
Nyrkiö and Nyrkiö Change Detection are trademarks of Nyrkiö Oy





