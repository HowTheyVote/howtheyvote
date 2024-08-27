import type { FunctionComponent, VNode } from "preact";
import { useRef, useState } from "preact/hooks";
import "./Tabs.css";

type PanelProps = {
  id: string;
  label: string;
};

const Panel: FunctionComponent<PanelProps> = ({ children }) => {
  return <>{children}</>;
};

type TabsComponent = FunctionComponent & { Panel: typeof Panel };

const Tabs: TabsComponent = ({ children }) => {
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const tablistRef = useRef<HTMLDivElement>(null);

  const panels = (Array.isArray(children) ? children : [children]).filter(
    (child) => child.type === Panel,
  );

  const focusTab = (index: number) => {
    const tabs = tablistRef.current?.querySelectorAll("button[role='tab']");

    if (!tabs) {
      return;
    }

    const tab = tabs[index];

    if (!tab || !(tab instanceof HTMLElement)) {
      return;
    }

    tab.focus();
  };

  const onCycle = (diff: number) => {
    let newIndex = (selectedIndex + diff) % panels.length;

    if (newIndex < 0) {
      newIndex = panels.length + newIndex;
    }

    setSelectedIndex(newIndex);
    focusTab(newIndex);
  };

  const onKeyDown = (event: KeyboardEvent) => {
    if (event.key === "ArrowRight") {
      onCycle(1);
    }

    if (event.key === "ArrowLeft") {
      onCycle(-1);
    }
  };

  return (
    <div class="tabs">
      <div
        class="tabs__tablist"
        role="tablist"
        onKeyDown={onKeyDown}
        ref={tablistRef}
      >
        {panels.map((panel: VNode<PanelProps>, index: number) => (
          <button
            key={panel.props.id}
            type="button"
            class="tabs__button"
            id={panel.props.id}
            role="tab"
            aria-selected={selectedIndex === index}
            onClick={() => setSelectedIndex(index)}
          >
            {panel.props.label}
          </button>
        ))}
      </div>

      {panels.map((panel: VNode<PanelProps>, index: number) => (
        <div
          key={panel.props.id}
          class="tabs__panel"
          role="tabpanel"
          aria-labelledby={panel.props.id}
          hidden={index !== selectedIndex}
        >
          {panel}
        </div>
      ))}
    </div>
  );
};

Tabs.Panel = Panel;

export default Tabs;
