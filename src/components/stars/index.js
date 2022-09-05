import React, { useEffect, useState } from "react";

import fetchStars from "../../services/fetchStars";

function Stars() {
  const [stars, setStars] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const json = await fetchStars("last_7_days");
        setStars(json);
      } catch (error) {
        console.log("error", error);
      }
    };

    fetchData();
  }, []);

  if (!stars) {
    return <div>Loading...</div>;
  }

  return (
    <>
      {stars.map((star) => {
        var repoName = star.repo_name;
        return <p>{repoName}</p>;
      })}
    </>
  );
}

export default Stars;
