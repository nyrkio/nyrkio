export const githubSubmit = async (e) => {
  e.preventDefault();
  console.log("Github submit");
  const data = await fetch("https://nyrk.io/api/v0/auth/github/authorize")
    .then((response) => response.json())
    .then((url) => url["authorization_url"])
    .then((url) => {
      console.log(url);
      window.location.href = url;
      setLoggedIn(true);
      localStorage.setItem("loggedIn", "true");
    })
    .catch((error) => console.log(error));
};
