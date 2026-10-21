import { useEffect, useState } from "react";
import { getMetrics, getModels } from "../api/models";
import type { Metrics, ModelInfo } from "../types/model";

export function useModels() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const [m, me] = await Promise.all([getModels(), getMetrics()]);
        if (active) {
          setModels(m);
          setMetrics(me);
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  return { models, metrics, loading, error };
}
