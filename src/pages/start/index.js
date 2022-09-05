import { Box, ActionList } from "@primer/react";
import DateRangeToggle from "../../components/date-range";

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
            <ActionList>
              <ActionList.Item>Last 24 hours</ActionList.Item>
              <ActionList.Item>Last 7 days</ActionList.Item>
              <ActionList.Item>Last 30 days</ActionList.Item>
              <ActionList.Item
                onSelect={(event) => console.log("Date range changed TODO")}
              >
                All time
              </ActionList.Item>
            </ActionList>
          </div>
        </div>
      </Box>
    </>
  );
}

export default Start;
