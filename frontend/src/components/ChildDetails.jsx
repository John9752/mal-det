import React, { useEffect, useState } from "react";
import { Activity, ShieldAlert, Award, Calendar, Heart, ArrowLeft, RefreshCw, ChevronRight, PlusCircle, Check } from "lucide-react";
import API_URL from "../api";

export default function ChildDetails({ t, childId, onBack, token, onUnauthorized }) {
  const [child, setChild] = useState(null);
  const [charts, setCharts] = useState(null);
  const [recs, setRecs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showLogForm, setShowLogForm] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  // Log new measurement form states
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [muac, setMuac] = useState("");
  const [hemoglobin, setHemoglobin] = useState("");
  const [dietaryHabits, setDietaryHabits] = useState("Adequate");
  const [logSubmitting, setLogSubmitting] = useState(false);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      const commonHeaders = {
        "Authorization": `Bearer ${token}`
      };

      // Fetch details
      const detailRes = await fetch(`${API_URL}/api/children/${childId}`, {
        headers: commonHeaders
      });
      if (detailRes.status === 401) {
        onUnauthorized();
        return;
      }
      if (!detailRes.ok) throw new Error("Child not found");
      const childData = await detailRes.json();
      setChild(childData);

      // Fetch charts
      const chartRes = await fetch(`${API_URL}/api/children/${childId}/growth-chart`, {
        headers: commonHeaders
      });
      if (chartRes.status === 401) {
        onUnauthorized();
        return;
      }
      if (chartRes.ok) {
        const chartData = await chartRes.json();
        setCharts(chartData);
      }

      // Fetch recommendations
      const recRes = await fetch(`${API_URL}/api/children/${childId}/recommendations`, {
        headers: commonHeaders
      });
      if (recRes.status === 401) {
        onUnauthorized();
        return;
      }
      if (recRes.ok) {
        const recData = await recRes.json();
        setRecs(recData);
      }
    } catch (e) {
      console.error("Error fetching child details:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, [childId]);

  const handleLogMeasurement = async (e) => {
    e.preventDefault();
    if (!weight || !height || !muac) {
      alert("Weight, height, and MUAC are required.");
      return;
    }
    setLogSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("weight_kg", parseFloat(weight));
      formData.append("height_cm", parseFloat(height));
      formData.append("muac_cm", parseFloat(muac));
      if (hemoglobin) {
        formData.append("hemoglobin_gdl", parseFloat(hemoglobin));
      }
      formData.append("dietary_habits", dietaryHabits);

      const res = await fetch(`${API_URL}/api/children/${childId}/records`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      });

      if (res.status === 401) {
        onUnauthorized();
        return;
      }

      if (res.ok) {
        setShowLogForm(false);
        setWeight("");
        setHeight("");
        setMuac("");
        setHemoglobin("");
        fetchAllData(); // reload charts and records
      } else {
        alert("Failed to submit measurements");
      }
    } catch (err) {
      console.error(err);
      alert("Error submitting measurements");
    } finally {
      setLogSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', gap: '20px' }}>
        <RefreshCw className="pulse-severe" size={32} style={{ animation: 'spin 1.5s linear infinite' }} />
        <p style={{ color: 'var(--text-muted)' }}>{t.loading}</p>
      </div>
    );
  }

  if (!child) {
    return (
      <div className="glass-panel" style={{ padding: '30px', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>Child profile not found.</p>
        <button className="btn" style={{ marginTop: '14px' }} onClick={onBack}>Back to Dashboard</button>
      </div>
    );
  }

  const lastRecord = child.records.length > 0 ? child.records[child.records.length - 1] : null;

  return (
    <div>
      {/* Top Navigation Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <button className="btn btn-secondary" style={{ padding: '10px 18px' }} onClick={onBack}>
          <ArrowLeft size={16} /> Back
        </button>
        <div style={{ display: 'flex', gap: '12px' }}>
          <a 
            href={`${API_URL}/api/children/${childId}/report`} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}
          >
            📄 Download Health Card
          </a>
          <button className="btn" onClick={() => setShowLogForm(!showLogForm)}>
            <PlusCircle size={16} /> Log Measurement
          </button>
        </div>
      </div>

      {/* Log Measurement Modal Box */}
      {showLogForm && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px', borderStyle: 'solid', animation: 'fadeIn 0.3s ease' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 'bold', marginBottom: '16px' }}>Log New Measurements</h3>
          <form onSubmit={handleLogMeasurement}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '14px' }}>
              <div className="form-group">
                <label>{t.weight} *</label>
                <input type="number" step="0.01" className="form-control" value={weight} onChange={(e) => setWeight(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>{t.height} *</label>
                <input type="number" step="0.1" className="form-control" value={height} onChange={(e) => setHeight(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>{t.muac} *</label>
                <input type="number" step="0.1" className="form-control" value={muac} onChange={(e) => setMuac(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>{t.hemoglobin}</label>
                <input type="number" step="0.1" className="form-control" value={hemoglobin} onChange={(e) => setHemoglobin(e.target.value)} />
              </div>
              <div className="form-group">
                <label>{t.diet} *</label>
                <select className="form-control" value={dietaryHabits} onChange={(e) => setDietaryHabits(e.target.value)}>
                  <option value="Poor">{t.poor}</option>
                  <option value="Adequate">{t.adequate}</option>
                  <option value="Good">{t.good}</option>
                </select>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
              <button type="button" className="btn btn-secondary" onClick={() => setShowLogForm(false)}>Cancel</button>
              <button type="submit" className="btn" disabled={logSubmitting}>
                {logSubmitting ? "Saving..." : "Save Record"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Child Header Profile Info */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexWrap: 'wrap', gap: '24px', alignItems: 'center', marginBottom: '24px' }}>
        {lastRecord?.image_path ? (
          <img 
            src={`http://127.0.0.1:8000/static/uploads/${lastRecord.image_path.split(/\/|\\/).pop()}`} 
            alt={child.name} 
            className="photo-upload-preview" 
            style={{ width: '90px', height: '90px', borderRadius: '45px' }} 
            onError={(e) => {
              // Fallback if image load fails
              e.target.style.display = 'none';
            }}
          />
        ) : (
          <div style={{ width: '90px', height: '90px', borderRadius: '45px', background: 'var(--primary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', fontWeight: 'bold' }}>
            {child.name.charAt(0).toUpperCase()}
          </div>
        )}

        <div style={{ flex: 1, minWidth: '200px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <h2 style={{ fontSize: '1.65rem', fontWeight: 'bold' }}>{child.name}</h2>
            {lastRecord && (
              <span className={`status-badge ${lastRecord.status === 'Normal' ? 'normal' : (lastRecord.status === 'Mild Malnutrition' ? 'mild' : (lastRecord.status === 'Moderate Malnutrition' ? 'moderate' : 'severe'))}`}>
                {lastRecord.status === 'Normal' ? t.normal : (lastRecord.status === 'Mild Malnutrition' ? t.mild : (lastRecord.status === 'Moderate Malnutrition' ? t.moderate : t.severe))}
              </span>
            )}
          </div>
          
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '6px' }}>
            {child.gender === "Male" ? t.male : t.female} &bull; {child.age_months.toFixed(0)} Months &bull; {child.village}, {child.district}, {child.state}
          </p>
        </div>

        {lastRecord && (
          <div style={{ textAlign: 'right', minWidth: '120px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>{t.risk_score}</div>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--primary-color)' }}>{lastRecord.risk_score}%</div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="tab-headers">
        <button className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab("overview")}>Overview & History</button>
        <button className={`tab-btn ${activeTab === 'nutrition' ? 'active' : ''}`} onClick={() => setActiveTab("nutrition")}>{t.diet_plan}</button>
        <button className={`tab-btn ${activeTab === 'schemes' ? 'active' : ''}`} onClick={() => setActiveTab("schemes")}>{t.eligible_schemes}</button>
      </div>

      {/* Tab: Overview (Growth Charts and logged list) */}
      {activeTab === "overview" && (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {charts && (
            <div className="growth-profile-container">
              <div className="glass-panel" style={{ padding: '20px' }}>
                <img 
                  src={`data:image/png;base64,${charts.weight_chart_b64}`} 
                  alt="Weight Chart" 
                  style={{ width: '100%', borderRadius: '8px', border: '1px solid var(--card-border)' }} 
                />
              </div>
              <div className="glass-panel" style={{ padding: '20px' }}>
                <img 
                  src={`data:image/png;base64,${charts.height_chart_b64}`} 
                  alt="Height Chart" 
                  style={{ width: '100%', borderRadius: '8px', border: '1px solid var(--card-border)' }} 
                />
              </div>
            </div>
          )}

          {/* Measurements log table */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 'bold', marginBottom: '16px' }}>Logged Measurements History</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--card-border)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px' }}>{t.date}</th>
                    <th style={{ padding: '12px' }}>{t.weight}</th>
                    <th style={{ padding: '12px' }}>{t.height}</th>
                    <th style={{ padding: '12px' }}>{t.muac}</th>
                    <th style={{ padding: '12px' }}>{t.hemoglobin}</th>
                    <th style={{ padding: '12px' }}>{t.diet}</th>
                    <th style={{ padding: '12px' }}>{t.status}</th>
                  </tr>
                </thead>
                <tbody>
                  {child.records.map(rec => (
                    <tr key={rec.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                      <td style={{ padding: '14px 12px' }}>{new Date(rec.recorded_at).toLocaleDateString()}</td>
                      <td style={{ padding: '14px 12px', fontWeight: 'bold' }}>{rec.weight_kg} kg</td>
                      <td style={{ padding: '14px 12px' }}>{rec.height_cm} cm</td>
                      <td style={{ padding: '14px 12px' }}>{rec.muac_cm} cm</td>
                      <td style={{ padding: '14px 12px' }}>{rec.hemoglobin_gdl ? `${rec.hemoglobin_gdl} g/dL` : "-"}</td>
                      <td style={{ padding: '14px 12px' }}>{rec.dietary_habits}</td>
                      <td style={{ padding: '14px 12px' }}>
                        <span className={`status-badge ${rec.status === 'Normal' ? 'normal' : (rec.status === 'Mild Malnutrition' ? 'mild' : (rec.status === 'Moderate Malnutrition' ? 'moderate' : 'severe'))}`}>
                          {rec.status === 'Normal' ? t.normal : (rec.status === 'Mild Malnutrition' ? t.mild : (rec.status === 'Moderate Malnutrition' ? t.moderate : t.severe))}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Diet Plan Recommendations */}
      {activeTab === "nutrition" && recs && (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Targets row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '8px' }}>{t.calories}</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent-color)' }}>{recs.nutrition.required_calories} Kcal</div>
            </div>
            <div className="glass-panel" style={{ padding: '24px', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '8px' }}>{t.proteins}</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--secondary-color)' }}>{recs.nutrition.required_protein_g} grams</div>
            </div>
          </div>

          {/* Regional Foods Suggestion Grid */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 'bold', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Heart size={20} color="var(--status-moderate-text)" /> Locally Sourced Nutritious Foods ({recs.nutrition.region})
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {recs.nutrition.food_recommendations.map((food, idx) => (
                <div key={idx} style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '12px', border: '1px solid var(--card-border)', display: 'flex', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(99,102,241,0.1)', color: 'var(--primary-color)', fontWeight: 'bold', flexShrink: 0 }}>
                    {idx+1}
                  </div>
                  <div>
                    <h4 style={{ fontWeight: '600', fontSize: '0.95rem' }}>{food.food}</h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>{food.benefits}</p>
                    <div style={{ display: 'inline-block', fontSize: '0.75rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)', padding: '2px 8px', borderRadius: '4px', marginTop: '8px' }}>
                      Cost: {food.cost}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Clinical Guidelines / Action Items */}
          <div className="glass-panel" style={{ padding: '24px', borderLeft: '4px solid var(--primary-color)' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 'bold', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={20} color="var(--primary-color)" /> {t.action_required}
            </h3>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', listStyle: 'none' }}>
              {recs.nutrition.clinical_guidelines.map((line, idx) => (
                <li key={idx} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', fontSize: '0.92rem' }}>
                  <ChevronRight size={18} color="var(--primary-color)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Tab: Eligible Welfare Schemes */}
      {activeTab === "schemes" && recs && (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {recs.schemes.map((sch, idx) => (
            <div key={idx} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--accent-color)' }}>{sch.name}</h3>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginTop: '2px' }}>{sch.ministry}</span>
                </div>
                <div className="status-badge normal" style={{ background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', color: 'var(--accent-color)' }}>
                  Eligible
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px', marginTop: '10px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Eligibility Rule</span>
                  <span style={{ fontSize: '0.9rem' }}>{sch.eligibility}</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Scheme Benefits</span>
                  <span style={{ fontSize: '0.9rem', lineHeight: '1.4' }}>{sch.benefits}</span>
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px 18px', borderRadius: '8px', border: '1px solid var(--card-border)', fontSize: '0.88rem', marginTop: '10px' }}>
                <b>How to Claim:</b> {sch.how_to_apply}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
