import React, { useState } from 'react';
import './styles.css';

const API = 'http://127.0.0.1:8000';

export default function App() {
  const [source, setSource] = useState(null);
  const [target, setTarget] = useState(null);
  const [sensor, setSensor] = useState('UNKNOWN');
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(
    'Upload both source and reference images to begin.'
  );

  const ready = source instanceof File && target instanceof File;

  const handleSource = (e) => {
    const file = e.target.files?.[0] || null;

    setSource(file);
    setResult(null);

    if (file && target) {
      setStatus('Both images selected. Ready to run.');
    } else {
      setStatus('Upload both source and reference images to begin.');
    }
  };

  const handleTarget = (e) => {
    const file = e.target.files?.[0] || null;

    setTarget(file);
    setResult(null);

    if (file && source) {
      setStatus('Both images selected. Ready to run.');
    } else {
      setStatus('Upload both source and reference images to begin.');
    }
  };

  async function run(event) {
    event.preventDefault();

    if (!ready) {
      setStatus('Please upload BOTH images before running LUNALIGN.');
      return;
    }

    const formData = new FormData();

    formData.append('source', source);
    formData.append('target', target);
    formData.append('source_sensor', sensor);
    formData.append('target_sensor', sensor);
    formData.append('performance_mode', 'RESEARCH');

    setResult(null);
    setStatus('Processing...');

    try {
      const response = await fetch(`${API}/api/register`, {
        method: 'POST',
        body: formData,
      });

      const text = await response.text();

      console.log('STATUS:', response.status);
      console.log('RAW RESPONSE:', text);

      if (!response.ok) {
        throw new Error(text || `Server error ${response.status}`);
      }

      let data;

      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(
          `Server returned non-JSON response: ${text.slice(0, 300)}`
        );
      }

      setResult(data);

      setStatus(
        data.explanation ||
          data.status ||
          'Processing complete.'
      );
    } catch (error) {
      console.error(error);
      setResult(null);
      setStatus(`Processing error: ${error.message}`);
    }
  }

  const getMetric = (key) => {
    if (!result) return '--';

    return result[key] ?? result.metrics?.[key] ?? '--';
  };

  const getImageUrl = (path) => {
    if (!path) return null;

    if (path.startsWith('http')) {
      return path;
    }

    return `${API}${path.startsWith('/') ? '' : '/'}${path}`;
  };

  const coverageGrid =
    result?.coverage_grid ||
    result?.metrics?.coverage_grid ||
    null;

  const coverageCells = coverageGrid?.cells || [];

  const success =
    result?.status === 'SUCCESS' ||
    status?.toUpperCase().includes('HIGH CONFIDENCE') ||
    status?.toUpperCase().includes('SUCCESS');

  const inlierRatio = getMetric('inlier_ratio');
  const spatialCoverage = getMetric('spatial_coverage');
  const processingTime = getMetric('processing_time_s');
  const refinedRmse = getMetric('refined_rmse_px');

  return (
    <main className="app">

      {/* HEADER */}
      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            ◐
          </div>

          <div>
            <h1>LUNALIGN AI</h1>
            <p>
              Cross-sensor lunar registration workbench
            </p>
          </div>

        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          SYSTEM ONLINE
        </div>

      </header>


      {/* DASHBOARD */}
      <div className="dashboard">


        {/* INPUT PANEL */}
        <section className="panel input-panel">

          <div className="panel-heading">

            <div>
              <span className="eyebrow">
                INPUT DATA
              </span>

              <h2>
                Image Registration
              </h2>
            </div>

            <span className="step-number">
              01
            </span>

          </div>


          <form onSubmit={run}>

            <div className="upload-grid">


              {/* SOURCE IMAGE */}
              <label className="image-drop">

                <input
                  type="file"
                  accept="image/*,.tif,.tiff"
                  onChange={handleSource}
                />

                <div className="drop-icon">
                  {source ? '✓' : '↑'}
                </div>

                <span className="drop-title">
                  Source Image
                </span>

                <span className="drop-subtitle">
                  {source
                    ? source.name
                    : 'Upload lunar source image'}
                </span>

                <span className="drop-hint">
                  JPG / PNG / TIFF
                </span>

              </label>


              {/* REFERENCE IMAGE */}
              <label className="image-drop">

                <input
                  type="file"
                  accept="image/*,.tif,.tiff"
                  onChange={handleTarget}
                />

                <div className="drop-icon">
                  {target ? '✓' : '↑'}
                </div>

                <span className="drop-title">
                  Reference Image
                </span>

                <span className="drop-subtitle">
                  {target
                    ? target.name
                    : 'Upload reference image'}
                </span>

                <span className="drop-hint">
                  JPG / PNG / TIFF
                </span>

              </label>

            </div>


            {/* CONTROLS */}
            <div className="control-row">

              <label className="select-control">

                <span>
                  Sensor
                </span>

                <select
                  value={sensor}
                  onChange={(e) =>
                    setSensor(e.target.value)
                  }
                >
                  <option value="UNKNOWN">
                    UNKNOWN
                  </option>

                  <option value="OHRC">
                    OHRC
                  </option>

                  <option value="TMC">
                    TMC
                  </option>

                  <option value="IIRS">
                    IIRS
                  </option>

                  <option value="LRO_NAC">
                    LRO NAC
                  </option>

                  <option value="SELENE">
                    SELENE
                  </option>
                </select>

              </label>


              <button
                className="run-button"
                type="submit"
                disabled={!ready}
              >
                <span>
                  RUN LUNALIGN
                </span>

                <span className="arrow">
                  →
                </span>

              </button>

            </div>

          </form>


          {/* STATUS */}
          <div className="status-line">

            <span
              className={
                success
                  ? 'status-dot success'
                  : 'status-dot'
              }
            ></span>

            <span>
              {status}
            </span>

          </div>

        </section>



        {/* OVERVIEW PANEL */}
        <section className="panel overview-panel">

          <div className="panel-heading">

            <div>

              <span className="eyebrow">
                REGISTRATION
              </span>

              <h2>
                Run Overview
              </h2>

            </div>

            <span className="step-number">
              02
            </span>

          </div>


          {!result ? (

            <div className="empty-state">

              <div className="empty-orbit">
                ◎
              </div>

              <h3>
                Awaiting registration
              </h3>

              <p>
                Upload two lunar images and run
                the registration pipeline.
              </p>

            </div>

          ) : (

            <div className="overview-content">


              {/* RESULT STATUS */}
              <div
                className={`result-banner ${
                  success
                    ? 'success'
                    : 'warning'
                }`}
              >

                <div>

                  <span className="banner-label">
                    REGISTRATION STATUS
                  </span>

                  <strong>
                    {success
                      ? 'SUCCESS'
                      : 'REVIEW RESULT'}
                  </strong>

                </div>

                <span className="confidence">
                  {success
                    ? 'HIGH CONFIDENCE'
                    : 'CHECK QUALITY'}
                </span>

              </div>



              {/* METRICS */}
              <div className="metric-grid">


                <div className="metric-card">

                  <span>
                    Matches
                  </span>

                  <strong>
                    {getMetric(
                      'candidate_matches'
                    )}
                  </strong>

                  <small>
                    candidate points
                  </small>

                </div>


                <div className="metric-card">

                  <span>
                    Inliers
                  </span>

                  <strong>
                    {getMetric('inliers')}
                  </strong>

                  <small>
                    verified points
                  </small>

                </div>


                <div className="metric-card">

                  <span>
                    Inlier Ratio
                  </span>

                  <strong>

                    {typeof inlierRatio ===
                    'number'
                      ? `${(
                          inlierRatio * 100
                        ).toFixed(0)}%`
                      : inlierRatio}

                  </strong>

                  <small>
                    geometric consistency
                  </small>

                </div>


                <div className="metric-card">

                  <span>
                    Coverage
                  </span>

                  <strong>

                    {typeof spatialCoverage ===
                    'number'
                      ? `${(
                          spatialCoverage * 100
                        ).toFixed(0)}%`
                      : spatialCoverage}

                  </strong>

                  <small>
                    image area
                  </small>

                </div>

              </div>



              {/* TECHNICAL DETAILS */}
              <div className="technical-row">


                <div>

                  <span>
                    TRANSFORM
                  </span>

                  <strong>
                    {getMetric(
                      'transform_model'
                    )}
                  </strong>

                </div>


                <div>

                  <span>
                    PROCESSING
                  </span>

                  <strong>

                    {processingTime !== '--'
                      ? `${Number(
                          processingTime
                        ).toFixed(2)} s`
                      : '--'}

                  </strong>

                </div>


                <div>

                  <span>
                    RMSE
                  </span>

                  <strong>

                    {refinedRmse !== '--'
                      ? `${Number(
                          refinedRmse
                        ).toFixed(4)} px`
                      : '--'}

                  </strong>

                </div>

              </div>

            </div>

          )}

        </section>



        {/* OUTPUT RESULTS */}
        {result && (

          <section className="panel results-panel">

            <div className="panel-heading">

              <div>

                <span className="eyebrow">
                  OUTPUT
                </span>

                <h2>
                  Registration Results
                </h2>

              </div>

              <span className="step-number">
                03
              </span>

            </div>


            <div className="result-images">


              <ResultImage
                title="Registered Image"
                src={getImageUrl(
                  result.registered_image ||
                    result.urls?.registered_image
                )}
              />


              <ResultImage
                title="Alpha Overlay"
                src={getImageUrl(
                  result.overlay ||
                    result.urls?.overlay
                )}
              />


              <ResultImage
                title="Checkerboard"
                src={getImageUrl(
                  result.checkerboard ||
                    result.urls?.checkerboard
                )}
              />


              <ResultImage
                title="Difference"
                src={getImageUrl(
                  result.difference ||
                    result.urls?.difference
                )}
              />

            </div>

          </section>

        )}



        {/* COVERAGE ANALYSIS */}
        {result &&
          coverageCells.length > 0 && (

            <section className="panel coverage-panel">

              <div className="panel-heading">

                <div>

                  <span className="eyebrow">
                    SPATIAL ANALYSIS
                  </span>

                  <h2>
                    Match Coverage
                  </h2>

                </div>

              </div>


              <div className="coverage-layout">


                {/* GRID */}
                <div className="coverage-grid">

                  {coverageCells.flatMap(
                    (row, rowIndex) =>
                      row.map(
                        (value, colIndex) => (

                          <div
                            key={`${rowIndex}-${colIndex}`}
                            className={`coverage-cell ${
                              value > 0
                                ? 'active'
                                : ''
                            }`}
                            title={`Matches: ${value}`}
                          >
                            {value > 0
                              ? value
                              : ''}
                          </div>

                        )
                      )
                  )}

                </div>



                {/* COVERAGE INFO */}
                <div className="coverage-info">


                  <div>

                    <span>
                      SPATIAL COVERAGE
                    </span>

                    <strong>

                      {typeof spatialCoverage ===
                      'number'
                        ? `${(
                            spatialCoverage * 100
                          ).toFixed(1)}%`
                        : '--'}

                    </strong>

                  </div>


                  <div>

                    <span>
                      ENTROPY
                    </span>

                    <strong>
                      {coverageGrid?.entropy ??
                        '--'}
                    </strong>

                  </div>


                  <div>

                    <span>
                      CONVEX HULL
                    </span>

                    <strong>
                      {coverageGrid?.convex_hull_coverage ??
                        '--'}
                    </strong>

                  </div>

                </div>

              </div>

            </section>

          )}

      </div>


      {/* FOOTER */}
      <footer>
        LUNALIGN AI • Lunar image correspondence
        and registration
      </footer>

    </main>
  );
}



function ResultImage({ title, src }) {

  return (

    <div className="result-image-card">

      <div className="result-image-header">

        <span>
          {title}
        </span>

        {src && (
          <span className="available">
            AVAILABLE
          </span>
        )}

      </div>


      <div className="image-container">

        {src ? (

          <img
            src={src}
            alt={title}
          />

        ) : (

          <div className="image-placeholder">
            No image returned
          </div>

        )}

      </div>

    </div>

  );
}