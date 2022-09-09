import { Box, Heading, Text, CircleBadge } from "@primer/react";
import { StarIcon } from "@primer/octicons-react";
import MainFooter from "../../components/footer";
import MainHeader from "../../components/header";
import Stars from "../../components/stars";

import "./index.css";

function Start() {
  return (
    <>
      <MainHeader />
      <Box bg="canvas.default" className="center">
        <Box
          bg="canvas.subtle"
          className="border-bottom main-header border-color-muted"
        >
          <CircleBadge variant="small" inline={true} sx={{mb: 15}}>
            <CircleBadge.Icon icon={StarIcon} />
          </CircleBadge>
          <Heading as={"h1"} sx={{ fontSize: 5 }}>
            Trending
          </Heading>
          <Text as={"p"}>
            See what the GitHub community is most excited about today.
          </Text>
        </Box>
      </Box>
      <Stars />
      <MainFooter />
    </>
  );
}

export default Start;
