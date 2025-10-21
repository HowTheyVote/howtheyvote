// This is a hacky workaround to fix CSS and image imports during test execution
export function load(url, _, nextLoad) {
  if (/\.css$/.test(url)) {
    return {
      format: "module",
      shortCircuit: true,
      source: "export default {};",
    };
  }

  if (/\.(png|jpg|svg)/.test(url)) {
    return {
      format: "module",
      shortCircuit: true,
      source: `export default "${url}";`,
    };
  }

  return nextLoad(url);
}
