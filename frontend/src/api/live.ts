import { api } from "./client";

export function liveStreamUrl(): string {
  return `${api.defaults.baseURL}/live/stream`;
}

export async function simulateAttack(count = 20): Promise<void> {
  await api.post(`/live/simulate?count=${count}`);
}
