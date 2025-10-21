import { register } from "node:module";
import { beforeEach } from "node:test";
import { JSDOM } from "jsdom";

// Set up DOM globals
global.window = new JSDOM("<!document html>").window;
global.document = window.document;

beforeEach(() => {
  // Reset the DOM before each test
  document.body.innerHTML = "";
});

// Registers a custom loader that simply drops CSS imports when executing tests
register("./testLoader.js", import.meta.url);
