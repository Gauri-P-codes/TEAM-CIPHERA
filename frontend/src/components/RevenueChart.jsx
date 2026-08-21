import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";

const BAR_COLORS = ["#d9a441", "#357048", "#c98a2d", "#275735", "#e8bf70"];

function formatINR(value) {
  if (Math.abs(value) >= 1e7) return `₹${(value / 1e7).toFixed(1)}Cr`;
  if (Math.abs(value) >= 1e5) return `₹${(value / 1e5).toFixed(1)}L`;
  if (Math.abs(value) >= 1e3) return `₹${(value / 1e3).toFixed(0)}K`;
  return `₹${value}`;
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-field-950 text-field-50 text-sm rounded-lg px-3 py-2 shadow-lg border border-field-700">
      <p className="font-medium">{d.industry_label}</p>
      <p className="font-mono text-molasses-300">Net revenue: {formatINR(d.net_revenue_inr)}</p>
      <p className="text-field-100/70 text-xs">Score: {d.sustainability_score}/100</p>
    </div>
  );
}

export default function RevenueChart({ results }) {
  const data = results.map((r) => ({
    ...r,
    name: r.industry_label.split(" / ")[0],
  }));

  return (
    <div className="bg-field-50 text-field-950 rounded-2xl p-6 shadow-xl">
      <h3 className="font-display text-xl font-semibold mb-4">Net revenue by industry</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5ded0" vertical={false} />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#14301f" }} />
          <YAxis tickFormatter={formatINR} tick={{ fontSize: 11, fill: "#14301f" }} width={60} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#eaf1e7" }} />
          <Bar dataKey="net_revenue_inr" radius={[6, 6, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
