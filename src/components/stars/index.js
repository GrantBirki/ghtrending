import React, { useEffect, useState } from "react";
import { Link, Text } from "@primer/react";

import fetchStars from "../../services/fetchStars";
import "./index.css";

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
        let repoOwner = star.repo_name.split("/")[0];
        let repoName = star.repo_name.split("/")[1];

        return (
          <>
            <div className="table-row">
              <Link sx={{ fontSize: 3 }} href={star.repo_url}>
                <Text as="span">{repoOwner}</Text>
                <Text as="span"> / </Text>
                <Text as="span" fontWeight="bold">
                  {repoName}
                </Text>
              </Link>
              <Text
                sx={{
                  marginTop: "3px",
                  marginBottom: "3px",
                }}
                as={"p"}
                color="neutral"
              >
                {star.description}
              </Text>
              <div className="f6 color-fg-muted mt-2">
                <Text fontSize={"12px"} color="neutral.emphasisPlus" as="span">
                  {star.language}
                </Text>
              </div>
            </div>
          </>
        );
      })}
    </>
  );
}

export default Stars;
