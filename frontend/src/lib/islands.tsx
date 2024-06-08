import {
  type ComponentChildren,
  type ComponentType,
  hydrate,
  toChildArray,
} from "preact";

type IslandProps = {
  children: ComponentChildren;
};

export function Island({ children }: IslandProps) {
  const childArr = toChildArray(children);

  if (childArr.length !== 1) {
    throw new Error(
      `Islands must have exactly one child. This islands has ${childArr.length} children.`,
    );
  }

  const child = childArr[0];

  if (typeof child !== "object" || typeof child.type !== "function") {
    throw new Error("Islands must have only components as children.");
  }

  const component = child.type.name;
  const props = JSON.stringify(child.props);

  return (
    <div
      style="display:contents"
      data-island-component={component}
      data-island-props={props}
    >
      {children}
    </div>
  );
}

// biome-ignore lint/suspicious/noExplicitAny: No idea how to type this correctly
export function hydrateIslands(components: Array<ComponentType<any>>) {
  for (const Component of components) {
    const name = Component.name;
    const islands = document.querySelectorAll(
      `[data-island-component="${name}"]`,
    );

    for (const island of Array.from(islands)) {
      if (!(island instanceof window.HTMLElement)) {
        return;
      }

      const props = JSON.parse(island.dataset.islandProps || "{}") as object;
      hydrate(<Component {...props} />, island);
    }
  }
}
