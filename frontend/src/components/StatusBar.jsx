import React from "react";

export default function StatusBar({ status }) {
  const memoryCounts = status?.memory_counts || {};

  return (
    <div className="status-bar">
      <div className="status-copy">
        <strong>System design:</strong> static profile memory is indexed offline. Current context is refreshed separately, and debug mode exposes the full planner → retrieval → verifier trace.
      </div>

      <div className="status-metrics">
        <span className={`status-pill ${status?.index_ready ? "ready" : "not-ready"}`}>
          {status?.index_ready ? "Index ready" : "Index not ready"}
        </span>
        <span>Long-term: {memoryCounts.long_term ?? 0}</span>
        <span>Current: {memoryCounts.current ?? 0}</span>
        <span>Archive: {memoryCounts.archive ?? 0}</span>
      </div>
    </div>
  );
}