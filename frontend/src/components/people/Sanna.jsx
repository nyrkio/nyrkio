import headShot from "../../static/people/SannaClose-600x800.jpg";

export const SannaCard = () => {
  return (
    <div className="row row-cols-1 row-cols-md-2">
      <div className="col">
        <div className="card m-3 rounded-3 shadow people-card">
          <div className="card-header p-5 justify-content-center text-center">
            <img src={headShot} alt="Head shot" className="rounded-3" />
            <h4 className="my-2">Sanna Ingo</h4>
            <p>Admin, Finance & Facilities</p>
          </div>
        </div>
      </div>
      <div className="col p-4">
        <p>

        </p>
        <p>
        In 2025,
        Sanna has stepped in to a more operative role, to ensure a smooth co-operation with the accounting, government taxes and so on. Sanna has 3 decades of experience
        using Linux, KDE and LibreOffice in all of the company paperwork. Pretty much going back to when KDE and OpenOffice got started.
        </p>
        <p>With a Masters degree in Finnish Folkloristics, she is also the undisputed domain expert on <a href="/legend">Nyyrikki</a> and mythology of the Finnish forest and its creatures.</p>
      </div>
    </div>
  );
};
