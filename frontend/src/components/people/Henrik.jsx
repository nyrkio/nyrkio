import headShot from "../../static/people/Henrik-600x800.jpg";
import { UserCard } from "../UserCard/UserCard.jsx";

export const HenrikCard = () => {
  return (
    <>
      <UserCard profile={{
        image: {
          src: headShot,
          width: 600,
          height: 800
        },
        name: 'Henrik Ingo',
        position: 'CEO',
        description: "<p>Henrik has worked two decades in the world of Open Source databases: MySQL, MariaDB, MongoDB, Cassandra, Postgresql... He is known for his interest in performance and scaling, including topics like distributed consensus algorithms.</p><p>Henrik worked on the MongoDB performance engineering team in 2015, where the E-Divisive algorithm was first used for automating the detection of performance regressions, and eventually published as both a conference paper and open source code. Later he managed the performance team at Datastax, where further improvements were implemented and again open sourced. Now Nyrkiö is bringing that work into the mainstream.</p>"
      }}/>
    </>
  );
};
