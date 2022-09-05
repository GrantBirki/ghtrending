import { Box } from "@primer/react";
import DateRangeToggle from "../../components/date-range";
import Stars from "../../components/stars";

import "./index.css";

function Start() {
  return (
    <>
      <div className="center">
        <div className="border-bottom main-header bg-color-muted">
          <h1>Trending</h1>
          <p className="f4 color-fg-muted col-md-6 mx-auto">
            See what the GitHub community is most excited about today.
          </p>
        </div>
      </div>
      <Box>
        <div className="container-lg">
          <div className="container-lg-header bg-color-muted">
            <div></div>
            <div className="table-header-options">
              <DateRangeToggle />
            </div>
          </div>
          <div className="container-table">
            <Stars />
          </div>
        </div>
      </Box>
    </>
  );
}

export default Start;
