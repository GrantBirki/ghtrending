import { ActionMenu, ActionList } from "@primer/react";

function DateRangeToggle() {
  return (
    <ActionMenu>
      <ActionMenu.Button>Date range</ActionMenu.Button>
      <ActionMenu.Overlay>
        <ActionList>
          <ActionList.Item>Last 24 hours</ActionList.Item>
          <ActionList.Item>Last 7 days</ActionList.Item>
          <ActionList.Item>Last 30 days</ActionList.Item>
          <ActionList.Item onSelect={(event) => console.log("Date range changed TODO")}>
            All time
          </ActionList.Item>
        </ActionList>
      </ActionMenu.Overlay>
    </ActionMenu>
  );
}

export default DateRangeToggle;
