export interface ModelInfo {
  name: string;
  role: string;
  feature_count: number;
  classes: string[];
}

export interface ClassMetric {
  precision: number;
  recall: number;
  f1: number;
  support: number;
}

export interface BinarySummary {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
}

export interface ConfusionMatrix {
  labels: string[];
  matrix: number[][];
}

export interface BinaryMetric {
  summary: BinarySummary;
  report: Record<string, ClassMetric>;
  confusion_matrix: ConfusionMatrix;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

export interface Metrics {
  dataset: {
    name: string;
    test_rows: number;
    benign_rows: number;
    attack_rows: number;
    disclaimer: string;
  };
  binary: Record<string, BinaryMetric>;
  attack_type: {
    summary: {
      accuracy: number;
      precision_macro: number;
      recall_macro: number;
      f1_macro: number;
      f1_weighted: number;
      support: number;
    };
    class_report: Array<ClassMetric & { class: string }>;
  };
  feature_importance: {
    binary: FeatureImportance[];
    attack_type: FeatureImportance[];
  };
}
