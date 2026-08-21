function inr(value) {
  return `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

const FEASIBILITY_STYLES = {
  High: "bg-field-700 text-field-50",
  Medium: "bg-molasses-500 text-field-950",
  Low: "bg-field-100 text-field-950/70",
};

export default function ResultsList({ results }) {
  return (
    <div className="space-y-4">
      {results.map((r, i) => (
        <div key={`${r.industry_key}-${r.waste_stream}`} className="bg-field-50 text-field-950 rounded-2xl p-5 md:p-6 shadow-xl">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-field-800/50">#{i + 1}</span>
                <h3 className="font-display text-xl font-semibold">{r.industry_label}</h3>
              </div>
              <p className="text-sm text-field-800/60 mt-0.5">
                {r.waste_quantity_tons.toLocaleString("en-IN")} t {r.waste_stream.replace("_", " ")} → {r.buyer_name} ({r.buyer_state})
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs font-medium px-3 py-1 rounded-full ${FEASIBILITY_STYLES[r.feasibility]}`}>
                {r.feasibility} feasibility
              </span>
              <div className="text-right">
                <p className="font-display text-2xl font-bold text-field-900">{r.sustainability_score}</p>
                <p className="text-[10px] uppercase tracking-wide text-field-800/50">score / 100</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 mt-5 text-sm">
            <Metric label="Distance" value={`${r.distance_km} km`} />
            <Metric label="Trucks needed" value={r.trucks_required} />
            <Metric label="Transport cost" value={inr(r.transport_cost_inr)} />
            <Metric label="Est. revenue" value={inr(r.estimated_revenue_inr)} />
            <Metric
              label="Net revenue"
              value={inr(r.net_revenue_inr)}
              accent={r.net_revenue_inr >= 0 ? "text-field-700" : "text-red-700"}
            />
            <Metric label="CO2 avoided" value={`${(r.co2_avoided_kg / 1000).toFixed(1)} t`} />
          </div>
        </div>
      ))}
    </div>
  );
}

function Metric({ label, value, accent = "text-field-950" }) {
  return (
    <div className="border-t border-field-700/15 pt-2">
      <p className="text-[11px] uppercase tracking-wide text-field-800/50">{label}</p>
      <p className={`font-medium ${accent}`}>{value}</p>
    </div>
  );
}
