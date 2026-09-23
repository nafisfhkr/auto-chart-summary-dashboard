const root = document.querySelector('#dashboard');

function escapeHtml(value) { return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function formatPeriod(period, frequency) { const d = new Date(`${period}T00:00:00`); return frequency === 'monthly' ? d.toLocaleDateString('id-ID',{month:'short',year:'numeric'}) : d.getFullYear(); }
function chartSvg(observations, chartType, frequency) {
  if (!observations.length) return '<p class="meta">Data belum tersedia.</p>';
  const values = observations.map(o => Number(o.value)), rawMin = Math.min(...values), rawMax = Math.max(...values);
  const rawRange = rawMax - rawMin, padding = rawRange ? rawRange * .12 : Math.max(Math.abs(rawMax) * .12, 1);
  const min = rawMin - padding, max = rawMax + padding, range = max - min || 1;
  const left = 58, right = 624, top = 24, bottom = 298, width = right - left, height = bottom - top;
  const y = value => bottom - ((value - min) / range * height);
  const x = i => left + (i / Math.max(values.length - 1, 1) * width);
  const points = values.map((v,i) => `${x(i)},${y(v)}`).join(' ');
  const grid = [0, .5, 1].map(step => { const value = max - (range * step); return `<line class="grid-line" x1="${left}" y1="${y(value)}" x2="${right}" y2="${y(value)}"/><text class="axis-label" x="${left - 10}" y="${y(value) + 4}" text-anchor="end">${value.toFixed(1)}</text>`; }).join('');
  const frame = `${grid}<line class="axis" x1="${left}" y1="${bottom}" x2="${right}" y2="${bottom}"/>`;
  const labels = `<div class="labels">${observations.map((item, index) => `<span style="left:${(index / Math.max(observations.length - 1, 1)) * 100}%">${formatPeriod(item.period, frequency)}</span>`).join('')}</div>`;
  if (chartType === 'bar') {
    const slot = width / Math.max(values.length, 1), barWidth = Math.min(42, slot * .62);
    const bars = values.map((value, index) => { const center = left + slot * (index + .5), top = y(value); return `<rect class="bar" x="${center - barWidth / 2}" y="${top}" width="${barWidth}" height="${Math.max(bottom - top, 1)}" rx="3"/>`; }).join('');
    return `<svg class="chart" viewBox="0 0 680 340" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Perbandingan data">${frame}${bars}</svg>${labels}`;
  }
  const area = chartType === 'area' ? `<polygon class="area" points="${left},${bottom} ${points} ${right},${bottom}"/>` : '';
  return `<svg class="chart" viewBox="0 0 680 340" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Tren data">${frame}${area}<polyline class="line" points="${points}"/>${values.map((v,i)=>`<circle class="dot" cx="${x(i)}" cy="${y(v)}" r="4"/>`).join('')}</svg>${labels}`;
}
function renderLineChart(observations, frequency) { return chartSvg(observations, 'line', frequency); }
function renderBarChart(observations, frequency) { return chartSvg(observations, 'bar', frequency); }
function renderAreaChart(observations, frequency) { return chartSvg(observations, 'area', frequency); }
function renderChartVisualization(chart) {
  const renderers = { line: renderLineChart, bar: renderBarChart, area: renderAreaChart };
  return (renderers[chart.chart_type] || renderers.line)(chart.observations, chart.frequency);
}
function renderChart(chart) {
  const summary = chart.summary;
  const summaryHtml = summary ? `<p>${escapeHtml(summary.summary_text)}</p><span class="badge">✓ Rule-based validated</span><span class="timestamp">Dibuat ${escapeHtml(summary.generated_at || '-')} · ${escapeHtml(summary.provider || '-')} · ${escapeHtml(summary.model_name || '-')}</span>` : '<p>Ringkasan belum tersedia.</p>';
  return `<article class="card"><h2>${escapeHtml(chart.indicator_name)}</h2><p class="meta">${escapeHtml(chart.region)} · ${escapeHtml(chart.unit || '')} · ${escapeHtml(chart.frequency)}</p>${renderChartVisualization(chart)}<section class="summary"><h3>Ringkasan AI</h3>${summaryHtml}</section></article>`;
}
fetch('/api/dashboard/dashboard_jatim_demo').then(response => { if (!response.ok) throw new Error(); return response.json(); }).then(data => { root.innerHTML = data.charts.map(renderChart).join('') || '<p class="state">Data belum tersedia.</p>'; }).catch(() => { root.innerHTML = '<p class="state error">Gagal memuat dashboard.</p>'; });
