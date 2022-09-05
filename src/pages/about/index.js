import { Box, Heading, Text } from "@primer/react";
import MainHeader from "../../components/header";

function About() {
  return (
    <>
      <MainHeader />
      <Box bg="canvas.default" className="center">
        <Box height={"100vh"} bg="canvas.subtle" borderColor={"fg.subtle"}>
          <Heading as={"h1"} sx={{ fontSize: 5 }}>
            About
          </Heading>
          <Text as={"p"}>TODO</Text>
        </Box>
      </Box>
    </>
  );
}

export default About;
