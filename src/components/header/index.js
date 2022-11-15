import {
  Header,
  Text,
  useTheme,
  ToggleSwitch,
  CircleBadge,
} from "@primer/react";
import { useState } from "react";
import { StarIcon } from "@primer/octicons-react";

function MainHeader() {
  var iconFill = "";
  const { setColorMode, colorScheme } = useTheme();

  var checked = false;
  if (colorScheme === "light") {
    checked = true;
    iconFill = "#24292f";
  } else {
    checked = false;
    iconFill = "#cdd9e5";
  }

  const [isOn, setIsOn] = useState(checked);

  const onClick = () => {
    setIsOn(!isOn);
  };

  const handleSwitchChange = (on) => {
    if (on) {
      setColorMode("light");
      // set body background color to white
      document.body.style.backgroundColor = "#fff";
    } else {
      setColorMode("dark");
      // set body background color to dark
      document.body.style.backgroundColor = "#24292f";
    }
  };

  return (
    <Header>
      <Header.Item
        sx={{
          fontSize: 2,
        }}
      >
        <Header.Link href="/">
          <CircleBadge size={32} sx={{ mr: 2 }}>
            <CircleBadge.Icon icon={StarIcon} sx={{ fill: iconFill }} />
          </CircleBadge>
          <Text>GitHub Trending</Text>
        </Header.Link>
      </Header.Item>
      <Header.Item>
        <Header.Link href="/about">About</Header.Link>
      </Header.Item>
      <Header.Item full>
        <Header.Link href="https://github.com/GrantBirki/ghtrending">
          Code
        </Header.Link>
      </Header.Item>
      <Header.Item mr={0}>
        <ToggleSwitch
          defaultChecked={isOn}
          onClick={onClick}
          onChange={handleSwitchChange}
          checked={isOn}
          aria-labelledby="switchLabel"
          size="small"
          statusLabelPosition="end"
        />
      </Header.Item>
    </Header>
  );
}

export default MainHeader;
