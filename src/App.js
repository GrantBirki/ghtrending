import React from "react";
import { ThemeProvider, BaseStyles } from "@primer/react";

import Start from "./pages/start";

function App() {
  return (
    <ThemeProvider colorMode="auto" dayScheme="light" nightScheme="dark_dimmed">
      <BaseStyles>
        <Start />
      </BaseStyles>
    </ThemeProvider>
  );
}

export default App;
