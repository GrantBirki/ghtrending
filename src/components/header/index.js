import { Header, StyledOcticon } from "@primer/react";
import { StarIcon } from "@primer/octicons-react";

function MainHeader() {
  return (
    <Header
      sx={{
        backgroundColor: "checks.bg",
      }}
    >
      <Header.Item
        sx={{
          fontSize: 2,
        }}
      >
        <StyledOcticon icon={StarIcon} size={32} sx={{ mr: 2 }} />
        <span>GitHub Trending</span>
      </Header.Item>
    </Header>
  );
}

export default MainHeader;
