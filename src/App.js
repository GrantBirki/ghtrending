import React from "react";
import { ThemeProvider, BaseStyles } from "@primer/react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import Start from "./pages/start";
import About from "./pages/about";

function App() {
  return (
    <ThemeProvider colorMode="auto" dayScheme="light" nightScheme="dark_dimmed">
      <BaseStyles>
        <Router>
          <Routes>
            <Route path="/" element={<Start />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </Router>
      </BaseStyles>
    </ThemeProvider>
  );
}

export default App;
