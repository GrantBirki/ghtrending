import { Text } from "@primer/react";
import "./index.css";

function LanguageColor(props) {
  const languageColors = require("../../data/language-colors.json");

  const lang = languageColors[props.lang];

  var color = null;
  try {
    color = lang.color;
  } catch {
    return (
      <Text
        as={"span"}
        key={`${props.repo_url}-language-color`}
        style={{ backgroundColor: "#808080" }}
        className="repo-language-color"
      ></Text>
    );
  }

  if (color === undefined || color === null) {
    return (
      <Text
        as={"span"}
        key={`${props.repo_url}-language-color`}
        style={{ backgroundColor: "#808080" }}
        className="repo-language-color"
      ></Text>
    );
  }

  return (
    <Text
      as={"span"}
      key={`${props.repo_url}-language-color`}
      style={{ backgroundColor: color }}
      className="repo-language-color"
    ></Text>
  );
}

export default LanguageColor;
