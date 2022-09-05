import React, { useEffect, useState } from "react";
import { Link, Text, Box } from "@primer/react";
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
        var keyIndex = `${star.repo_name}`;
        let repoOwner = star.repo_name.split("/")[0];
        let repoName = star.repo_name.split("/")[1];
        let langFmt = star.language;
        if (langFmt === null) {
          langFmt = "Other";
        }

        return (
          <Box className="table-row" key={`${keyIndex}-repo-row-div`}>
            <Text
              key={`${keyIndex}-repo-icon-text`}
              sx={{
                marginRight: "7px",
              }}
            >
              <RepoIcon key={`${keyIndex}-repo-icon`} size={16} />
            </Text>
            <Link
              key={`${keyIndex}-repo-link`}
              sx={{ fontSize: 3 }}
              href={star.repo_url}
            >
              <Text key={`${keyIndex}-repo-owner`}>{repoOwner}</Text>
              <Text key={`${keyIndex}-repo-slash`}> / </Text>
              <Text key={`${keyIndex}-repo-name`} fontWeight="bold">
                {repoName}
              </Text>
            </Link>
            <Text
              key={`${keyIndex}-repo-desc`}
              sx={{
                marginTop: "3px",
                marginBottom: "3px",
              }}
              as={"p"}
            >
              {star.description}
            </Text>
            <Box key={`${keyIndex}-repo-info-div`}>
              <LanguageColor
                key={`${keyIndex}-repo-lang-comp`}
                keyIndex={`${keyIndex}-repo-lang-comp`}
                lang={star.language}
                repo_url={star.repo_url}
              />
              <Text
                key={`${keyIndex}-repo-langfmt`}
                fontSize={"12px"}
                color="neutral.emphasisPlus"
              >
                {langFmt}
              </Text>
              <Text
                key={`${keyIndex}-repo-stars-count-wrapper`}
                sx={{ float: "right" }}
              >
                <Text
                  key={`${keyIndex}-repo-stars-count-wrapper-margin`}
                  sx={{ marginRight: "4px" }}
                >
                  <StarIcon
                    key={`${keyIndex}-repo-stars-count-icon`}
                    size={16}
                  />
                </Text>
                {star.stars} stars today
              </Text>
            </Box>
          </Box>
        );
      })}
    </>
  );
}

export default Stars;
