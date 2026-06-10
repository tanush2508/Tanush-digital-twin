import React from "react";

function layerLabel(layer) {
  if (layer === "long_term") return "Long-term";
  if (layer === "current") return "Current";
  if (layer === "archive") return "Archive";
  return layer;
}

export default function SourcePanel({ sources }) {
  return (
    <div className="source-panel">
      <div className="section-title">Sources</div>
      <div className="source-list">
        {sources.map((source) => (
          <div key={source.chunk_id} className="source-card">
            <div className="source-card-top">
              <strong>{source.title}</strong>
              <span className={`layer-pill layer-${source.layer}`}>
                {layerLabel(source.layer)}
              </span>
            </div>
            <div className="source-meta">
              <span>{source.source}</span>
              <span>score {source.score.toFixed(3)}</span>
            </div>
            <p>{source.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  );
}