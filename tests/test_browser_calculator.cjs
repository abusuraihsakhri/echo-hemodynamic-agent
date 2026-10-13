"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { calculate } = require("../web/calculator.js");
const sample = () => ({
  lvotDiameter: "2", lvotVti: "22", heartRate: "72",
  height: "", weight: "", pht: "", trVelocity: "",
  rap: "", ef: "", eVelocity: "", aVelocity: "", ePrime: ""
});

test("LVOT area, stroke volume, and cardiac output", () => {
  const actual = calculate(sample());
  assert.equal(actual["LVOT area (cm²)"], 3.142);
  assert.equal(actual["Stroke volume (mL)"], 69.12);
  assert.equal(actual["Cardiac output (L/min)"], 4.976);
});

test("Du Bois BSA, cardiac index, PHT, RVSP, and ratios", () => {
  const actual = calculate({ ...sample(), height: "170", weight: "70", pht: "220",
    trVelocity: "3", rap: "10", ef: "55", eVelocity: "80",
    aVelocity: "60", ePrime: "10" });
  assert.ok(actual["Body surface area (m², Du Bois)"] > 1.7);
  assert.ok(actual["Cardiac index (L/min/m²)"] > 2.5);
  assert.equal(actual["Mitral valve area (cm², PHT estimate)"], 1);
  assert.equal(actual["Estimated RVSP (mmHg)"], 46);
  assert.equal(actual["Mitral E/A ratio"], 1.333);
  assert.equal(actual["Mitral E/e-prime ratio"], 8);
});

test("reject non-finite, incomplete and invalid measurements", () => {
  assert.throws(() => calculate({ ...sample(), heartRate: "0" }), /greater than zero/);
  assert.throws(() => calculate({ ...sample(), heartRate: "Infinity" }), /finite/);
  assert.throws(() => calculate({ ...sample(), heartRate: "oops" }), /finite/);
  assert.throws(() => calculate({ ...sample(), height: "170" }), /both height and weight/);
  assert.throws(() => calculate({ ...sample(), rap: "10" }), /both TR velocity/);
  assert.throws(() => calculate({ ...sample(), ef: "101" }), /between 0 and 100/);
  assert.throws(() => calculate({ ...sample(), ePrime: "8" }), /Mitral E velocity is required/);
  assert.throws(() => calculate({ ...sample(), pht: "-1" }), /greater than zero/);
});
