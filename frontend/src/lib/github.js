/*
 * Github URLS and other things we standardize
 */

const repoFixes = (repo) => {
  if (repo.endsWith(".git")){
    repo = repo.substring(-4);
  }
  if (!repo.startsWith("https://github.com/")){
    repo = "https://github.com/" + repo;
  }
  return repo;
};

export const commitUrl = (repo, commit) => {
  repo = repoFixes(repo);
  return repo + "/commit/" + commit;
};

export const branchUrl = (repo, branch) => {
  repo = repoFixes(repo);
  return repo + "/tree/" + branch;
};
