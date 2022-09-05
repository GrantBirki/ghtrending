import { ActionMenu, ActionList } from "@primer/react";
import { useState } from "react";
import { CalendarIcon } from "@primer/octicons-react";
import './index.css';

const fieldTypes = [
  { icon: CalendarIcon, name: "Last 24 hours" },
  { icon: CalendarIcon, name: "Last 7 days" },
  { icon: CalendarIcon, name: "Last 30 days" },
  { icon: CalendarIcon, name: "All time" },
];

function DateRangeToggle() {
  const [selectedIndex, setSelectedIndex] = useState(1);
  const selectedType = fieldTypes[selectedIndex];

  return (
    <ActionMenu>
      <ActionMenu.Button
        aria-label="Date range"
        leadingIcon={selectedType.icon}
        className={"header-option"}
      >
        {selectedType.name}
      </ActionMenu.Button>
      <ActionMenu.Overlay width="medium">
        <ActionList selectionVariant="single">
          {fieldTypes.map((type, index) => (
            <ActionList.Item
              key={index}
              selected={index === selectedIndex}
              onSelect={() => setSelectedIndex(index)}
            >
              <ActionList.LeadingVisual>
                <type.icon />
              </ActionList.LeadingVisual>
              {type.name}
            </ActionList.Item>
          ))}
        </ActionList>
      </ActionMenu.Overlay>
    </ActionMenu>
  );
}

export default DateRangeToggle;
