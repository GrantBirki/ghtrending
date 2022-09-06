import { Box, Heading, Text } from "@primer/react";
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
          borderColor={"fg.subtle"}
          className="border-bottom main-header"
        >
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
