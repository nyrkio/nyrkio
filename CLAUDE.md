# Claude.md

This repo contains both the backend and frontend of nyrkio.com. It's original feature was a change point detection service 
that basically is a web / SaaS wrapper around Apache Otava (formerly known as Hunter, of Datastax Labs, and merely "signal processing" or "e-divisive" from MongoDB).
Nyrkiö adds visual graphs and notifications to slack and github. (Contrary to marketing, jira integration isn't actually implemented in this repo yet.)
As I'm writing this, we are ready to release a v2 of nyrkio.com, which adds a GitHub runner service. Nyrkiö's GitHub runners are configured for 
maximal stability and repeatability of benchmark results, as opposed to maximizing perf results or price-performance. (...of which there are many
other 3rd party offerings.) The runners are a major new feature, introducing metered billing for customers that use this feature. (The previous
business and enterprise subscription tiers remain, and will include 1600 and 4000 cpu-hours per month, respectively.)

Most of this code was initially written by a Matt Fleming, but he is no longer active in the project. For over a year the project has been 
brought forward by Henrik Ingo. The past 8 months or so, Joe Drumgoole, armed with his ownn instance of Claude, has helped a little.
Most notably he/they implemented a battery of front end tests with playwright. However, these tests aren't yet hooked into CI
(.github/worklows/) so some of them probably are out of sync and not passing right now.

The backend is a python FastAPI application, with MongoDB as a database. The frontend is a react single page application.

Claude does not / should not have permission to push to main (which triggers automatic deployment). In particular, Henrik's Claude instance
if a separate Linux user account, and Henrik will manually sync git repositories and create pull requests even. Claude has no direct github access
other than http to obsever public projects. (this is a public project)

## Short term goals

Short term we are inviting Claude to do some final release related tasks, such as updating docs and README files. When you 
wake up and read this, we'll do the following list of tasks.

 - [ ] update /docs/ and particularly /docs/getting-started to lead with and cover the github. 
   - Suggestions to separate the docs from the react app are welcome. e.g. should we run something else under nyrkio.com/docs/ ?
     Joe is a fan of readthedocs.
   - I can record demovideos, feel free to ask.
 - [ ] generally review everything and suggest improvements if there are glaring problems. (But prioritize the release. For example, upgrading python itself, pypi modules, npm modules... is NOT a priority before the release. It will be immediately after.)
 - The site was created by two backend / database and kernel engineers. Suggesting front end improvements where you see particularly bad CSS is welcome.
   But note that a certain hand made feel, communicating "yes we are performance engineers not UI designers" is part of the brand and should not be completely lost.

## Medium term goals (after the release)

 - [ ] Review playwright tests, and fix those that are failing
 - [ ] Create a .github/workflow/playwright.yml file to run all playwright tests as part of a PR. I'll add this to required tests in github (branch protection)
 - [ ] The big 100k patch intoo /frontend/ - that introduced all the playwright tests - is awfully fluffy to my taste. For example, surely we can delete the markdown
       files that document everything you did and tried to do to arrive at the end result? So delete and cleanup everything not needed.
 - [ ] Also for topics like how to run the tests... We are experienced engineers. You don't need to explain basics of how npm works. Just show the command,
       like `npm ui-test` (hypothetical example). As short as possible. But not shorter.
 - [ ] There is backend/runtests.sh that runs the lint, format, etc commands that we also use in GitHub actions. And in /frontend/ of course we have
       npm/package.json. But now Joe/Claude have added python scripts in /etc/ directory that can be used to start and stop both a backend and a frontend.
       We should move everything from backend/runtests.sh to use this new system. Probably a Makefile or invoke file. (Joe seems to prefer invoke?)
       Either way, in the end it should be possible to be in the root of the repo, do `make all-tests` or `inv all-tests` and run everything that will
       also run in GitHub actions.

### Dashboard
       
 - [ ] In the frontend, Dashboard.jsx, there's a line of code that hard coded cuts the data to 300 most recent points. However, the entire history is still fetched from the backend. As a first task, extend the backend API so that it takes as parameter both nr of points (e.g. 300) and/or a time window (60 days, or start and stop dates) and then uses these in the MongoDB query ($limit or $gte/$lte as appropriate)
 - [ ] For some commits we fetch the commit message from the github API and show it. To avoid exhausting the quota on API requests, there is a caching mechanism (Sieve cache). Instead, we should simply store the commit message in test_results under "attributes". The API should allow this as optional, and if not present, we should fetch it from the API. We could extend this to other meta data like commit author.
 - [ ] Unrelated to the above, but there's an  /impersonate/ api endpoint, which allows sysadmins to assume the identity of another user. This also stores a session variable in a global python dict(). Change this so that the session is stored in MongoDB.
 - [ ] Verify that after doing the above, there's nothing left that would prevent us from running several docker instances of the backend in parallel.
 

 - [ ] In addition to the above, we should in fact fetch from the Github api also all the commits that do not yet have any benchmark results. This is important since a regression can be introduced by any commit that is between the last data point and the previous one, not just the one that happens to have benchmark results available. (Note: by "all commits" I meanall commits in the recent history of the main branch or so. Do NOT query github api for the entire history of a repository as that will look like scraping to GitHub)


 - [ ] The current Dashboard code used to be 3 separate code paths: personal, org and public. I forced them into a single code path, but now the code is very bloated. A lot of the divs and react commponents are redundant with each other, but I didn't dear to remove any previously, for fear of surprising css effects and so on. Now with playwright test coverage, we can finally try some serious refactoring and rely on our tests to not break anythng
 - [ ] Either at the top or perhaps bottom of a dashboard page, add a horizontal widget that is a timeline: Allow user to scroll over dates, and git commits and the related commit messages + author info. And allow user to select a range of commits (indirectly a range of dates). The range selected by the user should now be fetched from MongoDB and plotted in the graphs in the dashboard.
 - [ ] When clicking on a dot in a graph, a modal dialog opens where user can see all the atributes and extra_info stored at this particular commit and test_result. Instead of a modal, change this so that it is a panel that opens or slides open next to the timeline we created in the previous point. If the panel is a little transparent, it can cover the grapsh an the change point table under itself. If needed, it could even occupy the entire screen.


## Long term (which might be sooner than I expect)


TODO


...but for now the main point of this section is that there's a lot in the current stack I don't like: React, fastapi_users, pydantic... So when working on the above tasks, Don't invest in too much refactoring or UI enhancements, as a future version might replace the current code completely.

## General requirements

- when you make commits make sure the CI checks on github pass
- when you create a test run it and all the other tests to validate that it works

Both of Henrik's children are graphics designers and/or artists and strongly critical of imagery generated by AI. Hence Nyrkiö Oy is committed to only user images either painted/drawn by a human, or photography. Lately this have been commissioned by Henrik's daughter Ebba. Wife and Nyrkiö partner Sanna supplies nature photography fitting the Nyrkio/Nyyrikki theme of Finnish/Karelian forests.

 - You must NEVER create or download AI generated images or graphics.
 - Also email and blog marketing we want to mostly type ourselves with our human fingers.
 - Manuals and documentation can be AI generated. Again, try to be succinct. "Do X in 3 easy steps", is a good format.
 - Code will increasingly be AI generated.
 
... in fact, as of this writing all Nyrkiö work (such as this repository) is done evenings and weekends. 
The improved velocity from AI is very welcome indeed.

 - While generating code is easy for you, the goal is NOT to generate as many lines as possible. Quite the opposite. Less lines of code means I am able to read and review it as a human, and hopefully also less bugs, if we assume the frequency of bugs per 1000 lines is somewhat constant.
   - Please use object oriented programming. In the case of JS/React, closures is good enough (as you can tell from existing code).
