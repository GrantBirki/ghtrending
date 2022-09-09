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
          <Box className="center"><Text as={"p"}>ghtrending is an open source site to aggregate and display various "trending" information about GitHub. This project is open source and made for the community to help people discover new and exciting GitHub projects!</Text></Box>
        </Box>
      </Box>
    </>
  );
}

export default About;
