import { Box, Heading, Text } from "@primer/react";
import MainHeader from "../../components/header";
import DateRangeToggle from "../../components/date-range";
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
      <Box bg="canvas.default" className="primary-header">
        <Box className="container-lg" borderColor={"fg.subtle"}>
          <Box
            bg="canvas.subtle"
            borderColor={"fg.subtle"}
            className="container-lg-header"
          >
            <Box></Box>
            <Box className="table-header-options">
              <DateRangeToggle />
            </Box>
          </Box>
          <Box className="container-table">
            <Stars />
          </Box>
        </Box>
      </Box>
    </>
  );
}

export default Start;
