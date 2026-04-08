// Mock for next/font/google - returns a function that produces
// an object with className and variable properties
function fontFactory() {
  return { className: "mocked-font", variable: "--mocked-font", style: { fontFamily: "mocked" } };
}

module.exports = {
  Geist: fontFactory,
  Geist_Mono: fontFactory,
};
