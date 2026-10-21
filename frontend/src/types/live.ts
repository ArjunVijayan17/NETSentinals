export interface LiveFlow {
  type: "flow";
  source: "ambient" | "simulated";
  label: "Benign" | "Attack";
  confidence: number;
  category: string | null;
  category_confidence: number | null;
  timestamp: string;
}
