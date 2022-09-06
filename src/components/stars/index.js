import React, { useEffect, useState } from "react";
import { Link, Text, Box, Avatar, SubNav, AvatarStack } from "@primer/react";
import { RepoIcon, StarIcon, RepoForkedIcon } from "@primer/octicons-react";
import fetchStars from "../../services/fetchStars";
import { ActionMenu, ActionList } from "@primer/react";
import { CalendarIcon } from "@primer/octicons-react";
import "./index.css";
import LanguageColor from "../language-color";

const fieldTypes = [
  {
    icon: CalendarIcon,
    name: "Last 24 hours",
    value: "last_24_hours",
    shortText: "today",
  },
  {
    icon: CalendarIcon,
    name: "Last 7 days",
    value: "last_7_days",
    shortText: "this week",
  },
  {
    icon: CalendarIcon,
    name: "Last 30 days",
    value: "last_30_days",
    shortText: "this month",
  },
  {
    icon: CalendarIcon,
    name: "All time",
    value: "all_time",
    shortText: "all time",
  },
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
            <Box>
              <SubNav aria-label="Main">
                <SubNav.Links>
                  <SubNav.Link selected>Repositories</SubNav.Link>
                </SubNav.Links>
              </SubNav>
            </Box>
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

              // if the contributors array exists and is not empty
              var contributors = null;
              if (star.contributors && star.contributors.length) {
                contributors = star.contributors;
              }

              return (
                <Box className="table-row" key={`${keyIndex}-repo-row-div`}>
                  {/* Repo Name */}
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

                  {/* Description */}
                  <Text
                    key={`${keyIndex}-repo-desc`}
                    sx={{
                      marginTop: "3px",
                      marginBottom: "3px",
                    }}
                    className="repo-desc"
                    as={"p"}
                  >
                    {star.description}
                  </Text>

                  {/* Repo details block */}
                  <Box key={`${keyIndex}-repo-info-div`}>
                    {/* Language */}
                    <LanguageColor
                      key={`${keyIndex}-repo-lang-comp`}
                      keyIndex={`${keyIndex}-repo-lang-comp`}
                      lang={star.language}
                      repo_url={star.repo_url}
                    />
                    <Text
                      sx={{ marginRight: "26px" }}
                      key={`${keyIndex}-repo-langfmt`}
                      fontSize={"12px"}
                    >
                      {langFmt}
                    </Text>

                    {/* Stargazers total */}
                    <Text
                      key={`${keyIndex}-repo-stargazers-total-wrapper-margin`}
                      sx={{ marginRight: "4px" }}
                    >
                      <StarIcon
                        key={`${keyIndex}-repo-stargazers-total-icon`}
                        size={16}
                      />
                    </Text>
                    <Text
                      sx={{ marginRight: "26px" }}
                      key={`${keyIndex}-repo-stargazers-total`}
                      fontSize={"12px"}
                    >
                      {star.stargazers_count.toLocaleString()}
                    </Text>

                    {/* Forks */}
                    <Text
                      key={`${keyIndex}-repo-forks-count-wrapper-margin`}
                      sx={{ marginRight: "4px" }}
                    >
                      <RepoForkedIcon
                        key={`${keyIndex}-repo-forks-count-icon`}
                        size={16}
                      />
                    </Text>
                    <Text
                      sx={{ marginRight: "26px" }}
                      key={`${keyIndex}-repo-forks`}
                      fontSize={"12px"}
                    >
                      {star.forks_count.toLocaleString()}
                    </Text>

                    {/* Contributors */}

                    {contributors && (
                      <Text
                        sx={{ marginRight: "12px" }}
                        key={`${keyIndex}-repo-built-by`}
                        fontSize={"12px"}
                      >
                        Built by
                      </Text>
                    )}
                    <Text key={`${keyIndex}-avatar-stack-wrapper`}>
                      <AvatarStack
                        key={`${keyIndex}-avatar-stack`}
                        sx={{
                          verticalAlign: "middle",
                          display: "inline-block",
                        }}
                      >
                        {contributors &&
                          contributors.map((contributor) => {
                            return (
                              <Avatar
                                key={`${keyIndex}-${contributor.avatar_url}-avatar`}
                                src={`${contributor.avatar_url}&size=24`}
                              />
                            );
                          })}
                      </AvatarStack>
                    </Text>

                    {/* Stars data */}
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
                      {star.stars.toLocaleString()} stars{" "}
                      {selectedType.shortText}
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
