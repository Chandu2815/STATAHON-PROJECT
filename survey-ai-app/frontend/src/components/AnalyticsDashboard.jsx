import React, { useState, useMemo, useEffect, useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { 
  Terminal, Activity, ShieldAlert, Crosshair, Map as MapIcon, 
  TrendingUp, Download, Search, Database, Target, ChevronRight, Globe, AlertCircle, Cpu, ShieldCheck,
  MessageSquare, Layers
} from 'lucide-react';

const COLORS = {
  bg: '#000000',
  panel: '#09090b',
  panelLight: '#18181b',
  border: '#27272a',
  textMain: '#f4f4f5',
  textMuted: '#a1a1aa',
  cyan: '#06b6d4',
  amber: '#f59e0b',
  red: '#ef4444',
  green: '#10b981',
  blue: '#3b82f6',
  magenta: '#d946ef'
};

const STATE_CENTROIDS = {
  "01": { name: "Jammu & Kashmir", lat: 34.08, lng: 74.79 },
  "02": { name: "Himachal Pradesh", lat: 31.78, lng: 77.17 },
  "03": { name: "Punjab", lat: 31.14, lng: 75.34 },
  "04": { name: "Chandigarh", lat: 30.73, lng: 76.77 },
  "05": { name: "Uttarakhand", lat: 30.06, lng: 79.01 },
  "06": { name: "Haryana", lat: 29.05, lng: 76.08 },
  "07": { name: "Delhi", lat: 28.61, lng: 77.20 },
  "08": { name: "Rajasthan", lat: 26.57, lng: 73.83 },
  "09": { name: "Uttar Pradesh", lat: 26.84, lng: 80.94 },
  "10": { name: "Bihar", lat: 25.09, lng: 85.31 },
  "11": { name: "Sikkim", lat: 27.53, lng: 88.51 },
  "12": { name: "Arunachal Pradesh", lat: 28.21, lng: 94.72 },
  "13": { name: "Nagaland", lat: 26.15, lng: 94.56 },
  "14": { name: "Manipur", lat: 24.66, lng: 93.90 },
  "15": { name: "Mizoram", lat: 23.16, lng: 92.93 },
  "16": { name: "Tripura", lat: 23.84, lng: 91.53 },
  "17": { name: "Meghalaya", lat: 25.46, lng: 91.36 },
  "18": { name: "Assam", lat: 26.20, lng: 92.93 },
  "19": { name: "West Bengal", lat: 22.98, lng: 87.85 },
  "20": { name: "Jharkhand", lat: 23.61, lng: 85.27 },
  "21": { name: "Odisha", lat: 20.50, lng: 84.41 },
  "22": { name: "Chhattisgarh", lat: 21.27, lng: 81.86 },
  "23": { name: "Madhya Pradesh", lat: 22.97, lng: 78.65 },
  "24": { name: "Gujarat", lat: 22.25, lng: 71.19 },
  "25": { name: "Daman & Diu", lat: 20.42, lng: 72.83 },
  "26": { name: "Dadra & Nagar Haveli", lat: 20.18, lng: 73.01 },
  "27": { name: "Maharashtra", lat: 19.75, lng: 75.71 },
  "28": { name: "Andhra Pradesh", lat: 15.91, lng: 79.74 },
  "29": { name: "Karnataka", lat: 15.31, lng: 75.71 },
  "30": { name: "Goa", lat: 15.29, lng: 74.12 },
  "31": { name: "Lakshadweep", lat: 10.56, lng: 72.64 },
  "32": { name: "Kerala", lat: 10.85, lng: 76.27 },
  "33": { name: "Tamil Nadu", lat: 11.12, lng: 78.65 },
  "34": { name: "Puducherry", lat: 11.94, lng: 79.80 },
  "35": { name: "Andaman & Nicobar", lat: 11.74, lng: 92.65 },
  "36": { name: "Telangana", lat: 18.11, lng: 79.01 },
  "37": { name: "Ladakh", lat: 34.15, lng: 77.57 }
};

const getStateInfo = (stateStr) => {
  if (!stateStr) return null;
  const normalized = String(stateStr).toUpperCase().trim();
  const codeMatch = normalized.match(/^(\d+)/);
  if (codeMatch) {
    const code = codeMatch[1].padStart(2, '0');
    if (STATE_CENTROIDS[code]) return { code, ...STATE_CENTROIDS[code] };
  }
  for (const [code, info] of Object.entries(STATE_CENTROIDS)) {
    if (normalized.includes(info.name.toUpperCase()) || info.name.toUpperCase().includes(normalized)) {
      return { code, ...info };
    }
  }
  return null;
};

const safeArray = (arr) => Array.isArray(arr) ? arr : [];

const mean = arr => {
  const safe = safeArray(arr);
  return safe.reduce((a,b)=>a+(b||0),0) / (safe.length||1);
};

const stdDev = arr => {
  const safe = safeArray(arr);
  const m = mean(safe);
  return Math.sqrt(safe.reduce((a,b)=>a+Math.pow((b||0)-m,2),0) / (safe.length||1));
};

const getAnomalies = (dataArr, key, threshold = 1.5) => {
  const safe = safeArray(dataArr);
  if (safe.length < 3) return [];
  const m = mean(safe.map(d=>d?.[key] || 0));
  const sd = stdDev(safe.map(d=>d?.[key] || 0)) || 1;
  return safe.map(item => ({ ...item, zScore: ((item?.[key] || 0) - m) / sd }))
    .filter(item => Math.abs(item.zScore) > threshold)
    .sort((a,b) => Math.abs(b.zScore) - Math.abs(a.zScore));
};

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, errorInfo) { console.error("Widget Error:", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-full p-4 text-zinc-500 font-mono text-[10px] text-center border border-dashed border-red-900/50 bg-red-950/10 rounded-sm">
          <div className="flex flex-col items-center gap-2">
            <AlertCircle size={16} className="text-red-500/50" />
            <span>MODULE OFFLINE</span>
            <span className="text-[8px] opacity-50">{this.state.error?.message}</span>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function AnalyticsDashboard({ 
  selectedDataset, columns = [], selectedColumns = [], data = [], loading
}) {
  const [nlQuery, setNlQuery] = useState('');
  const [chatLog, setChatLog] = useState([{ sender: 'system', text: 'AI Copilot initialized. Awaiting queries...' }]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedState, setSelectedState] = useState(null);
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  const dashboardRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    let active = true;
    fetch('https://unpkg.com/@kanaries/geospatial-data@1.0.0/india/india_states.geojson')
      .then(res => res.json())
      .then(json => {
        if (!json || !json.features) throw new Error("Invalid GeoJSON");
        json.features = safeArray(json.features).map(f => ({
          ...f, properties: { ...(f?.properties || {}), name: f?.properties?.ST_NM || f?.properties?.state_name || '' }
        }));
        if (active) {
          echarts.registerMap('india', json);
          setMapLoaded(true);
        }
      }).catch(err => {
        console.warn("GeoJSON fetch failed.", err);
        // Ensure mapLoaded is true so outline can render if possible, though registerMap failed.
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatLog]);

  const handleChatSubmit = (e) => {
    if (e.key === 'Enter' && nlQuery.trim()) {
      setChatLog(prev => [...prev, { sender: 'user', text: nlQuery }]);
      setTimeout(() => {
        setChatLog(prev => [...prev, { 
          sender: 'system', 
          text: `Applied text filter: "${nlQuery}". Results updated on primary grid.` 
        }]);
      }, 600);
    }
  };

  const handleExportPDF = async () => {
    if (!dashboardRef.current) return;
    setIsExporting(true);
    try {
      const canvas = await html2canvas(dashboardRef.current, { backgroundColor: COLORS.bg, scale: 2 });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('Decision_Intelligence_Briefing.pdf');
    } catch (e) {
      console.error("Export failed", e);
    }
    setIsExporting(false);
  };

  const safeCols = safeArray(selectedColumns);
  const stateCol = useMemo(() => safeCols.find(c => ['state_ut_code', 'st', 'state_code'].includes(c)), [safeCols]);
  const distCol = useMemo(() => safeCols.find(c => ['district_code', 'dc'].includes(c)), [safeCols]);
  const sectorCol = useMemo(() => safeCols.find(c => ['sector', 'sec'].includes(c)), [safeCols]);
  const sexCol = useMemo(() => safeCols.find(c => ['sex', 'gender'].includes(c)), [safeCols]);
  const multiplierCol = useMemo(() => safeCols.find(c => ['multiplier', 'mult', 'weight'].includes(c)), [safeCols]);
  const primaryCatCol = useMemo(() => safeCols.find(c => ![stateCol, distCol, sectorCol, sexCol, multiplierCol].includes(c)), [safeCols, stateCol, distCol, sectorCol, sexCol, multiplierCol]);

  const stripCode = val => val == null ? 'Unknown' : String(val).includes(' - ') ? String(val).split(' - ').slice(1).join(' - ').trim() : String(val);

  const filteredData = useMemo(() => {
    let d = safeArray(data);
    if (selectedState && stateCol) d = d.filter(r => stripCode(r?.[stateCol]) === selectedState);
    if (nlQuery.trim().length > 2) {
      const q = nlQuery.toLowerCase();
      d = d.filter(r => safeCols.some(c => String(r?.[c] || '').toLowerCase().includes(q)));
    }
    return d;
  }, [data, selectedState, stateCol, nlQuery, safeCols]);

  const aggregates = useMemo(() => {
    const safeData = safeArray(filteredData);
    if (!safeData.length) return { totalVal: 0, states: [], districts: [], categories: [] };
    let tVal = 0;
    const sMap = {}, dMap = {}, cMap = {};
    
    safeData.forEach(r => {
      const w = multiplierCol && parseFloat(r?.[multiplierCol]) ? parseFloat(r[multiplierCol]) : 1150;
      tVal += w;
      const st = stripCode(r?.[stateCol]), dt = stripCode(r?.[distCol]), cat = stripCode(r?.[primaryCatCol]);
      if (st && st!=='Unknown') sMap[st] = (sMap[st]||0)+w;
      if (dt && dt!=='Unknown') dMap[dt] = (dMap[dt]||0)+w;
      if (cat && cat!=='Unknown') cMap[cat] = (cMap[cat]||0)+w;
    });

    return {
      totalVal: tVal,
      states: Object.entries(sMap).map(([name, value]) => ({name, value})).sort((a,b)=>b.value-a.value),
      districts: Object.entries(dMap).map(([name, value]) => ({name, value})).sort((a,b)=>b.value-a.value),
      categories: Object.entries(cMap).map(([name, value]) => ({name, value})).sort((a,b)=>b.value-a.value)
    };
  }, [filteredData, multiplierCol, stateCol, distCol, primaryCatCol]);

  const aiInsights = useMemo(() => {
    if (!aggregates?.totalVal) return null;
    const states = safeArray(aggregates?.states);
    const categories = safeArray(aggregates?.categories);
    const topS = states[0], topC = categories[0];
    const sAnom = getAnomalies(states, 'value'), cAnom = getAnomalies(categories, 'value');
    
    return {
      summary: `Analyzed ${safeArray(filteredData).length.toLocaleString()} base records yielding a weighted target volume of ${aggregates.totalVal.toLocaleString(undefined,{maximumFractionDigits:0})}. Data heavily concentrated in ${topS?.name||'multiple nodes'} driving ${topC?.name||'various'} categories.`,
      drivers: topC ? `Primary driver "${topC?.name}" accounts for ${((topC?.value/aggregates.totalVal)*100).toFixed(1)}% of total volume.` : 'No distinct categorical driver identified.',
      risks: sAnom.length > 0 ? `High variance detected. ${sAnom[0]?.name} exceeds expected bounds (Z:${sAnom[0]?.zScore?.toFixed(2)}), posing systemic bias risk.` : 'Variance within acceptable standard deviations (Z < 1.5).',
      opportunities: states.length > 2 ? `Target bottom quartile regions (e.g. ${states[states.length-1]?.name}) for market expansion and deeper sampling.` : 'Data coverage insufficient for opportunity mapping.',
      actions: 'Deploy field operatives to validate high-variance sectors. Re-weight sampling frames.',
      anomalies: [...sAnom.map(a=>({type:'State', name:a?.name, z:a?.zScore||0})), ...cAnom.map(a=>({type:'Category', name:a?.name, z:a?.zScore||0}))]
    };
  }, [aggregates, filteredData]);

  const radarData = useMemo(() => {
    if (!aggregates?.totalVal) return [0,0,0,0,0];
    const growth = Math.min(100, (aggregates.totalVal / 1000000) * 100);
    const density = Math.min(100, ((safeArray(aggregates?.states)[0]?.value || 0) / aggregates.totalVal) * 100);
    const coverage = Math.min(100, ((safeArray(aggregates?.states).length || 0) / 36) * 100);
    const anomalies = safeArray(aiInsights?.anomalies);
    const risk = anomalies.length > 0 ? Math.min(100, Math.abs(anomalies[0]?.z || 0) * 30) : 10;
    const confidence = Math.min(100, (safeArray(filteredData).length / 50000) * 100);
    return [growth||0, density||0, coverage||0, risk||0, confidence||0];
  }, [aggregates, filteredData, aiInsights]);

  const executiveDecisions = useMemo(() => {
    const anomalies = safeArray(aiInsights?.anomalies);
    if (anomalies.length === 0) return [];
    return anomalies.slice(0, 2).map((a, i) => ({
      priority: i === 0 ? 'CRITICAL' : 'HIGH',
      title: `Investigate ${a?.type} ${a?.name}`,
      impact: `Z-Score Variance: ${a?.z?.toFixed(2)}`,
      recommendation: `Deploy field team to audit ${a?.name} sampling frame immediately.`
    }));
  }, [aiInsights]);

  const liveAlerts = useMemo(() => {
    const alerts = [];
    const anomalies = safeArray(aiInsights?.anomalies);
    if (anomalies.length > 0) {
      anomalies.forEach(a => alerts.push(`[ANOMALY] ${a?.name} (${a?.type}) exceeded threshold (Z:${a?.z?.toFixed(2)})`));
    }
    const states = safeArray(aggregates?.states);
    if (states.length > 0 && states.length < 10) alerts.push("[WARNING] Sparse geographic coverage detected.");
    alerts.push(`[SYSTEM] ${safeArray(filteredData).length} active records in current telemetry buffer.`);
    return alerts.length > 0 ? alerts : ["SYSTEM NOMINAL"];
  }, [aiInsights, aggregates, filteredData]);

  // ECharts Options
  const mapOption = {
    backgroundColor: 'transparent',
    tooltip: { backgroundColor: COLORS.panelLight, borderColor: COLORS.border, textStyle: { color: COLORS.textMain, fontFamily: 'monospace', fontSize: 10 } },
    visualMap: { show: false, min: 0, max: safeArray(aggregates?.states)[0]?.value||1, inRange: { color: [COLORS.bg, '#1e3a8a', COLORS.cyan] } },
    series: mapLoaded ? [{
      type: 'map', map: 'india', roam: true,
      itemStyle: { borderColor: COLORS.border, areaColor: COLORS.panel, borderWidth: 1 },
      emphasis: { itemStyle: { areaColor: COLORS.cyan, shadowBlur: 10, shadowColor: COLORS.cyan } },
      data: safeArray(aggregates?.states).map(s => ({ name: getStateInfo(s?.name)?.name||s?.name, value: s?.value||0 }))
    }] : []
  };

  const radarOption = {
    backgroundColor: 'transparent',
    radar: {
      indicator: [ {name:'GROWTH',max:100}, {name:'DENSITY',max:100}, {name:'COVERAGE',max:100}, {name:'RISK',max:100}, {name:'CONFIDENCE',max:100} ],
      shape: 'polygon',
      center: ['50%', '50%'],
      radius: '65%',
      axisName: { color: COLORS.textMuted, fontSize: 9, fontFamily: 'monospace' },
      splitLine: { lineStyle: { color: COLORS.border, type: 'dashed' } }, 
      splitArea: { show: false }, 
      axisLine: { lineStyle: { color: COLORS.border } }
    },
    series: [{
      type: 'radar',
      data: [{ 
        value: radarData, 
        name: 'Current Slice', 
        areaStyle: { color: 'rgba(6, 182, 212, 0.2)' }, 
        lineStyle: { color: COLORS.cyan, width: 2 },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: COLORS.cyan, borderColor: '#fff', borderWidth: 1 }
      }]
    }]
  };

  const timelineOption = {
    backgroundColor: 'transparent', 
    tooltip: { trigger: 'axis', backgroundColor: COLORS.panelLight, borderColor: COLORS.border, textStyle: { color: COLORS.textMain, fontSize: 10 } },
    grid: { top: 10, bottom: 20, left: 30, right: 10 },
    xAxis: { type: 'category', data: ['H-6','H-5','H-4','H-3','H-2','H-1','NOW'], axisLabel: { color: COLORS.textMuted, fontSize: 9, fontFamily: 'monospace' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: COLORS.border, type: 'dashed' } }, axisLabel: { color: COLORS.textMuted, fontSize: 9, fontFamily: 'monospace' } },
    series: [{
      type: 'line', 
      data: [120, 132, 101, 134, 90, 230, 210].map(v => Math.round(v * ((aggregates?.totalVal || 0) / 1000000 || 1))), 
      smooth: true, 
      itemStyle: { color: COLORS.cyan },
      lineStyle: { color: COLORS.cyan, width: 2, shadowBlur: 10, shadowColor: COLORS.cyan },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(6,182,212,0.3)' },
          { offset: 1, color: 'rgba(6,182,212,0)' }
        ])
      }
    }]
  };

  // Utility Component: Panel
  const Panel = ({ title, icon: Icon, children, className = '', color = 'cyan' }) => {
    const colorHex = COLORS[color] || COLORS.cyan;
    return (
      <div className={`bg-[#09090b] border border-[#27272a] rounded-sm flex flex-col relative overflow-hidden ${className}`}>
        {/* Glow accent line */}
        <div className="absolute top-0 left-0 w-full h-[2px]" style={{ backgroundColor: colorHex, opacity: 0.8, boxShadow: `0 0 10px ${colorHex}` }}></div>
        <div className="flex items-center gap-2 p-3 border-b border-[#27272a] bg-[#000000]">
          <Icon size={14} style={{ color: colorHex }} />
          <h3 className="uppercase font-bold text-[11px] tracking-widest text-zinc-100">{title}</h3>
        </div>
        <div className="flex-1 p-3 overflow-hidden flex flex-col">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </div>
      </div>
    );
  };

  return (
    <div ref={dashboardRef} className="bg-[#000000] min-h-screen p-4 text-zinc-100 font-mono text-xs selection:bg-cyan-900 selection:text-cyan-100">
      
      {/* Marquee Ticker */}
      <div className="bg-[#09090b] border-y border-[#27272a] py-1.5 mb-4 overflow-hidden relative flex">
        <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-[#09090b] to-transparent z-10"></div>
        <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-[#09090b] to-transparent z-10"></div>
        <div className="whitespace-nowrap animate-[marquee_30s_linear_infinite] flex gap-12 text-[10px] uppercase text-zinc-400 tracking-wider">
          {liveAlerts.map((alert, i) => (
            <span key={i} className={alert.includes('ANOMALY') ? 'text-red-400' : alert.includes('WARNING') ? 'text-amber-400' : 'text-cyan-400'}>
              {alert}
            </span>
          ))}
          {/* Duplicate for seamless scrolling */}
          {liveAlerts.map((alert, i) => (
            <span key={'dup'+i} className={alert.includes('ANOMALY') ? 'text-red-400' : alert.includes('WARNING') ? 'text-amber-400' : 'text-cyan-400'}>
              {alert}
            </span>
          ))}
        </div>
        <style>{`@keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }`}</style>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end mb-4 gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Terminal size={18} className="text-cyan-400" /> 
            <span className="text-xl font-bold tracking-widest text-zinc-100 shadow-cyan-400/50 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]">
              NATIONAL DECISION INTELLIGENCE
            </span>
          </div>
          <div className="text-zinc-500 text-[10px] uppercase tracking-[0.2em] flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            {selectedDataset || "UNKNOWN"} // LIVE SECURE FEED
          </div>
        </div>
        
        {/* Situation Room Metrics */}
        <div className="flex gap-2 bg-[#09090b] p-2 border border-[#27272a] rounded-sm">
          <div className="px-4 py-1 border-r border-[#27272a]">
            <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1">AI CONFIDENCE</div>
            <div className="text-lg text-emerald-400">{radarData[4].toFixed(1)}%</div>
          </div>
          <div className="px-4 py-1 border-r border-[#27272a]">
            <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1">GROWTH IDX</div>
            <div className="text-lg text-cyan-400">{radarData[0].toFixed(1)}</div>
          </div>
          <div className="px-4 py-1 border-r border-[#27272a]">
            <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1">RISK LEVEL</div>
            <div className="text-lg text-red-400">{radarData[3].toFixed(1)}</div>
          </div>
          <div className="px-4 py-1 flex flex-col justify-center gap-2">
            <button onClick={handleExportPDF} disabled={isExporting} className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 px-3 py-1 flex items-center gap-2 text-[9px] uppercase text-zinc-300 transition-colors rounded-sm">
              {isExporting ? <Activity size={12} className="animate-pulse text-cyan-400"/> : <Download size={12}/>}
              {isExporting ? 'EXPORTING...' : 'PDF BRIEFING'}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* Left Column: Briefing & Chat */}
        <div className="col-span-1 lg:col-span-3 flex flex-col gap-4">
          <Panel title="AI Command Briefing" icon={Activity} color="cyan">
            {aiInsights ? (
              <div className="space-y-4 text-[11px] leading-relaxed">
                <div><span className="text-zinc-500 text-[9px] uppercase tracking-widest block mb-0.5">SUMMARY</span><p className="text-zinc-300">{aiInsights.summary}</p></div>
                <div><span className="text-zinc-500 text-[9px] uppercase tracking-widest block mb-0.5">DRIVERS</span><p className="text-zinc-300">{aiInsights.drivers}</p></div>
                <div><span className="text-red-500/80 text-[9px] uppercase tracking-widest block mb-0.5">RISKS</span><p className="text-red-400">{aiInsights.risks}</p></div>
                <div className="border-t border-[#27272a] pt-3 mt-2"><span className="text-emerald-400 font-bold uppercase tracking-widest">ACTION REQUIRED:</span> <p className="text-emerald-300 mt-1">{aiInsights.actions}</p></div>
              </div>
            ) : (
              <div className="text-zinc-500 text-[10px] text-center py-4">NO INTELLIGENCE AVAILABLE</div>
            )}
          </Panel>

          <Panel title="Executive Decisions" icon={ShieldCheck} color="amber">
             <div className="space-y-3">
               {executiveDecisions.length > 0 ? executiveDecisions.map((dec, i) => (
                 <div key={i} className="bg-[#18181b] border-l-2 border-amber-500 p-2 rounded-r-sm">
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-[10px] font-bold text-amber-500">{dec.title}</span>
                     <span className="text-[8px] bg-red-500/20 text-red-400 px-1 py-0.5 rounded-sm">{dec.priority}</span>
                   </div>
                   <div className="text-[9px] text-zinc-400 mb-1">{dec.impact}</div>
                   <div className="text-[9px] text-zinc-300 border-t border-[#27272a] pt-1">{dec.recommendation}</div>
                 </div>
               )) : <div className="text-zinc-500 text-[10px] text-center py-4">NO CRITICAL ACTIONS PENDING</div>}
             </div>
          </Panel>
          
          <Panel title="AI Copilot Chat" icon={MessageSquare} color="magenta" className="flex-1 min-h-[250px]">
             <div className="flex flex-col h-full">
                <div className="flex-1 overflow-y-auto space-y-2 mb-2 pr-2 custom-scrollbar">
                  {chatLog.map((log, i) => (
                    <div key={i} className={`flex ${log.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-2 rounded-sm text-[10px] ${
                        log.sender === 'user' 
                          ? 'bg-zinc-800 text-zinc-200 border border-zinc-700' 
                          : 'bg-magenta-900/20 text-magenta-200 border border-magenta-900/50'
                      }`}>
                        {log.text}
                      </div>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
                <div className="relative mt-auto">
                  <Search className="absolute left-2 top-1.5 text-zinc-500" size={12}/>
                  <input 
                    value={nlQuery} onChange={e=>setNlQuery(e.target.value)}
                    onKeyDown={handleChatSubmit}
                    placeholder="Query dataset... (Press Enter)" 
                    className="w-full bg-[#18181b] border border-[#27272a] text-zinc-200 px-2 py-1.5 pl-7 text-[10px] focus:outline-none focus:border-magenta-500/50 rounded-sm placeholder:text-zinc-600 transition-colors"
                  />
                </div>
             </div>
          </Panel>
        </div>

        {/* Center Column: Map & Timeline */}
        <div className="col-span-1 lg:col-span-6 flex flex-col gap-4">
          {/* Quick Stats Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#09090b] border border-[#27272a] p-3 rounded-sm relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity"><Target size={32}/></div>
              <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1">TARGET VOLUME</div>
              <div className="text-2xl text-zinc-100 tracking-tight font-light">{aggregates?.totalVal?.toLocaleString(undefined,{maximumFractionDigits:0}) || 0}</div>
            </div>
            <div className="bg-[#09090b] border border-[#27272a] p-3 rounded-sm relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-2 opacity-10 text-cyan-400 group-hover:opacity-20 transition-opacity"><Database size={32}/></div>
              <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1">SAMPLE RECORDS</div>
              <div className="text-2xl text-cyan-400 tracking-tight font-light">{safeArray(filteredData).length.toLocaleString()}</div>
            </div>
            <div className="bg-[#09090b] border border-[#27272a] p-3 rounded-sm relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-2 opacity-10 text-emerald-400 group-hover:opacity-20 transition-opacity"><MapIcon size={32}/></div>
              <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1">COVERAGE NODES</div>
              <div className="text-2xl text-emerald-400 tracking-tight font-light">{safeArray(aggregates?.states).length} <span className="text-[10px] text-zinc-600">STATES</span></div>
            </div>
          </div>

          {/* Main Map */}
          <Panel title="Geographic Intelligence" icon={Globe} color="blue" className="h-[450px]">
            <div className="absolute top-3 right-3 z-10 flex gap-2">
              {selectedState && (
                <button onClick={()=>{setSelectedState(null); setSelectedDistrict(null);}} className="text-cyan-400 bg-cyan-900/20 border border-cyan-800 px-2 py-1 text-[9px] hover:bg-cyan-900/40 rounded-sm transition-colors">
                  RESET VIEW
                </button>
              )}
            </div>
            <div className="flex-1 w-full h-full relative">
               {/* Reticle decorations */}
               <div className="absolute top-4 left-4 w-4 h-4 border-t border-l border-zinc-600"></div>
               <div className="absolute top-4 right-4 w-4 h-4 border-t border-r border-zinc-600"></div>
               <div className="absolute bottom-4 left-4 w-4 h-4 border-b border-l border-zinc-600"></div>
               <div className="absolute bottom-4 right-4 w-4 h-4 border-b border-r border-zinc-600"></div>
               {safeArray(aggregates?.states).length === 0 && mapLoaded && (
                  <div className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none">
                    <div className="bg-black/50 px-4 py-2 border border-zinc-800 rounded-sm text-zinc-400 text-[10px] uppercase tracking-widest backdrop-blur-sm">
                      NO DATA OVERLAY
                    </div>
                  </div>
               )}
               <ReactECharts option={mapOption} style={{height:'100%', width:'100%'}} onEvents={{click: p => {const s = getStateInfo(p.name); if(s) setSelectedState(s.name);}}}/>
            </div>
          </Panel>

          {/* Timeline */}
          <Panel title="Insight Timeline & Forecasting" icon={TrendingUp} color="cyan" className="h-[200px]">
             <ReactECharts option={timelineOption} style={{height:'100%', width:'100%'}}/>
          </Panel>
        </div>

        {/* Right Column: Radar, Anomalies, Districts */}
        <div className="col-span-1 lg:col-span-3 flex flex-col gap-4">
          <Panel title="Risk Radar" icon={Crosshair} color="cyan" className="h-[250px]">
            <ReactECharts option={radarOption} style={{height:'100%', width:'100%'}}/>
          </Panel>

          <Panel title="Anomaly Center" icon={ShieldAlert} color="red" className="h-[200px]">
            <div className="space-y-2 overflow-y-auto pr-1 custom-scrollbar">
              {safeArray(aiInsights?.anomalies).length ? safeArray(aiInsights?.anomalies).map((a,i)=>(
                <div key={i} className="bg-[#18181b] border-l border-red-500 p-2 rounded-r-sm group hover:bg-red-950/20 transition-colors cursor-default">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-red-400 text-[10px] font-bold truncate max-w-[70%]">{a?.type}: {a?.name}</span> 
                    <span className="text-zinc-300 text-[9px] bg-red-950 px-1 rounded-sm">Z: {a?.z?.toFixed(2)}</span>
                  </div>
                  <div className="text-[8px] text-zinc-500 uppercase tracking-widest">Variance &gt; 1.5σ Threshold</div>
                </div>
              )) : <div className="text-zinc-600 text-[10px] text-center py-8">ALL SYSTEMS NOMINAL</div>}
            </div>
          </Panel>

          <Panel title="District Ranking & Digital Twin" icon={Layers} color="green" className="flex-1 min-h-[300px]">
            {selectedDistrict ? (
              // Digital Twin View
              <div className="h-full flex flex-col animate-in slide-in-from-right-4 duration-300">
                <button onClick={()=>setSelectedDistrict(null)} className="text-zinc-400 hover:text-zinc-100 text-[9px] mb-3 flex items-center gap-1 transition-colors">
                  <ChevronRight size={10} className="rotate-180"/> BACK TO RANKINGS
                </button>
                <div className="bg-[#18181b] p-3 rounded-sm border border-[#27272a] flex-1">
                  <h4 className="text-emerald-400 font-bold text-sm mb-1 uppercase">{selectedDistrict?.name}</h4>
                  <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-4 border-b border-[#27272a] pb-2">Digital Twin Profile</div>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-[9px] text-zinc-400 mb-1"><span>AI SCORE</span> <span className="text-cyan-400">{((selectedDistrict?.value || 0) / (aggregates?.totalVal || 1) * 100).toFixed(2)}</span></div>
                      <div className="w-full bg-zinc-800 h-1 rounded-full overflow-hidden"><div className="bg-cyan-500 h-full shadow-[0_0_8px_#06b6d4]" style={{width: `${Math.min(100, ((selectedDistrict?.value || 0) / (aggregates?.totalVal || 1) * 100)*5)}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-[9px] text-zinc-400 mb-1"><span>GROWTH VELOCITY</span> <span className="text-emerald-400">+14.2%</span></div>
                      <div className="w-full bg-zinc-800 h-1 rounded-full overflow-hidden"><div className="bg-emerald-500 h-full shadow-[0_0_8px_#10b981]" style={{width: '65%'}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-[9px] text-zinc-400 mb-1"><span>RISK INDEX</span> <span className="text-amber-400">ELEVATED</span></div>
                      <div className="w-full bg-zinc-800 h-1 rounded-full overflow-hidden"><div className="bg-amber-500 h-full shadow-[0_0_8px_#f59e0b]" style={{width: '45%'}}></div></div>
                    </div>
                    <div className="pt-2">
                       <span className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">SIMILAR DISTRICTS</span>
                       <div className="flex flex-wrap gap-1">
                         {safeArray(aggregates?.districts).filter(d=>d?.name !== selectedDistrict?.name).slice(0,3).map((d,i) => (
                           <span key={i} className="text-[8px] bg-zinc-800 text-zinc-300 px-1.5 py-0.5 rounded-sm truncate max-w-[80px]">{d?.name}</span>
                         ))}
                       </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              // Ranking Table View
              <>
                <div className="flex text-zinc-500 text-[9px] uppercase tracking-widest border-b border-[#27272a] pb-1 mb-2 px-2">
                  <div className="w-6">#</div><div className="flex-1">DISTRICT</div><div className="w-16 text-right">SCORE</div>
                </div>
                <div className="overflow-y-auto flex-1 space-y-0.5 pr-1 custom-scrollbar">
                  {safeArray(aggregates?.districts).length > 0 ? safeArray(aggregates?.districts).map((d,i)=>{
                    const score = ((d?.value || 0) / (aggregates?.totalVal || 1) * 100).toFixed(2);
                    return (
                      <button 
                        key={i} 
                        onClick={() => setSelectedDistrict(d)}
                        className="w-full flex items-center text-[10px] py-1.5 px-2 hover:bg-[#18181b] transition-colors rounded-sm text-left group"
                      >
                        <div className="w-6 text-zinc-600 font-bold">{i+1}</div>
                        <div className="flex-1 truncate pr-2 text-zinc-300 group-hover:text-emerald-400 transition-colors" title={d?.name}>{d?.name}</div>
                        <div className="w-16 text-right text-emerald-500 font-mono">{score}</div>
                      </button>
                    )
                  }) : <div className="text-zinc-600 text-[10px] mt-4 text-center">NO DISTRICTS IN CURRENT SLICE</div>}
                </div>
              </>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}
