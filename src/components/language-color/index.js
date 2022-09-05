import "./index.css";

function LanguageColor(props) {
  const languageColors = require("../../data/language-colors.json");

  const lang = languageColors[props.lang];

  var color = null;
  try {
    color = lang.color;
  } catch {
    return (
      <span
        style={{ backgroundColor: "#808080" }}
        className="repo-language-color"
      ></span>
    );
  }

  if (color === undefined || color === null) {
    return (
      <span
        style={{ backgroundColor: "#808080" }}
        className="repo-language-color"
      ></span>
    );
  }

  return (
    <span
      style={{ backgroundColor: color }}
      className="repo-language-color"
    ></span>
  );
}

export default LanguageColor;
