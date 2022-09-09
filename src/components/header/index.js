import {
  Header,
  StyledOcticon,
  Text,
  useTheme,
  ToggleSwitch,
  Flash,
} from "@primer/react";
import { useState } from "react";
import { StarIcon } from "@primer/octicons-react";

function MainHeader() {
  const { setColorMode, colorScheme } = useTheme();

  var checked = false;
  if (colorScheme === "light") {
    checked = true;
  }

  const [isOn, setIsOn] = useState(checked);

  const onClick = () => {
    setIsOn(!isOn);
  };

  const handleSwitchChange = (on) => {
    if (on) {
      setColorMode("light");
    } else {
      setColorMode("dark");
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
          <StyledOcticon icon={StarIcon} size={32} sx={{ mr: 2 }} />
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
