import { Box } from "@primer/react";
import DateRangeToggle from "../../components/date-range";
import Stars from "../../components/stars";

import "./index.css";

function Start() {
  return (
    <>
      <Box bg="canvas.default" className="center">
        <Box bg="canvas.subtle" className="border-bottom main-header">
          <h1>Trending</h1>
          <p>
            See what the GitHub community is most excited about today.
          </p>
        </Box>
      </Box>
      <Box bg="canvas.default" className="primary-header">
        <Box className="container-lg">
          <Box bg="canvas.subtle" className="container-lg-header">
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
