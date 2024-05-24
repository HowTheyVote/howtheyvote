// This is a hacky workaround to fix CSS imports during test execution
export function load(url, _, nextLoad) {
  if (/\.css$/.test(url)) {
    return {
      format: "module",
      shortCircuit: true,
      source: "export default {};",
    };
  }

  return nextLoad(url);
}
