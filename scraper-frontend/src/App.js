import React, { useState, useEffect } from "react";
import { SUGGESTED_URLS } from "./config";
import { Toast } from "./components/Toast";
import { useScraper } from "./hooks/useScraper";

function App() {
  const [url, setUrl] = useState("");
  const [toastMessage, setToastMessage] = useState(null);

  const { result, loading, error, scrape } = useScraper();
  const hostname = result ? new URL(result.url).hostname : null;

  const showToast = (msg) => setToastMessage(msg);

  // ------------------------------
  // URL VALIDATOR (STRONG VERSION)
  // ------------------------------
  const isValidURL = (input) => {
    if (!input) return false;

    let test = input.trim();

    if (!/^https?:\/\//i.test(test)) {
      test = "https://" + test;
    }

    try {
      const urlObj = new URL(test);
      const host = urlObj.hostname;

      if (!host) return false;

      // Allow localhost
      if (host === "localhost") return true;

      // Allow IPv4
      if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host)) return true;

      const parts = host.split(".");
      if (parts.length < 2) return false;

      if (parts.some((p) => !p)) return false;

      const tld = parts[parts.length - 1];
      if (tld.length < 2 || !/^[a-zA-Z]{2,}$/.test(tld)) return false;

      if (!/^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*$/.test(host)) return false;

      return true;
    } catch {
      return false;
    }
  };

  // ------------------------------
  // AUTO HTTPS
  // ------------------------------
  const normalizeUrl = (input) => {
    if (!input) return "";
    let clean = input.trim();

    if (!/^https?:\/\//i.test(clean)) {
      clean = "https://" + clean;
    }
    return clean;
  };

  // ------------------------------
  // SCRAPE HANDLER
  // ------------------------------
  const handleScrape = async () => {
    const original = url.trim();

    if (!isValidURL(original)) {
      showToast("Invalid URL format ❌");
      return;
    }

    const finalUrl = normalizeUrl(original);

    if (finalUrl !== original) {
      setUrl(finalUrl);
      showToast("Auto-added https:// ✔");
    }

    try {
      await scrape(finalUrl);
      showToast("Scrape complete ✔");
    } catch (err) {
      showToast(err.message || "Scrape failed ❌");
    }
  };

  // ENTER KEY GLOBAL LISTENER
  
  useEffect(() => {
    const onEnter = (e) => {
      if (e.key === "Enter") {
        e.preventDefault();

        if (!url.trim()) {
          showToast("Please enter a valid URL.");
          return;
        }

        handleScrape();
      }
    };

    window.addEventListener("keydown", onEnter);
    return () => window.removeEventListener("keydown", onEnter);
  }, [url]);

  // ------------------------------
  // DOWNLOAD JSON
  // ------------------------------
  const downloadJSON = () => {
    if (!result) return;

    const blob = new Blob([JSON.stringify({ result }, null, 2)], {
      type: "application/json",
    });

    const urlObj = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = urlObj;
    a.download = "scrape-result.json";
    a.click();
    URL.revokeObjectURL(urlObj);

    showToast("JSON downloaded 📄");
  };

  // ------------------------------

  return (
    <div className="min-h-screen bg-black text-gray-200 flex justify-center px-4 py-10 relative">

      {/* Toast */}
      <Toast message={toastMessage} onClose={() => setToastMessage(null)} />

      <div className="w-full max-w-4xl space-y-6">

        {/* Badge */}
        <div className="flex items-center justify-between mb-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-black/50 border border-gray-700 px-3 py-1 text-xs text-gray-400">
            <span className="inline-block h-2 w-2 rounded-full bg-green-600 animate-pulse" />
            <span>Lyftr Universal Scraper · MVP</span>
          </div>

          {hostname && (
            <span className="text-xs text-gray-500 hidden sm:block">{hostname}</span>
          )}
        </div>

        {/* Main Card */}
        <div
          className="rounded-2xl border border-gray-700 bg-black/80 shadow-xl shadow-black/80
                     backdrop-blur-sm p-5 sm:p-7 space-y-6 hover:border-green-700/50
                     transition-all duration-300"
        >

          <div className="space-y-2">
            <h1 className="text-3xl font-semibold tracking-tight text-white">
              Universal Website Scraper
            </h1>
            <p className="text-sm text-gray-400">
              Paste any public URL to fetch, render JS, scroll, click, and extract JSON.
            </p>
          </div>

          {/* URL Input */}
          <div className="space-y-3">
            <label className="text-xs text-gray-400 uppercase tracking-wide">Target URL</label>

            <div className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                placeholder="https://example.com"
                value={url}
                className="flex-1 rounded-xl bg-black/70 border border-gray-700 px-4 py-2.5
                           text-sm shadow-inner text-gray-100 placeholder:text-gray-500
                           focus:outline-none focus:ring-2 focus:ring-green-600"
                onChange={(e) => setUrl(e.target.value)}
              />

              <button
                onClick={handleScrape}
                disabled={loading}
                className="rounded-xl bg-green-700 px-5 py-2.5 text-sm font-semibold text-black
                           shadow-lg shadow-green-900/40 hover:bg-green-600 transition disabled:opacity-50
                           flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <span className="h-3 w-3 rounded-full border-2 border-black border-b-transparent animate-spin" />
                    Scraping…
                  </>
                ) : "Scrape"}
              </button>
            </div>

            {/* Suggested URLs */}
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_URLS.map((u) => (
                <button
                  key={u}
                  type="button"
                  onClick={() => {
                    setUrl(u);
                    showToast(`URL selected: ${u}`);
                  }}
                  className="rounded-full border border-gray-700 bg-black/50 px-3 py-1 text-[11px]
                             text-gray-300 hover:border-green-600 hover:text-green-300 transition"
                >
                  {new URL(u).hostname}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="rounded-xl border border-red-600 bg-red-950/80 px-3 py-2 text-sm text-red-200">
              {error}
            </div>
          )}

          {/* Empty */}
          {!result && !loading && !error && (
            <div className="rounded-xl border border-gray-700 border-dashed bg-black/40 px-4 py-6 text-sm text-gray-500">
              Run your first scrape to view structured metadata and sections.
            </div>
          )}

          {/* Result Output */}
          {result && (
            <div className="space-y-6">

              {/* Meta */}
              <section className="rounded-xl border border-gray-700 bg-black/60 p-4 shadow-[0_0_15px_rgba(0,255,140,0.08)]">
                <p className="text-green-400 font-semibold mb-2">Metadata</p>

                <p><span className="font-semibold text-gray-300">URL:</span> {result.url}</p>
                <p><span className="font-semibold text-gray-300">Title:</span> {result.meta.title || "(none)"}</p>
                <p><span className="font-semibold text-gray-300">Description:</span> {result.meta.description}</p>
                <p><span className="font-semibold text-gray-300">Language:</span> {result.meta.language}</p>
              </section>

              {/* Interactions */}
              <section className="rounded-xl border border-gray-700 bg-black/60 p-4 shadow-[0_0_15px_rgba(0,255,140,0.08)]">
                <p className="text-green-400 font-semibold mb-2">Interactions</p>
                <pre className="bg-black/80 border border-gray-700 p-2 rounded-lg text-xs overflow-auto max-h-48">
                  {JSON.stringify(result.interactions, null, 2)}
                </pre>
              </section>

              {/* Download JSON */}
              <button
                onClick={downloadJSON}
                className="w-full rounded-lg bg-black/50 border border-gray-700 hover:border-green-600
                           hover:text-green-300 px-4 py-2 text-sm transition"
              >
                Download JSON
              </button>

              {/* Sections */}
              <section className="space-y-3">
                {result.sections.map((section, idx) => (
                  <details
                    key={section.id || idx}
                    className="rounded-xl border border-gray-700 bg-black/60 p-3 shadow-[0_0_15px_rgba(0,255,140,0.05)]"
                    open={idx === 0}
                  >
                    <summary className="cursor-pointer font-semibold text-sm text-gray-100">
                      {section.label}{" "}
                      <span className="text-green-400 text-xs">{section.type}</span>
                    </summary>
                    <pre className="mt-2 max-h-80 overflow-auto rounded bg-black/80 border border-gray-700 p-2 text-xs">
                      {JSON.stringify(section, null, 2)}
                    </pre>
                  </details>
                ))}
              </section>
            </div>
          )}

        </div>
      </div>

    </div>
  );
}

export default App;
