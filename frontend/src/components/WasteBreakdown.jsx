const STREAM_LABELS = {
  bagasse: "Bagasse",
  press_mud: "Press mud",
  trash: "Field trash",
  molasses: "Molasses (est.)",
};

export default function WasteBreakdown({ breakdown }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {Object.entries(breakdown).map(([key, value]) => (
        <div key={key} className="bg-field-900/60 border border-field-700 rounded-xl px-4 py-3">
          <p className="text-xs uppercase tracking-wide text-molasses-300">{STREAM_LABELS[key] || key}</p>
          <p className="font-display text-2xl font-semibold mt-1">
            {value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
            <span className="text-sm font-body font-normal text-field-100/60 ml-1">t</span>
          </p>
        </div>
      ))}
    </div>
  );
}
