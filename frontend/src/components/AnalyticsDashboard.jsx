import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Users, AlertCircle, HeartPulse, RefreshCw, BarChart2 } from "lucide-react";
import API_URL from "../api";

export default function AnalyticsDashboard({ t, onViewChild, token, onUnauthorized }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [trainReport, setTrainReport] = useState("");
  const [showReport, setShowReport] = useState(false);
  


  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/analytics`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (res.status === 401) {
        onUnauthorized();
        return;
      }
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error("Error fetching analytics:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);



  const handleTrainModel = async () => {
    try {
      setTraining(true);
      const res = await fetch(`${API_URL}/api/train`, { 
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (res.status === 401) {
        onUnauthorized();
        return;
      }
      if (res.ok) {
        const json = await res.json();
        setTrainReport(json.report);
        setShowReport(true);
        fetchAnalytics(); // Refresh stats in case ML model changed categorisation
      }
    } catch (e) {
      console.error("Training request failed:", e);
    } finally {
      setTraining(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', gap: '20px' }}>
        <div className="btn btn-secondary" style={{ pointerEvents: 'none', border: 'none', background: 'transparent' }}>
          <RefreshCw className="pulse-severe" size={32} style={{ animation: 'spin 1.5s linear infinite' }} />
        </div>
        <p style={{ color: 'var(--text-muted)' }}>{t.loading}</p>
      </div>
    );
  }

  // Formatting data for Recharts
  const distributionData = [
    { name: t.normal, value: data?.malnutrition_distribution["Normal"] || 0, color: "#10b981" },
    { name: t.mild, value: data?.malnutrition_distribution["Mild Malnutrition"] || 0, color: "#fbbf24" },
    { name: t.moderate, value: data?.malnutrition_distribution["Moderate Malnutrition"] || 0, color: "#f97316" },
    { name: t.severe, value: data?.malnutrition_distribution["Severe Malnutrition"] || 0, color: "#ef4444" }
  ];

  const ageData = Object.keys(data?.age_distribution || {}).map(key => ({
    name: key,
    children: data.age_distribution[key]
  }));

  const genderPieData = Object.keys(data?.gender_distribution || {}).map(key => ({
    name: key === "Male" ? t.male : t.female,
    value: data.gender_distribution[key]
  }));
  
  const COLORS = ["#6366f1", "#a855f7"];

  return (
    <div>
      {/* KPI Section */}
      <div className="kpi-grid">
        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <h4>{t.kpi_registered}</h4>
            <div className="kpi-value">{data?.kpis.total_registered}</div>
          </div>
          <div className="kpi-icon-wrapper primary">
            <Users size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <h4>{t.kpi_sam}</h4>
            <div className="kpi-value" style={{ color: 'var(--status-severe-text)' }}>
              {data?.kpis.sam_cases}
            </div>
          </div>
          <div className="kpi-icon-wrapper danger">
            <AlertCircle size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <h4>{t.kpi_mam}</h4>
            <div className="kpi-value" style={{ color: 'var(--status-moderate-text)' }}>
              {data?.kpis.mam_cases}
            </div>
          </div>
          <div className="kpi-icon-wrapper warning">
            <AlertCircle size={24} />
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-info">
            <h4>{t.kpi_anemia}</h4>
            <div className="kpi-value" style={{ color: '#06b6d4' }}>
              {data?.kpis.anemia_cases}
            </div>
          </div>
          <div className="kpi-icon-wrapper accent">
            <HeartPulse size={24} />
          </div>
        </div>
      </div>

      {/* Quick Rates Bar */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexWrap: 'wrap', gap: '40px', justifyContent: 'space-around', marginBottom: '30px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{t.wasting_rate}</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--status-moderate-text)', marginTop: '4px' }}>{data?.kpis.wasting_rate}%</div>
        </div>
        <div style={{ width: '1px', background: 'var(--card-border)' }} />
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{t.stunting_rate}</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--status-mild-text)', marginTop: '4px' }}>{data?.kpis.stunting_rate}%</div>
        </div>
        <div style={{ width: '1px', background: 'var(--card-border)' }} />
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{t.underweight_rate}</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--status-severe-text)', marginTop: '4px' }}>{data?.kpis.underweight_rate}%</div>
        </div>
      </div>

      {/* Dashboard Main Visuals */}
      <div style={{ marginBottom: '30px' }}>
        {/* Nutritional Status Distribution Chart - Full Width */}
        <div className="glass-panel chart-card">
          <div className="chart-header">
            <h3><BarChart2 size={20} color="var(--secondary-color)" /> {t.status}</h3>
          </div>
          <div style={{ height: '340px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData} margin={{ top: 10, right: 30, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 13 }} />
                <YAxis tick={{ fill: 'var(--text-muted)' }} />
                <Tooltip 
                  contentStyle={{ background: '#1e293b', border: '1px solid var(--card-border)', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Secondary Graphs */}
      <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        {/* Age Groups Distribution */}
        <div className="glass-panel chart-card">
          <div className="chart-header">
            <h3>{t.age}</h3>
          </div>
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)' }} />
                <YAxis tick={{ fill: 'var(--text-muted)' }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                <Bar dataKey="children" fill="var(--primary-color)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gender Breakdown */}
        <div className="glass-panel chart-card">
          <div className="chart-header">
            <h3>{t.gender}</h3>
          </div>
          <div style={{ height: '280px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={genderPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {genderPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Model Retraining Section */}
      <div className="glass-panel model-train-panel" style={{ borderStyle: 'dashed' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{t.re_train_model}</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            Run synthetic generation and update Random Forest / XGBoost classifiers with current settings.
          </p>
        </div>
        <button className="btn" onClick={handleTrainModel} disabled={training}>
          <RefreshCw size={18} className={training ? "pulse-severe" : ""} style={{ animation: training ? 'spin 1s linear infinite' : 'none' }} />
          {training ? "Training..." : t.re_train_model}
        </button>
      </div>

      {showReport && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '30px', animation: 'fadeIn 0.5s ease' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--primary-color)' }}>{t.model_accuracy}</h3>
            <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => setShowReport(false)}>
              Hide
            </button>
          </div>
          <div className="model-report-box">{trainReport}</div>
        </div>
      )}

      {/* High Risk Alerts Grid Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 'bold', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={20} color="var(--status-severe-text)" /> {t.high_risk_list}
        </h3>
        {data?.high_risk_list.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>{t.no_alerts}</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '600px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--card-border)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '12px' }}>{t.name}</th>
                  <th style={{ padding: '12px' }}>{t.age}</th>
                  <th style={{ padding: '12px' }}>{t.village}</th>
                  <th style={{ padding: '12px' }}>{t.status}</th>
                  <th style={{ padding: '12px' }}>{t.risk_score}</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.high_risk_list.map(child => (
                  <tr key={child.child_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <td style={{ padding: '14px 12px', fontWeight: '600' }}>{child.name}</td>
                    <td style={{ padding: '14px 12px' }}>{child.age_months.toFixed(0)}m</td>
                    <td style={{ padding: '14px 12px' }}>{child.village}</td>
                    <td style={{ padding: '14px 12px' }}>
                      <span className={`status-badge ${child.status === 'Severe Malnutrition' ? 'severe' : 'moderate'}`}>
                        {child.status === 'Severe Malnutrition' ? t.severe : t.moderate}
                      </span>
                    </td>
                    <td style={{ padding: '14px 12px', fontWeight: 'bold' }}>{child.risk_score}%</td>
                    <td style={{ padding: '14px 12px', textAlign: 'right' }}>
                      <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }} onClick={() => onViewChild(child.child_id)}>
                        {t.view_details}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
