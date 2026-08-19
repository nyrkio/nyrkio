import headShot from "../../static/people/golems.svg";
import { UserCard } from "../UserCard/UserCard.jsx";

export const GolemsCard = () => {
  return (
    <>
      <UserCard profile={{
        image: {
          src: headShot,
          width: 84,
          height: 35
        },
        name: 'GOLEMS GABB',
        position: 'Partner',
        description: "<p>The story of our partnership with the Finnish continuous benchmarking platform Nyrkiö is a true testament to how open-source collaboration and shared values create lasting connections.</p><p>It all began back in the days of Drupal 4.6-7, when Oleksandr from Golems took over maintainership of the Footnotes module originally created by Nyrkiö's founder, Henrik Ingo. Years of dedicated stewardship, mutual respect, and trust eventually evolved into an official joint venture agreement.</p><p>Today, the Golems team acts as an integral tech arm for Nyrkiö—bringing complete expertise across UI/UX design, full-stack web development, and project management. Together, we are actively crafting a brand-new experience for nyrkio.com, empowering engineering teams to spot and resolve performance regressions faster than ever.</p>",
      }}/>
    </>
  );
};
