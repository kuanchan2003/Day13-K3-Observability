from __future__ import annotations


def render_dashboard() -> str:
    """Return the dependency-free runtime dashboard used for CP2 evidence."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Day 13 AI Observability</title>
  <style>
    :root { color-scheme: dark; --bg:#07111f; --card:#101d2e; --line:#26384e; --text:#f3f7fb; --muted:#93a4b8; --cyan:#36d1dc; --green:#48d597; --amber:#ffbe55; --red:#ff667a; }
    * { box-sizing:border-box; }
    body { margin:0; min-width:960px; background:radial-gradient(circle at 10% 0,#123052 0,transparent 30%),var(--bg); color:var(--text); font:14px/1.45 Inter,Segoe UI,sans-serif; }
    main { max-width:1400px; margin:auto; padding:28px 34px 40px; }
    header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:22px; }
    h1 { font-size:27px; margin:0 0 5px; letter-spacing:-.4px; }
    .subtitle,.meta,.hint { color:var(--muted); }
    .controls { display:flex; gap:10px; align-items:center; }
    .pill { border:1px solid var(--line); background:#0c1928; border-radius:9px; padding:8px 12px; }
    .live::before { content:""; display:inline-block; width:8px; height:8px; margin-right:7px; border-radius:50%; background:var(--green); box-shadow:0 0 10px var(--green); }
    .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
    .card { min-height:220px; padding:19px; border:1px solid var(--line); border-radius:14px; background:linear-gradient(145deg,rgba(20,37,57,.96),rgba(11,24,39,.96)); box-shadow:0 12px 34px rgba(0,0,0,.18); }
    .card-head { display:flex; justify-content:space-between; gap:12px; align-items:start; }
    h2 { margin:0; font-size:16px; }
    .unit { margin-top:3px; font-size:12px; color:var(--muted); }
    .status { font-size:11px; font-weight:700; letter-spacing:.4px; padding:4px 7px; border-radius:12px; background:rgba(72,213,151,.12); color:var(--green); }
    .status.bad { background:rgba(255,102,122,.12); color:var(--red); }
    .big { margin:24px 0 4px; font-size:36px; font-weight:750; letter-spacing:-1px; }
    .triplet,.pair { display:grid; gap:9px; margin-top:19px; }
    .triplet { grid-template-columns:repeat(3,1fr); }
    .pair { grid-template-columns:repeat(2,1fr); }
    .metric { padding:10px; border-radius:9px; background:rgba(4,12,23,.52); }
    .metric b { display:block; margin-top:3px; font-size:20px; }
    .bar { position:relative; height:8px; margin:22px 0 10px; border-radius:9px; background:#24364c; overflow:hidden; }
    .bar > i { display:block; height:100%; width:0; border-radius:inherit; background:linear-gradient(90deg,var(--cyan),var(--green)); transition:width .35s; }
    .threshold { border-top:1px dashed #49617d; margin-top:18px; padding-top:11px; color:var(--muted); font-size:12px; }
    .threshold b { color:var(--amber); }
    .breakdown { min-height:22px; margin-top:12px; color:var(--muted); font-size:12px; overflow-wrap:anywhere; }
    footer { display:flex; justify-content:space-between; margin-top:18px; color:var(--muted); font-size:12px; }
    .error { display:none; margin-bottom:16px; padding:10px 12px; border:1px solid var(--red); border-radius:8px; color:#ffdce1; }
  </style>
</head>
<body>
<main>
  <header>
    <div><h1>Day 13 AI Observability</h1><div class="subtitle">Runtime metrics · 6 operational signals</div></div>
    <div class="controls"><span class="pill">Last 60 minutes</span><span class="pill">Refresh 30s</span><span class="pill live">LIVE</span></div>
  </header>
  <div id="error" class="error"></div>
  <section class="grid">
    <article class="card">
      <div class="card-head"><div><h2>Latency percentiles</h2><div class="unit">Milliseconds (ms)</div></div><span id="latency-status" class="status">WITHIN SLO</span></div>
      <div class="triplet"><div class="metric">P50<b id="p50">—</b></div><div class="metric">P95<b id="p95">—</b></div><div class="metric">P99<b id="p99">—</b></div></div>
      <div class="bar"><i id="latency-bar"></i></div><div class="hint">P95 position against SLO</div>
      <div class="threshold">SLO line · P95 <b>≤ 3,000 ms</b></div>
    </article>
    <article class="card">
      <div class="card-head"><div><h2>Request traffic</h2><div class="unit">Requests in current process</div></div><span class="status">MONITORED</span></div>
      <div id="traffic" class="big">—</div><div class="hint">Successful requests observed</div>
      <div class="bar"><i id="traffic-bar"></i></div>
      <div class="threshold">Operational floor · traffic <b>≥ 1 request</b></div>
    </article>
    <article class="card">
      <div class="card-head"><div><h2>Error rate &amp; breakdown</h2><div class="unit">Percent (%)</div></div><span id="error-status" class="status">WITHIN SLO</span></div>
      <div id="error-rate" class="big">—</div><div class="hint">Failed / total requests</div><div id="breakdown" class="breakdown">No errors recorded</div>
      <div class="threshold">SLO line · error rate <b>≤ 2%</b></div>
    </article>
    <article class="card">
      <div class="card-head"><div><h2>Cost over time</h2><div class="unit">US dollars (USD)</div></div><span id="cost-status" class="status">WITHIN BUDGET</span></div>
      <div id="total-cost" class="big">—</div><div class="hint">Total estimated model cost</div><div class="metric" style="margin-top:16px">Average per request<b id="avg-cost">—</b></div>
      <div class="threshold">Budget threshold · total <b>≤ $2.50</b></div>
    </article>
    <article class="card">
      <div class="card-head"><div><h2>Input &amp; output tokens</h2><div class="unit">Tokens</div></div><span id="tokens-status" class="status">WITHIN LIMIT</span></div>
      <div class="pair"><div class="metric">Input<b id="tokens-in">—</b></div><div class="metric">Output<b id="tokens-out">—</b></div></div>
      <div class="bar"><i id="tokens-bar"></i></div><div class="hint">Combined token consumption</div>
      <div class="threshold">Usage threshold · combined <b>≤ 50,000 tokens</b></div>
    </article>
    <article class="card">
      <div class="card-head"><div><h2>Quality proxy</h2><div class="unit">Average score (0–1)</div></div><span id="quality-status" class="status">MEETS TARGET</span></div>
      <div id="quality" class="big">—</div><div class="hint">Heuristic response quality</div>
      <div class="bar"><i id="quality-bar"></i></div>
      <div class="threshold">Quality threshold · mean <b>≥ 0.75</b></div>
    </article>
  </section>
  <footer><span>Source: <code>/metrics</code> · contract: <code>config/dashboard.yaml</code></span><span id="updated">Waiting for metrics…</span></footer>
</main>
<script>
const number = value => Number(value || 0);
const integer = value => number(value).toLocaleString('en-US');
const setStatus = (id, good, ok, bad) => { const el=document.getElementById(id); el.textContent=good?ok:bad; el.classList.toggle('bad',!good); };
const setBar = (id, value) => document.getElementById(id).style.width=`${Math.max(0,Math.min(100,value))}%`;
async function refresh() {
  try {
    const response=await fetch('/metrics',{cache:'no-store'}); if(!response.ok) throw new Error(`HTTP ${response.status}`); const m=await response.json();
    document.getElementById('p50').textContent=`${integer(m.latency_p50)} ms`; document.getElementById('p95').textContent=`${integer(m.latency_p95)} ms`; document.getElementById('p99').textContent=`${integer(m.latency_p99)} ms`;
    document.getElementById('traffic').textContent=integer(m.traffic); document.getElementById('error-rate').textContent=`${number(m.error_rate_pct).toFixed(2)}%`;
    const parts=Object.entries(m.error_breakdown||{}).map(([key,value])=>`${key}: ${value}`); document.getElementById('breakdown').textContent=parts.length?parts.join(' · '):'No errors recorded';
    document.getElementById('total-cost').textContent=`$${number(m.total_cost_usd).toFixed(4)}`; document.getElementById('avg-cost').textContent=`$${number(m.avg_cost_usd).toFixed(4)}`;
    document.getElementById('tokens-in').textContent=integer(m.tokens_in_total); document.getElementById('tokens-out').textContent=integer(m.tokens_out_total); document.getElementById('quality').textContent=number(m.quality_avg).toFixed(2);
    setBar('latency-bar',number(m.latency_p95)/3000*100); setBar('traffic-bar',number(m.traffic)*10); setBar('tokens-bar',(number(m.tokens_in_total)+number(m.tokens_out_total))/50000*100); setBar('quality-bar',number(m.quality_avg)*100);
    setStatus('latency-status',number(m.latency_p95)<=3000,'WITHIN SLO','SLO BREACH'); setStatus('error-status',number(m.error_rate_pct)<=2,'WITHIN SLO','SLO BREACH'); setStatus('cost-status',number(m.total_cost_usd)<=2.5,'WITHIN BUDGET','OVER BUDGET'); setStatus('tokens-status',number(m.tokens_in_total)+number(m.tokens_out_total)<=50000,'WITHIN LIMIT','OVER LIMIT'); setStatus('quality-status',number(m.quality_avg)>=.75,'MEETS TARGET','BELOW TARGET');
    document.getElementById('updated').textContent=`Updated ${new Date().toLocaleTimeString()}`; document.getElementById('error').style.display='none';
  } catch (error) { const el=document.getElementById('error'); el.textContent=`Metrics unavailable: ${error.message}`; el.style.display='block'; }
}
refresh(); setInterval(refresh,30000);
</script>
</body>
</html>"""
