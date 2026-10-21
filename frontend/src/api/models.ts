import { api } from "./client";
import type { Metrics, ModelInfo } from "../types/model";

export async function getModels(): Promise<ModelInfo[]> {
  const { data } = await api.get<ModelInfo[]>("/models");
  return data;
}

export async function getMetrics(): Promise<Metrics> {
  const { data } = await api.get<Metrics>("/metrics");
  return data;
}

export async function getHealth(): Promise<{ status: string; models: Record<string, boolean> }> {
  const { data } = await api.get("/health");
  return data;
}
