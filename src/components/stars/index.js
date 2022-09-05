import React, { useEffect, useState } from "react";
import { Link, Text, Box } from "@primer/react";
import { RepoIcon, StarIcon } from "@primer/octicons-react";
import fetchStars from "../../services/fetchStars";
import { ActionMenu, ActionList } from "@primer/react";
import { CalendarIcon } from "@primer/octicons-react";
import "./index.css";
import LanguageColor from "../language-color";

const fieldTypes = [
  { icon: CalendarIcon, name: "Last 24 hours", value: "last_24_hours" },
  { icon: CalendarIcon, name: "Last 7 days", value: "last_7_days" },
  { icon: CalendarIcon, name: "Last 30 days", value: "last_30_days" },
  { icon: CalendarIcon, name: "All time", value: "all_time" },
];

function Stars() {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const selectedType = fieldTypes[selectedIndex];
  const [stars, setStars] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const json = await fetchStars(selectedType.value);
        setStars(json);
      } catch (error) {
        console.log("error", error);
      }
    };

    fetchData();
  }, [selectedType.value]);

  if (!stars) {
    return <div key={"loading-stars"}>Loading...</div>;
  }

  return (
    <>
      <Box bg="canvas.default" className="primary-header">
        <Box className="container-lg" borderColor={"fg.subtle"}>
          <Box
            bg="canvas.subtle"
            borderColor={"fg.subtle"}
            className="container-lg-header"
          >
            <Box></Box>
            <Box className="table-header-options">
              <ActionMenu>
                <ActionMenu.Button
                  aria-label="Date range"
                  leadingIcon={selectedType.icon}
                  className={"header-option"}
                >
                  {selectedType.name}
                </ActionMenu.Button>
                <ActionMenu.Overlay width="medium">
                  <ActionList selectionVariant="single">
                    {fieldTypes.map((type, index) => (
                      <ActionList.Item
                        key={index}
                        selected={index === selectedIndex}
                        onSelect={() => setSelectedIndex(index)}
                      >
                        <ActionList.LeadingVisual>
                          <type.icon />
                        </ActionList.LeadingVisual>
                        {type.name}
                      </ActionList.Item>
                    ))}
                  </ActionList>
                </ActionMenu.Overlay>
              </ActionMenu>
            </Box>
          </Box>
          <Box className="container-table">
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
                    <Text key={`${keyIndex}-repo-langfmt`} fontSize={"12px"}>
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
          </Box>
        </Box>
      </Box>
    </>
  );
}

export default Stars;
