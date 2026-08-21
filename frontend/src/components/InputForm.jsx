import { useState } from "react";
import LocationMap from "./LocationMap";

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const DISPOSAL_LABELS = {
  burned_in_field: "Burned in field",
  dumped_unused: "Dumped / left unused",
  partially_composted: "Partially composted",
  partially_utilized: "Already partially utilized",
};

export default function InputForm({ meta, onSubmit, loading }) {
  const [locationLabel, setLocationLabel] = useState("");
  const [lat, setLat] = useState(null);
  const [lon, setLon] = useState(null);
  const [production, setProduction] = useState("");
  const [disposal, setDisposal] = useState("burned_in_field");
  const [seasonStart, setSeasonStart] = useState(11);
  const [seasonEnd, setSeasonEnd] = useState(4);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [formError, setFormError] = useState("");

  const disposalMethods = meta?.disposal_methods || Object.keys(DISPOSAL_LABELS);

  function handlePick(pickedLat, pickedLon) {
    setLat(pickedLat);
    setLon(pickedLon);
    if (!locationLabel) {
      setLocationLabel(`${pickedLat.toFixed(4)}, ${pickedLon.toFixed(4)}`);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (lat === null || lon === null) {
      setFormError("Pin your location on the map before submitting.");
      return;
    }
    if (!production || Number(production) <= 0) {
      setFormError("Enter sugarcane production greater than zero.");
      return;
    }
    setFormError("");
    onSubmit({
      location_label: locationLabel || `${lat.toFixed(4)}, ${lon.toFixed(4)}`,
      lat,
      lon,
      production_tons: Number(production),
      disposal_method: disposal,
      season_start_month: Number(seasonStart),
      season_end_month: Number(seasonEnd),
      current_month: Number(currentMonth),
    });
  }

  return (
    <form onSubmit={handleSubmit} className="bg-field-50 text-field-950 rounded-2xl p-6 md:p-8 shadow-xl">
      <h2 className="font-display text-2xl font-semibold mb-1">Field inputs</h2>
      <p className="text-field-800/70 text-sm mb-6">
        Four inputs are all we need — the engine derives everything else.
      </p>

      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium mb-2">
            1. Location <span className="text-field-800/50 font-normal">— click the map to drop a pin</span>
          </label>
          <LocationMap lat={lat} lon={lon} onPick={handlePick} />
          <input
            type="text"
            value={locationLabel}
            onChange={(e) => setLocationLabel(e.target.value)}
            placeholder="Label this location (district / mill name)"
            className="mt-2 w-full rounded-lg border border-field-700/30 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-molasses-500"
          />
          {lat !== null && (
            <p className="text-xs text-field-800/60 mt-1 font-mono">
              {lat.toFixed(4)}, {lon.toFixed(4)}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            2. Sugarcane production (tonnes)
          </label>
          <input
            type="number"
            min="1"
            step="any"
            value={production}
            onChange={(e) => setProduction(e.target.value)}
            placeholder="e.g. 50000"
            className="w-full rounded-lg border border-field-700/30 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-molasses-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">3. Current disposal method</label>
          <select
            value={disposal}
            onChange={(e) => setDisposal(e.target.value)}
            className="w-full rounded-lg border border-field-700/30 px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-molasses-500"
          >
            {disposalMethods.map((m) => (
              <option key={m} value={m}>
                {DISPOSAL_LABELS[m] || m}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">4. Harvest / crushing season</label>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <span className="text-xs text-field-800/60">Season starts</span>
              <select
                value={seasonStart}
                onChange={(e) => setSeasonStart(e.target.value)}
                className="w-full rounded-lg border border-field-700/30 px-2 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-molasses-500"
              >
                {MONTHS.map((m, i) => (
                  <option key={m} value={i + 1}>{m}</option>
                ))}
              </select>
            </div>
            <div>
              <span className="text-xs text-field-800/60">Season ends</span>
              <select
                value={seasonEnd}
                onChange={(e) => setSeasonEnd(e.target.value)}
                className="w-full rounded-lg border border-field-700/30 px-2 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-molasses-500"
              >
                {MONTHS.map((m, i) => (
                  <option key={m} value={i + 1}>{m}</option>
                ))}
              </select>
            </div>
            <div>
              <span className="text-xs text-field-800/60">Current month</span>
              <select
                value={currentMonth}
                onChange={(e) => setCurrentMonth(e.target.value)}
                className="w-full rounded-lg border border-field-700/30 px-2 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-molasses-500"
              >
                {MONTHS.map((m, i) => (
                  <option key={m} value={i + 1}>{m}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {formError && (
        <p className="text-red-700 text-sm mt-4 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {formError}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="mt-6 w-full bg-field-900 hover:bg-field-800 disabled:opacity-50 text-field-50 font-medium rounded-lg py-3 transition-colors"
      >
        {loading ? "Matching industries…" : "Find best waste-to-value options"}
      </button>
    </form>
  );
}
