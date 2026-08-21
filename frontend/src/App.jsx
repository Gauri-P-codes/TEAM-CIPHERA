import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import InputForm from "./components/InputForm";
import WasteBreakdown from "./components/WasteBreakdown";
import ResultsList from "./components/ResultsList";
import RevenueChart from "./components/RevenueChart";
import { fetchMeta, postEstimate } from "./api";

export default function App() {
  const [meta, setMeta] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchMeta().then(setMeta).catch(() => {});
  }, []);

  async function handleSubmit(payload) {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await postEstimate(payload);
      setResult(data);
    } catch (e) {
      setError(e.message || "Something went wrong. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-field-950 text-field-50">
      <header className="border-b border-field-800 px-6 md:px-10 py-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <p className="text-molasses-400 font-mono text-xs tracking-widest uppercase">Waste-to-value engine</p>
            <h1 className="font-display text-2xl md:text-3xl font-semibold mt-1">Sugarcane Byproduct Matcher</h1>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 md:px-10 py-10 grid lg:grid-cols-[420px_1fr] gap-8">
        <InputForm meta={meta} onSubmit={handleSubmit} loading={loading} />

        <div className="space-y-6">
          {!result && !loading && !error && (
            <div className="h-full min-h-[300px] flex items-center justify-center border-2 border-dashed border-field-800 rounded-2xl text-field-100/40 text-center px-8">
              Fill in the four inputs to see matched industries, transport costs, and revenue potential.
            </div>
          )}

          {loading && (
            <div className="h-full min-h-[300px] flex items-center justify-center text-field-100/60">
              Estimating waste streams and matching buyers…
            </div>
          )}

          {error && (
            <div className="bg-red-950/40 border border-red-800 text-red-200 rounded-2xl px-5 py-4">
              {error}
            </div>
          )}

          {result && (
            <>
              <div>
                <h2 className="font-display text-lg font-semibold mb-3">
                  Estimated waste streams
                  {result.is_peak_season && (
                    <span className="ml-3 text-xs font-body font-normal text-molasses-400 align-middle">
                      Peak crushing season — freight rates elevated
                    </span>
                  )}
                </h2>
                <WasteBreakdown breakdown={result.waste_breakdown} />
              </div>

              <RevenueChart results={result.results} />

              <div className="bg-molasses-500/10 border border-molasses-500/30 rounded-2xl px-5 py-4">
                <p className="text-xs uppercase tracking-wide text-molasses-400 mb-1">Recommendation</p>
                <p className="text-field-50/90 leading-relaxed">{result.explanation}</p>
              </div>

              <div>
                <h2 className="font-display text-lg font-semibold mb-3">Ranked options</h2>
                <ResultsList results={result.results} />
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
