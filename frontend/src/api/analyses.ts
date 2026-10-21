import { api } from "./client";
import type { AnalysisDetail, AnalysisSummary } from "../types/analysis";

export async function uploadCsv(
  file: File,
  onProgress?: (pct: number) => void,
): Promise<AnalysisDetail> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<AnalysisDetail>("/analyze-csv", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });
  return data;
}

export async function listAnalyses(): Promise<AnalysisSummary[]> {
  const { data } = await api.get<AnalysisSummary[]>("/analyses");
  return data;
}

export async function getAnalysis(id: string): Promise<AnalysisDetail> {
  const { data } = await api.get<AnalysisDetail>(`/analyses/${id}`);
  return data;
}

export function downloadUrl(id: string): string {
  return `${api.defaults.baseURL}/analyses/${id}/download`;
}
