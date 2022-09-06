import { Box, Text, Link } from "@primer/react";
import "./index.css";

function MainFooter() {
  return (
    <Box bg="canvas.default" className="center">
      <Box
        bg="canvas.subtle"
        borderColor={"fg.subtle"}
        className="border-bottom main-header"
      >
        <Box paddingBottom={"10px"}>
          <Text fontSize={3}>ghtrending ❤️ open source</Text>
        </Box>
        <hr className="footer-hr"></hr>
        <Box paddingTop={"10px"}>
          <Text color={"fg.muted"}>
            <Link href="https://reactjs.org/">React</Link> -{" "}
            <Link href="https://primer.style/react/">Primer</Link> -{" "}
            <Link href="http://www.gharchive.org/">GHarchive</Link>
          </Text>
        </Box>

        <Box padding={"5px"}>
          <Text>
            <Link href="https://github.com/GrantBirki/ghtrending/">
              Source Code
            </Link>
          </Text>
        </Box>

        <Box>
          <Text color={"fg.muted"} fontSize={0}>
            This site is not associated with GitHub, Inc.
          </Text>
        </Box>
      </Box>
    </Box>
  );
}

export default MainFooter;
