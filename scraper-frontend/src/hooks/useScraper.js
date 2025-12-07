import { useState, useCallback } from "react";
import { API_BASE } from "../config";


export function useScraper() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const scrape = useCallback(async (url) => {
    if (!url.trim()) {
      throw new Error("Please enter a valid URL.");
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const text = await res.text();
      let data = null;

      try {
        data = text ? JSON.parse(text) : null;
      } catch {
        throw new Error(
          `Backend returned non-JSON (status ${res.status}): ${text.slice(
            0,
            200
          )}`
        );
      }

      if (!res.ok) {
        throw new Error(
          (data && data.detail) || `Request failed (status ${res.status})`
        );
      }

      setResult(data.result);
      return data.result;
    } catch (err) {
      setError(err.message || "Unknown error occurred");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, scrape };
}
