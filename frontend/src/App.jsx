import React, { useState } from 'react';
import './styles.css';

const API = '';

// This app is intentionally guarded at both UI and submit levels. No file = no request.

export default function App() {
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState('Upload both source and reference images to begin.');
  const [source, setSource] = useState(null);
  const [target, setTarget] = useState(null);
  const [sensor, setSensor] = useState('UNKNOWN');

  const ready = Boolean(source && target && source instanceof File && target instanceof File);

  // Never permit submission unless both file inputs contain actual File objects.
  const canRun = ready;

  const clearResult = () => setResult(null);

  const handleSource = (event) => {
    const file = event.target.files?.[0] || null;
    setSource(file);
    clearResult();
    setStatus(file && target ? 'Both images selected. Ready to run.' : 'Upload both source and reference images to begin.');
  };

  const handleTarget = (event) => {
    const file = event.target.files?.[0] || null;
    setTarget(file);
    clearResult();
    setStatus(file && source ? 'Both images selected. Ready to run.' : 'Upload both source and reference images to begin.');
  };

  async function run(event) {
    event.preventDefault();
    event.stopPropagation();

    // Hard UI guard: no request is ever sent unless BOTH files exist.
    if (!(source instanceof File) || !(target instanceof File)) {
      setResult(null);
      setStatus('Please upload BOTH source and reference images before running LunaAlign.');
      return;
    }

    const fd = new FormData();
    fd.append('source', source, source.name);
    fd.append('target', target, target.name);
    fd.append('source_sensor', sensor);
    fd.append('target_sensor', sensor);
    fd.append('performance_mode', 'RESEARCH');

    setResult(null);
    setStatus('Processing…');

    try {
      const response = await fetch(`${API}/api/register`, { method: 'POST', body: fd });
      let data = {};
      try { data = await response.json(); } catch (_) { data = { detail: 'Invalid server response' }; }
      if (!response.ok) throw new Error(data.detail || 'Processing failed');
      setResult(data);
      setStatus(data.explanation || data.status || 'Processing complete.');
    } catch (error) {
      setResult(null);
      setStatus(`Processing error: ${error.message}`);
    }
  }

  const disabled = !canRun;

  return (
    <main>
      <h1>LUNALIGN AI</h1>
      <p>Cross-sensor lunar registration workbench</p>
      <form onSubmit={run} noValidate>
        <section>
          <label>
            Source image
            <input type="file" accept="image/*,.tif,.tiff" onChange={handleSource} />
          </label>
          <label>
            Reference image
            <input type="file" accept="image/*,.tif,.tiff" onChange={handleTarget} />
          </label>
          <select value={sensor} onChange={e => setSensor(e.target.value)}>
            <option>UNKNOWN</option><option>OHRC</option><option>TMC</option><option>IIRS</option><option>LRO_NAC</option><option>SELENE</option>
          </select>
          <button type="submit" disabled={disabled} aria-disabled={disabled}>
            RUN LUNALIGN
          </button>
        </section>
      </form>
      <p>{status}</p>
      {result && (
        <section>
          <h2>{result.status}</h2>
          <pre>{JSON.stringify(result.metrics, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}
