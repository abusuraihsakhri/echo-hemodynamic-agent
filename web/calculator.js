/* Dependency-free echocardiographic arithmetic for the static browser UI.
 * This module deliberately does not diagnose valve disease, HFpEF, or pulmonary hypertension.
 */
(function (root) {
  "use strict";

  function number(value, name, optional) {
    if (value === undefined || value === null || String(value).trim() === "") {
      if (optional) return null;
      throw new Error(name + " is required.");
    }
    const n = Number(value);
    if (!Number.isFinite(n)) throw new Error(name + " must be a finite number.");
    return n;
  }

  function positive(value, name, optional) {
    const n = number(value, name, optional);
    if (n !== null && n <= 0) throw new Error(name + " must be greater than zero.");
    return n;
  }

  function nonnegative(value, name, optional) {
    const n = number(value, name, optional);
    if (n !== null && n < 0) throw new Error(name + " cannot be negative.");
    return n;
  }

  const round = (value, places) => Number(value.toFixed(places));

  function calculate(values) {
    const diameter = positive(values.lvotDiameter, "LVOT diameter");
    const vti = positive(values.lvotVti, "LVOT VTI");
    const hr = positive(values.heartRate, "Heart rate");
    const height = positive(values.height, "Height", true);
    const weight = positive(values.weight, "Weight", true);
    const pht = positive(values.pht, "Mitral pressure half-time", true);
    const tr = nonnegative(values.trVelocity, "TR peak velocity", true);
    const rap = nonnegative(values.rap, "Right atrial pressure", true);
    const ef = nonnegative(values.ef, "LVEF", true);
    const e = positive(values.eVelocity, "Mitral E velocity", true);
    const a = positive(values.aVelocity, "Mitral A velocity", true);
    const ePrime = positive(values.ePrime, "Tissue Doppler e-prime", true);
    if ((height === null) !== (weight === null))
      throw new Error("Supply both height and weight to calculate cardiac index.");
    if ((tr === null) !== (rap === null))
      throw new Error("Supply both TR velocity and estimated right atrial pressure.");
    if ((e === null) !== (a === null))
      throw new Error("Supply both mitral E and A velocities.");
    if (ePrime !== null && e === null)
      throw new Error("Mitral E velocity is required for E/e-prime.");
    if (ef !== null && ef > 100) throw new Error("LVEF must be between 0 and 100%.");

    const area = Math.PI * (diameter / 2) ** 2;
    const strokeVolume = area * vti;
    const cardiacOutput = strokeVolume * hr / 1000;
    const results = {
      "LVOT area (cm²)": round(area, 3),
      "Stroke volume (mL)": round(strokeVolume, 2),
      "Cardiac output (L/min)": round(cardiacOutput, 3)
    };
    if (height !== null) {
      const bsa = 0.007184 * height ** 0.725 * weight ** 0.425;
      results["Body surface area (m², Du Bois)"] = round(bsa, 3);
      results["Cardiac index (L/min/m²)"] = round(cardiacOutput / bsa, 3);
    }
    if (pht !== null) results["Mitral valve area (cm², PHT estimate)"] = round(220 / pht, 3);
    if (tr !== null) results["Estimated RVSP (mmHg)"] = round(4 * tr * tr + rap, 2);
    if (ef !== null) results["LVEF (%)"] = ef;
    if (e !== null) {
      results["Mitral E/A ratio"] = round(e / a, 3);
      if (ePrime !== null) results["Mitral E/e-prime ratio"] = round(e / ePrime, 3);
    }
    if (Object.values(results).some((v) => !Number.isFinite(v)))
      throw new Error("The supplied measurements exceed the supported numerical range.");
    return results;
  }

  const api = Object.freeze({ calculate });
  root.EchoCalculator = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
