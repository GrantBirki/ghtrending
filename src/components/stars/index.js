import React, { useEffect, useState } from "react";
import { Link, Text } from "@primer/react";
import { RepoIcon, StarIcon } from "@primer/octicons-react";
import fetchStars from "../../services/fetchStars";
import "./index.css";
import LanguageColor from "../language-color";

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
    return <div key={"loading-stars"}>Loading...</div>;
  }

  return (
    <>
      {stars.map((star) => {
        let repoOwner = star.repo_name.split("/")[0];
        let repoName = star.repo_name.split("/")[1];
        let langFmt = star.language;
        if (langFmt === null) {
          langFmt = "Other";
        }

        return (
          <>
            <div className="table-row" key={`${star.repo_url}-repo-row-div`}>
              <Text
                key={`${star.repo_url}-repo-icon-text`}
                sx={{
                  marginRight: "7px",
                }}
                as={"span"}
              >
                <RepoIcon key={`${star.repo_url}-repo-icon`} size={16} />
              </Text>
              <Link
                key={`${star.repo_url}-repo-link`}
                sx={{ fontSize: 3 }}
                href={star.repo_url}
              >
                <Text key={`${star.repo_url}-repo-owner`} as="span">
                  {repoOwner}
                </Text>
                <Text key={`${star.repo_url}-repo-slash`} as="span">
                  {" "}
                  /{" "}
                </Text>
                <Text
                  key={`${star.repo_url}-repo-name`}
                  as="span"
                  fontWeight="bold"
                >
                  {repoName}
                </Text>
              </Link>
              <Text
                key={`${star.repo_url}-repo-desc`}
                sx={{
                  marginTop: "3px",
                  marginBottom: "3px",
                }}
                as={"p"}
              >
                {star.description}
              </Text>
              <div
                key={`${star.repo_url}-repo-info-div`}
              >
                <LanguageColor
                  key={`${star.repo_url}-repo-lang-comp`}
                  lang={star.language}
                  repo_url={star.repo_url}
                />
                <Text
                  key={`${star.repo_url}-repo-langfmt`}
                  fontSize={"12px"}
                  color="neutral.emphasisPlus"
                  as="span"
                >
                  {langFmt}
                </Text>
                <Text
                  key={`${star.repo_url}-repo-stars-count-wrapper`}
                  sx={{ float: "right" }}
                >
                  <Text
                    key={`${star.repo_url}-repo-stars-count-wrapper-margin`}
                    as="span"
                    sx={{ marginRight: "4px" }}
                  >
                    <StarIcon
                      key={`${star.repo_url}-repo-stars-count-icon`}
                      size={16}
                    />
                  </Text>
                  {star.stars} stars today
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
