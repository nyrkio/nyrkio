import headShot from "../../static/people/Joe-600x800.jpg";
import { UserCard } from "../UserCard/UserCard.jsx";

export const JoeCard = () => {
  return (
    <>
      <UserCard profile={{
        image: {
          src: headShot,
          width: 600,
          height: 800
        },
        name: 'Joe Drumgoole',
        position: 'Go To Market',
        description: "<p>From Oracle to founding startups of his own, Joe brings with him decades of experience from the Dublin tech scene. Joe and Henrik met in 2013 when MongoDB expanded to Europe and assembled a \"dream team\" of database experts that the European database industry had not seen before, and probably never will. Most recently Joe worked at PostgreSQL shop Neon.</p><p>Joe joined Nyrkiö in 2025 shouldering a broad hands on role fitting the entrepreneurial spirit in the company. While formally responsible for marketing and developer relations, Joe has also managed to evolve R&D processes in the company by dragging Henrik into the AI era: In a single AI generated 100k line patch, Joe caught up 2 years worth of technical debt in playwright tests! All those tests we promised to add \"later\"... we finally did!</p>"
      }}/>
    </>
  );
};
