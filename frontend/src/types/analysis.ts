export interface RowResult {
  row: number;
  label: "Benign" | "Attack";
  confidence: number;
  category: string | null;
  category_confidence: number | null;
}

export interface AnalysisSummary {
  id: string;
  filename: string;
  created_at: string;
  total_rows: number;
  benign_count: number;
  attack_count: number;
  attack_rate: number;
  categories: Record<string, number>;
}

export interface AnalysisDetail extends AnalysisSummary {
  model_name: string;
  row_results: RowResult[];
}
