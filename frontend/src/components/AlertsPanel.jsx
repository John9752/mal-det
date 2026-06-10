import React, { useEffect, useState } from "react";
import { AlertTriangle, Calendar, Clipboard, CheckCircle, RefreshCw, ChevronRight } from "lucide-react";
import API_URL from "../api";

export default function AlertsPanel({ t, onViewChild, token, onUnauthorized }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeAlert, setActiveAlert] = useState(null); // Alert currently being completed

  // Follow up logging states
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [muac, setMuac] = useState("");
  const [hemoglobin, setHemoglobin] = useState("");
  const [dietaryHabits, setDietaryHabits] = useState("Adequate");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/alerts`, {
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
        
        // Fetch child name and village details for each alert
        const enrichedAlerts = await Promise.all(
          json.map(async alert => {
            try {
              const childRes = await fetch(`${API_URL}/api/children/${alert.child_id}`, {
                headers: {
                  "Authorization": `Bearer ${token}`
                }
              });
              if (childRes.status === 401) {
                onUnauthorized();
                return null;
              }
              if (childRes.ok) {
                const childData = await childRes.json();
                return {
                  ...alert,
                  child_name: childData.name,
                  gender: childData.gender,
                  age_months: childData.age_months,
                  village: childData.village,
                  status: childData.records[childData.records.length - 1]?.status || "Malnourished"
                };
              }
            } catch (e) {
              console.error(e);
            }
            return { ...alert, child_name: `Child #${alert.child_id}`, village: "Unknown", status: "Moderate/Severe" };
          })
        );

        // Filter out null values in case unauthorized was triggered
        setAlerts(enrichedAlerts.filter(a => a !== null));
      }
    } catch (e) {
      console.error("Error fetching alerts:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleCompleteCheckup = async (e) => {
    e.preventDefault();
    if (!weight || !height || !muac) {
      alert("Weight, Height, and MUAC are required to log progress.");
      return;
    }

    setSubmitting(true);
    try {
      // Step 1: Add new health record
      const formData = new FormData();
      formData.append("weight_kg", parseFloat(weight));
      formData.append("height_cm", parseFloat(height));
      formData.append("muac_cm", parseFloat(muac));
      if (hemoglobin) {
        formData.append("hemoglobin_gdl", parseFloat(hemoglobin));
      }
      formData.append("dietary_habits", dietaryHabits);

      const recordRes = await fetch(`${API_URL}/api/children/${activeAlert.child_id}/records`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      });

      if (recordRes.status === 401) {
        onUnauthorized();
        return;
      }

      if (!recordRes.ok) {
        throw new Error("Failed to log new measurements");
      }

      // Step 2: Complete the alert in DB
      const alertForm = new FormData();
      if (notes) {
        alertForm.append("notes", notes);
      }
      
      const alertRes = await fetch(`${API_URL}/api/alerts/${activeAlert.id}/complete`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: alertForm
      });

      if (alertRes.status === 401) {
        onUnauthorized();
        return;
      }

      if (alertRes.ok) {
        setActiveAlert(null);
        setWeight("");
        setHeight("");
        setMuac("");
        setHemoglobin("");
        setNotes("");
        fetchAlerts(); // refresh alert list
      } else {
        alert("Failed to close follow-up task.");
      }

    } catch (err) {
      console.error(err);
      alert(err.message || "An error occurred.");
    } finally {
      setSubmitting(false);
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

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <AlertTriangle color="var(--status-severe-text)" className="pulse-severe" />
        {t.followups}
      </h2>

      {/* Complete Checkup Inline Form */}
      {activeAlert && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '30px', borderStyle: 'solid', animation: 'fadeIn 0.3s ease' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 'bold' }}>
              Perform Check-up for {activeAlert.child_name}
            </h3>
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={() => setActiveAlert(null)}>
              Cancel
            </button>
          </div>

          <form onSubmit={handleCompleteCheckup}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '14px', marginBottom: '16px' }}>
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

            <div className="form-group" style={{ marginBottom: '20px' }}>
              <label>{t.notes}</label>
              <textarea 
                className="form-control" 
                rows="2" 
                value={notes} 
                onChange={(e) => setNotes(e.target.value)} 
                placeholder="Log dietary changes, referral information, or health notes..."
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button type="submit" className="btn" disabled={submitting}>
                {submitting ? "Saving Check-up..." : t.save}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Active Alerts List */}
      {alerts.length === 0 ? (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
          <CheckCircle size={48} color="#10b981" style={{ margin: '0 auto 16px auto' }} />
          <p style={{ color: 'var(--text-muted)' }}>{t.no_alerts}</p>
        </div>
      ) : (
        <div className="alert-list">
          {alerts.map(alert => {
            const scheduled = new Date(alert.scheduled_date);
            const isOverdue = scheduled < new Date();

            return (
              <div key={alert.id} className="glass-panel alert-item" style={{ borderLeft: `4px solid ${isOverdue ? 'var(--status-severe-text)' : 'var(--status-moderate-text)'}` }}>
                <div className="alert-details">
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 'bold' }}>{alert.child_name}</h3>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {alert.gender === "Male" ? t.male : t.female} &bull; {alert.age_months.toFixed(0)}m &bull; {alert.village}
                  </span>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '10px' }}>
                    <span className={`status-badge ${alert.status === 'Severe Malnutrition' ? 'severe' : 'moderate'}`} style={{ fontSize: '0.75rem', padding: '2px 8px' }}>
                      {alert.status === 'Severe Malnutrition' ? t.severe : t.moderate}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: isOverdue ? 'var(--status-severe-text)' : 'var(--text-muted)' }}>
                      <Calendar size={14} />
                      <span>Scheduled: {scheduled.toLocaleDateString()} {isOverdue && "(OVERDUE)"}</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                  <button className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: '0.85rem' }} onClick={() => onViewChild(alert.child_id)}>
                    Profile
                  </button>
                  <button className="btn" style={{ padding: '8px 14px', fontSize: '0.85rem' }} onClick={() => setActiveAlert(alert)}>
                    <Clipboard size={14} /> {t.complete}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
