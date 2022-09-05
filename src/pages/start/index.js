import { Box } from "@primer/react";
import DateRangeToggle from "../../components/date-range";
import Stars from "../../components/stars";

import "./index.css";

function Start() {
  return (
    <>
      <Box bg="canvas.default" className="center">
        <div className="border-bottom main-header bg-color-muted">
          <h1>Trending</h1>
          <p>
            See what the GitHub community is most excited about today.
          </p>
        </div>
      </Box>
      <Box bg="canvas.default" className="primary-header">
        <div className="container-lg">
          <Box bg="canvas.subtle" className="container-lg-header">
            <div></div>
            <div className="table-header-options">
              <DateRangeToggle />
            </div>
          </Box>
          <div className="container-table">
            <Stars />
          </div>
        </div>
      </Box>
    </>
  );
}

export default Start;
