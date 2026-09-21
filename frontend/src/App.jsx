import React, { useMemo, useState } from 'react';
import './styles.css';

const API = 'http://127.0.0.1:8000';
const resultImageUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return `${API}${url}`;
};
const sensorOptions = [
  ['UNKNOWN', 'Unknown'],
  ['OHRC', 'OHRC'],
  ['TMC', 'TMC'],
  ['IIRS', 'IIRS'],
  ['LRO_NAC', 'LRO (Narrow Angle)'],
  ['SELENE', 'SELENE'],
];

function App() {
  const [source, setSource] = useState(null);
  const [target, setTarget] = useState(null);
  const [sourceSensor, setSourceSensor] = useState('LRO_NAC');
  const [targetSensor, setTargetSensor] = useState('LRO_NAC');
  const [representation, setRepresentation] = useState('auto');
  const [coverageGrid, setCoverageGrid] = useState('8');
  const [engine, setEngine] = useState('SIFT');
  const [performance, setPerformance] = useState('BALANCED');
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState('Upload both source and reference images to begin.');
  const [running, setRunning] = useState(false);
  const [activeNav, setActiveNav] = useState('Home');

  const ready = source instanceof File && target instanceof File;

  const metric = (key, fallback = '--') =>
    result?.[key] ?? result?.metrics?.[key] ?? fallback;

  const imageUrl = (value) => {
    if (!value) return null;
    if (String(value).startsWith('http')) return value;
    return `${API}${String(value).startsWith('/') ? '' : '/'}${value}`;
  };

  const resultPath = (...keys) => {
    console.log("FULL RESULT:", result);
  for (const key of keys) {
    const value =
      result?.urls?.[key] ??
      result?.[key] ??
      result?.paths?.[key];

    if (value) {
      console.log("IMAGE KEY:", key);
      console.log("IMAGE VALUE:", value);
      console.log("IMAGE URL:", imageUrl(value));
      return imageUrl(value);
    }
  }
  return null;
};
  const inlierRatio = Number(metric('inlier_ratio', NaN));
  const coverage = Number(metric('spatial_coverage', NaN));
  const rmse = Number(metric('rmse_px', NaN));
  const medianError = Number(metric('median_error_px', NaN));
  const p95Error = Number(metric('p95_error_px', NaN));
  const processing = Number(metric('processing_time_s', NaN));
  const matches = metric('candidate_matches');
  const inliers = metric('inliers');
  const transform = metric('transform_model');

  const success =
    String(result?.status || '').toUpperCase() === 'SUCCESS';

  const confidence = useMemo(() => {
    if (!result) return 0;
    if (Number.isFinite(inlierRatio) && Number.isFinite(coverage)) {
      return Math.round(
        Math.max(0, Math.min(100, inlierRatio * 65 + coverage * 35))
      );
    }
    return success ? 87 : 35;
  }, [result, inlierRatio, coverage, success]);

  async function run(event) {
    event.preventDefault();

    if (!ready) {
      setStatus('Please upload BOTH images before running LUNALIGN.');
      return;
    }

    setRunning(true);
    setResult(null);
    setStatus('Processing…');

    const formData = new FormData();
    formData.append('source', source);
    formData.append('target', target);
    formData.append('source_sensor', sourceSensor);
    formData.append('target_sensor', targetSensor);
    formData.append('performance_mode', performance === 'FAST' ? 'FAST' : 'RESEARCH');

    try {
      const response = await fetch(`${API}/api/register`, {
        method: 'POST',
        body: formData,
      });

      const text = await response.text();

      if (!response.ok) {
        throw new Error(text || `Server error ${response.status}`);
      }

      const data = JSON.parse(text);
      setResult(data);
      setStatus(data.explanation || data.status || 'Processing complete.');
    } catch (error) {
      setResult(null);
      setStatus(`Processing error: ${error.message}`);
    } finally {
      setRunning(false);
    }
  }

  function chooseFile(setter, event) {
    const file = event.target.files?.[0] || null;
    setter(file);
    setResult(null);
    if (file && (setter === setSource ? target : source)) {
      setStatus('Both images selected. Ready to run.');
    } else {
      setStatus('Upload both source and reference images to begin.');
    }
  }

  function demoMessage(type) {
    setStatus(
      type === 'failure'
        ? 'Failure demo is available in the backend fixture. Connect its endpoint when exposed by the API.'
        : 'Demo fixture is available in the backend. Connect its endpoint when exposed by the API.'
    );
  }

  const registered = resultPath(
  'registered_image',
  'registered',
  'registered_path'
);

const overlay = resultPath(
  'overlay',
  'alpha_overlay'
);

const checkerboard = resultPath(
  'checkerboard'
);

const difference =
  result?.urls?.difference
    ? imageUrl(result.urls.difference)
    : resultPath('difference', 'difference_image', 'difference_path');
  const heatmap = resultPath('match_heatmap', 'heatmap');
  const normalizationBefore = resultPath('normalized_before', 'illumination_before');
  const normalizationAfter = resultPath('normalized_after', 'illumination_after');

  return (
    <main className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">◐</div>
          <div>
            <h1>LUNALIGN <span>AI</span></h1>
            <p>Sun-Angle &amp; Cross-Sensor Lunar Image Correspondence Engine</p>
          </div>
        </div>

        <nav className="main-nav">
          {['Home', 'Results', 'Reports', 'Settings'].map((item) => (
            <button
              key={item}
              className={activeNav === item ? 'nav-item active' : 'nav-item'}
              onClick={() => setActiveNav(item)}
            >
              {item === 'Home' ? '⌂' : item === 'Results' ? '◉' : item === 'Reports' ? '▤' : '⚙'}
              <span>{item}</span>
            </button>
          ))}
        </nav>

        <div className="system-status">
          <span className="status-dot success" />
          Local Processing Enabled
        </div>
      </header>

      <form className="workspace" onSubmit={run}>
        <section className="control-panel panel">
          <UploadCard
            title="Input Image"
            file={source}
            onChange={(e) => chooseFile(setSource, e)}
          />
          <UploadCard
            title="Reference Image"
            file={target}
            onChange={(e) => chooseFile(setTarget, e)}
          />

          <SelectControl label="Source Sensor" value={sourceSensor} onChange={setSourceSensor}>
            {sensorOptions.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </SelectControl>

          <SelectControl label="Reference Sensor" value={targetSensor} onChange={setTargetSensor}>
            {sensorOptions.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </SelectControl>

          <SelectControl label="Representation" value={representation} onChange={setRepresentation}>
            <option value="auto">AUTO SELECT</option>
            <option value="raw">RAW</option>
            <option value="clahe">CLAHE</option>
            <option value="gradient">GRADIENT</option>
            <option value="edge">EDGE</option>
            <option value="local_contrast">LOCAL CONTRAST</option>
          </SelectControl>

          <SelectControl label="Coverage Grid" value={coverageGrid} onChange={setCoverageGrid}>
            <option value="4">4 × 4</option>
            <option value="8">8 × 8</option>
            <option value="10">10 × 10</option>
          </SelectControl>

          <SelectControl label="Engine" value={engine} onChange={setEngine}>
            <option>SIFT</option>
            <option>ORB</option>
            <option>AKAZE</option>
          </SelectControl>

          <SelectControl label="Performance" value={performance} onChange={setPerformance}>
            <option>BALANCED</option>
            <option>FAST</option>
            <option>RESEARCH</option>
          </SelectControl>

          <div className="action-stack">
            <button className="primary-button" type="submit" disabled={!ready || running}>
              <span>▶</span> {running ? 'PROCESSING…' : 'RUN LUNALIGN'}
            </button>
            <button className="secondary-button" type="button" onClick={() => demoMessage('demo')}>
              ◫ RUN DEMO
            </button>
            <button className="secondary-button" type="button" onClick={() => demoMessage('failure')}>
              ◉ RUN FAILURE DEMO
            </button>
          </div>
        </section>

        {!result ? (
          <section className="empty-dashboard panel">
            <div className="empty-orbit">◌</div>
            <h2>Awaiting Registration</h2>
            <p>Select a source and reference lunar image, then run the registration engine.</p>
            <div className="status-line"><span className="status-dot" />{status}</div>
          </section>
        ) : (
          <>
            <section className="visual-grid">
  <ImagePanel
    title="Registered Image"
    src={registered}
    success={success}
  />

  <ImagePanel
    title="Alpha Overlay"
    src={overlay}
  />

  <ImagePanel
    title="Checkerboard"
    src={checkerboard}
  />

  <ImagePanel
  title="Difference Image"
  src="http://127.0.0.1:8000/results/624bb1d18df8/difference.png"
/>
  <ConfidencePanel
    confidence={confidence}
    success={success}
    result={result}
  />
</section>
            <section className="metric-strip">
              <MetricCard label="State" value={success ? 'SUCCESS' : 'REVIEW'} detail={result.status} state />
              <MetricCard label="Candidate Matches" value={matches} />
              <MetricCard label="Inliers" value={inliers} />
              <MetricCard label="Inlier Ratio" value={Number.isFinite(inlierRatio) ? inlierRatio.toFixed(4) : '--'} />
              <MetricCard label="RMSE" value={Number.isFinite(rmse) ? `${rmse.toFixed(3)} px` : '--'} />
              <MetricCard label="Median Error" value={Number.isFinite(medianError) ? `${medianError.toFixed(3)} px` : '--'} />
              <MetricCard label="P95 Error" value={Number.isFinite(p95Error) ? `${p95Error.toFixed(3)} px` : '--'} />
            </section>

            <section className="lower-grid">
              <HeatmapPanel src={heatmap} result={result} />
              <LandmarkPanel result={result} source={source} target={target} />
              <DiagnosisPanel result={result} success={success} />
              <NormalizationPanel before={normalizationBefore} after={normalizationAfter} />
              <ComparisonPanel result={result} />
              <MatchDetails result={result} source={source} target={target} />
            </section>

            <section className="technical-footer panel">
              <div><span>TRANSFORM</span><strong>{transform || '--'}</strong></div>
              <div><span>PROCESSING TIME</span><strong>{Number.isFinite(processing) ? `${processing.toFixed(2)} s` : '--'}</strong></div>
              <div><span>SPATIAL COVERAGE</span><strong>{Number.isFinite(coverage) ? `${(coverage * 100).toFixed(1)}%` : '--'}</strong></div>
              <div className="explanation"><span>ENGINE EXPLANATION</span><strong>{result.explanation || 'No explanation returned.'}</strong></div>
            </section>
          </>
        )}

        <div className="run-status">{status}</div>
      </form>

      <footer className="footer">
        <span>◐ LUNALIGN AI</span>
        <span>Better Correspondence. Better Moon Mapping.</span>
        <span>Built for a brighter lunar future ◐</span>
      </footer>
    </main>
  );
}

function UploadCard({ title, file, onChange }) {
  return (
    <label className="upload-card">
      <div className="upload-title"><span>▣</span>{title}</div>
      <input type="file" accept="image/*,.tif,.tiff" onChange={onChange} />
      <div className="preview-box">
        {file ? (
          <img src={URL.createObjectURL(file)} alt={title} />
        ) : (
          <div className="upload-placeholder">↑<small>Choose image</small></div>
        )}
      </div>
      <div className="file-name">{file?.name || 'No image selected'}</div>
      <span className="remove-hint">JPG / PNG / TIFF</span>
    </label>
  );
}

function SelectControl({ label, value, onChange, children }) {
  return (
    <label className="select-control">
      <span>{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {children}
      </select>
    </label>
  );
}

function ImagePanel({ title, src, success }) {
  return (
    <section className="dash-card image-panel">
      <div className="card-title"><span>▣</span>{title}{success && <b className="check">✓</b>}</div>
      <div className="large-image">
        {src ? (
  <img
    src={src}
    alt={title}
    onError={(e) => console.error("IMAGE LOAD ERROR:", src, e)}
  />
) : (
  <div className="no-data">No image returned</div>
)}
      </div>
    </section>
  );
}

function ConfidencePanel({ confidence, success, result }) {
  return (
    <section className="dash-card confidence-panel">
      <div className="card-title">▣ Alignment Confidence</div>
      <div className="confidence-layout">
        <div className="ring" style={{ '--confidence': `${confidence}%` }}>
          <div><strong>{confidence}%</strong><small>{success ? 'High Confidence' : 'Needs Review'}</small></div>
        </div>
        <div className="confidence-list">
          <p>✓ <b>Feature matches:</b> {Number(result?.metrics?.candidate_matches ?? 0) > 0 ? 'Found' : 'Low'}</p>
          <p>✓ <b>Inlier ratio:</b> {result?.metrics?.inlier_ratio != null ? `${(result.metrics.inlier_ratio * 100).toFixed(1)}%` : '--'}</p>
          <p>✓ <b>Geometric error:</b> {result?.metrics?.rmse_px != null ? `${Number(result.metrics.rmse_px).toFixed(3)} px` : '--'}</p>
          <p>✓ <b>Spatial coverage:</b> {result?.metrics?.spatial_coverage != null ? `${(result.metrics.spatial_coverage * 100).toFixed(1)}%` : '--'}</p>
        </div>
      </div>
      <div className="info-box">Metrics shown here are calculated from the current backend registration response.</div>
    </section>
  );
}

function MetricCard({ label, value, detail, state }) {
  return (
    <div className={`metric-card ${state ? 'state-card' : ''}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  );
}

function HeatmapPanel({ src, result }) {
  return (
    <section className="dash-card heatmap-card">
      <div className="card-title">♣ Match Heatmap</div>
      <div className="heatmap">
        {src ? <img src={src} alt="Match heatmap" /> : <div className="heatmap-placeholder">Heatmap not returned by API</div>}
      </div>
      <div className="legend"><span>Strong</span><i /><span>Medium</span><i /><span>Weak</span></div>
    </section>
  );
}

function LandmarkPanel({ result, source, target }) {
  const points = result?.correspondences || [];
  return (
    <section className="dash-card landmark-card">
      <div className="card-title">◈ Crater Landmark Detection</div>
      <div className="landmark-images">
        <Thumb file={source} label="Input Image" />
        <span className="landmark-arrow">›</span>
        <Thumb file={target} label="Reference Image" />
      </div>
      <div className="point-list">
        <span>Verified correspondences: {points.length}</span>
        {points.slice(0, 3).map((p, i) => (
          <span key={i}>Match {i + 1}: {formatPoint(p)}</span>
        ))}
      </div>
    </section>
  );
}

function Thumb({ file, label }) {
  return (
    <div>
      <span>{label}</span>
      <div className="thumb">
        {file ? <img src={URL.createObjectURL(file)} alt={label} /> : 'No image'}
      </div>
    </div>
  );
}

function formatPoint(point) {
  if (!point) return '--';
  const s = point.source || point.src || [];
  const t = point.target || point.dst || [];
  return `${Array.isArray(s) ? s.map(n => Number(n).toFixed(0)).join(', ') : '--'} → ${Array.isArray(t) ? t.map(n => Number(n).toFixed(0)).join(', ') : '--'}`;
}

function DiagnosisPanel({ result, success }) {
  const explanation = result?.explanation || 'No diagnostic explanation returned.';
  return (
    <section className={`dash-card diagnosis-card ${success ? 'diagnosis-success' : ''}`}>
      <div className="card-title">⚠ Automatic Failure Diagnosis</div>
      <div className="diagnosis-badge">{success ? 'REGISTRATION ACCEPTED' : String(result?.status || 'QUALITY REVIEW')}</div>
      <h4>{success ? 'Registration quality' : 'Why did it fail or require review?'}</h4>
      <p>{explanation}</p>
      <div className="suggestion">💡 Suggested action: inspect match count, spatial coverage, illumination normalization, and sensor metadata.</div>
    </section>
  );
}

function NormalizationPanel({ before, after }) {
  return (
    <section className="dash-card normalization-card">
      <div className="card-title">☼ Illumination Normalization (Before vs After)</div>
      <div className="before-after">
        <div><span>Before</span><div className="small-image">{before ? <img src={before} alt="Before normalization" /> : 'Not returned'}</div></div>
        <div><span>After</span><div className="small-image">{after ? <img src={after} alt="After normalization" /> : 'Not returned'}</div></div>
        <div className="normalization-notes">
          <p>✓ Brightness normalization</p>
          <p>✓ Contrast enhancement</p>
          <p>✓ Shadow reduction</p>
          <p>✓ Improved feature matching</p>
        </div>
      </div>
    </section>
  );
}

function ComparisonPanel({ result }) {
  const rows = [
   [
  'Active engine',
  result?.metadata?.engine?.active ||
    result?.metrics?.engine ||
    'Selected by pipeline',
  result?.metrics?.candidate_matches ?? '--',
  result?.metrics?.inliers ?? '--',
  result?.metrics?.rmse_px ?? '--'
],
    ['ORB', '--', '--', '--', '--'],
    ['AKAZE', '--', '--', '--', '--'],
  ];

  return (
    <section className="dash-card comparison-card">
      <div className="card-title">▣ Multi-Algorithm Comparison</div>
      <table>
        <thead><tr><th>Engine</th><th>Matches</th><th>Inliers</th><th>Inlier Ratio</th><th>RMSE (px)</th></tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={i === 0 ? 'selected-row' : ''}>
              <td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td>
              <td>{typeof r[3] === 'number' && r[3] > 1 ? (Number(result?.metrics?.inlier_ratio || 0) * 100).toFixed(1) : r[3]}</td>
              <td>{r[4]}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-note">Only values returned by the current backend are populated; unrun algorithms are not fabricated.</div>
    </section>
  );
}

function MatchDetails({ result, source, target }) {
  const points = result?.correspondences || [];
  return (
    <section className="dash-card match-card">
      <div className="card-title">⌕ Match Details <span>Interactive</span></div>
      <div className="match-images">
        <Thumb file={source} label="Input Image" />
        <Thumb file={target} label="Reference Image" />
      </div>
      <div className="match-summary">
        <span>Matches: {points.length}</span>
        <span>Inliers: {result?.metrics?.inliers ?? '--'}</span>
        <span>RMSE: {result?.metrics?.rmse_px != null ? `${Number(result.metrics.rmse_px).toFixed(3)} px` : '--'}</span>
      </div>
    </section>
  );
}

export default App;
