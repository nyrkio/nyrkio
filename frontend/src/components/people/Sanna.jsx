import headShot from "../../static/people/SannaClose-600x800.jpg";
import { UserCard } from "../UserCard/UserCard.jsx";

export const SannaCard = () => {
  return (
    <>
      <UserCard profile={{
        image: {
          src: headShot,
          width: 600,
          height: 800
        },
        name: 'Sanna Ingo',
        position: 'Admin, Finance & Facilities',
        description: "<p>In 2025, Sanna has stepped in to a more operative role, to ensure a smooth co-operation with the accounting, government taxes and so on. Sanna has 3 decades of experience using Linux, KDE and LibreOffice in all of the company paperwork. Pretty much going back to when KDE and OpenOffice got started.</p><p>With a Masters degree in Finnish Folkloristics, she is also the undisputed domain expert on<a href=\"/legend\">Nyyrikki</a>and mythology of the Finnish forest and its creatures.</p>"
      }}/>
    </>
  );
};
