import { Box } from "@primer/react";
import DateRangeToggle from "../../components/date-range";

function Start() {
  return (
    <>
      <Box
        borderColor="border.default"
        borderWidth={1}
        borderStyle="solid"
        p={3}
      >
        <h1>Trending</h1>
      </Box>
      <DateRangeToggle />
    </>
  );
}

export default Start;
