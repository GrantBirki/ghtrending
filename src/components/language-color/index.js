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
        key={`${props.repo_url}-language-color`}
        style={{ backgroundColor: "#808080" }}
        className="repo-language-color"
      ></span>
    );
  }

  if (color === undefined || color === null) {
    return (
      <span
        key={`${props.repo_url}-language-color`}
        style={{ backgroundColor: "#808080" }}
        className="repo-language-color"
      ></span>
    );
  }

  return (
    <span
      key={`${props.repo_url}-language-color`}
      style={{ backgroundColor: color }}
      className="repo-language-color"
    ></span>
  );
}

export default LanguageColor;
