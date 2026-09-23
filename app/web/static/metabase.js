const root = document.querySelector('#metabase-dashboard');
function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function renderChart(chart) {
  const summary = chart.latest_valid_summary;
  const summaryHtml = summary ? `<p>${escapeHtml(summary.summary_text)}</p><span class="badge">✓ Rule-based validated</span><span class="timestamp">${escapeHtml(summary.provider || '-')} · ${escapeHtml(summary.model_name || '-')}</span>` : '<p>Ringkasan belum tersedia.</p>';
  return `<article class="card"><h2>${escapeHtml(chart.title)}</h2><p class="meta">Question ${escapeHtml(chart.question_id)} · ${escapeHtml(chart.insight_type)}</p><iframe class="metabase-frame" src="${escapeHtml(chart.embed_url)}" title="${escapeHtml(chart.title)}" loading="lazy"></iframe><section class="summary"><h3>Ringkasan AI</h3>${summaryHtml}</section></article>`;
}
fetch('/api/metabase/dashboard/metabase_pilot').then(response => { if (!response.ok) throw new Error(); return response.json(); }).then(data => { root.innerHTML = data.charts.map(renderChart).join('') || '<p class="state">Data belum tersedia.</p>'; }).catch(() => { root.innerHTML = '<p class="state error">Konfigurasi Metabase belum tersedia.</p>'; });
