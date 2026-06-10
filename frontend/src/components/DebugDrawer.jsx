import React from "react";

function formatMs(value) {
  if (typeof value !== "number") return "-";
  return `${value.toFixed(1)} ms`;
}

export default function DebugDrawer({ debug }) {
  const planner = debug?.planner || {};
  const verifier = debug?.verifier || {};
  const policy = debug?.policy || {};
  const retrievedChunks = debug?.retrieved_chunks || [];
  const timings = debug?.timings_ms || {};

  return (
    <details className="debug-drawer">
      <summary>Why this answer</summary>

      <div className="debug-grid">
        <div className="debug-card">
          <div className="section-title">Planner</div>
          <div className="debug-list">
            <div><strong>Question type:</strong> {planner.question_type || "-"}</div>
            <div><strong>Temporal mode:</strong> {planner.temporal_mode || "-"}</div>
            <div><strong>Target layers:</strong> {(planner.target_layers || []).join(", ") || "-"}</div>
            <div><strong>Target tags:</strong> {(planner.target_tags || []).join(", ") || "-"}</div>
            <div><strong>Needs synthesis:</strong> {String(planner.needs_multi_source_synthesis ?? false)}</div>
            <div><strong>Should cite:</strong> {String(planner.should_cite ?? false)}</div>
          </div>
        </div>

        <div className="debug-card">
          <div className="section-title">Verifier</div>
          <div className="debug-list">
            <div><strong>Action:</strong> {verifier.action || "-"}</div>
            <div><strong>Confidence:</strong> {typeof verifier.confidence === "number" ? verifier.confidence.toFixed(2) : "-"}</div>
            <div><strong>Supported claims:</strong> {verifier.supported_claims?.length ?? 0}</div>
            <div><strong>Partial claims:</strong> {verifier.partially_supported_claims?.length ?? 0}</div>
            <div><strong>Unsupported claims:</strong> {verifier.unsupported_claims?.length ?? 0}</div>
            <div><strong>Policy result:</strong> {policy.action || "-"}</div>
          </div>
        </div>

        <div className="debug-card full-width">
          <div className="section-title">Timings</div>
          <div className="timing-row">
            <span>Planner + embed</span>
            <strong>{formatMs(timings.plan_plus_embed)}</strong>
          </div>
          <div className="timing-row">
            <span>Retrieve + evidence</span>
            <strong>{formatMs(timings.retrieve_plus_evidence)}</strong>
          </div>
          <div className="timing-row">
            <span>Respond</span>
            <strong>{formatMs(timings.respond)}</strong>
          </div>
          <div className="timing-row">
            <span>Verify</span>
            <strong>{formatMs(timings.verify)}</strong>
          </div>
          <div className="timing-row">
            <span>Total</span>
            <strong>{formatMs(timings.total)}</strong>
          </div>
        </div>

        <div className="debug-card full-width">
          <div className="section-title">Retrieved evidence</div>
          <div className="retrieved-list">
            {retrievedChunks.map((chunk) => (
              <div key={chunk.chunk_id} className="retrieved-card">
                <div className="retrieved-top">
                  <strong>{chunk.title}</strong>
                  <span>{chunk.layer}</span>
                </div>
                <div className="retrieved-meta">
                  <span>{chunk.source}</span>
                  <span>score {Number(chunk.score).toFixed(3)}</span>
                </div>
                <p>{chunk.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </details>
  );
}