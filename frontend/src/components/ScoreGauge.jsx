import React from "react";

export default function ScoreGauge({ score, size = 60, strokeWidth = 5 }) {
  const normalizedScore = Math.min(100, Math.max(0, Math.round(score || 0)));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  // Signature color thresholds
  const strokeColor =
    normalizedScore >= 75
      ? "#10B981" // Distinct Emerald for high match
      : normalizedScore >= 45
      ? "#6366F1" // Electric Indigo signature accent
      : "#64748B"; // Muted Slate for lower match

  const trackColor = "rgba(255, 255, 255, 0.08)";

  return (
    <div
      style={{
        position: "relative",
        width: size,
        height: size,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
      title={`Match Score: ${normalizedScore}%`}
    >
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        {/* Track Ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={trackColor}
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress Gauge */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          style={{ transition: "stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1)" }}
        />
      </svg>
      {/* Monospace Tabular Percentage Text */}
      <div
        style={{
          position: "absolute",
          fontFamily: "'JetBrains Mono', 'Fira Code', ui-monospace, monospace",
          fontVariantNumeric: "tabular-nums",
          fontWeight: 700,
          fontSize: size <= 50 ? "0.75rem" : "0.95rem",
          color: strokeColor,
          letterSpacing: "-0.04em",
        }}
      >
        {normalizedScore}%
      </div>
    </div>
  );
}
