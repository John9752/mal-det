import React, { useState } from "react";
import { Camera, FileText, MapPin, Activity, CheckCircle, RefreshCw } from "lucide-react";
import API_URL from "../api";

export default function DataEntryForm({ t, onChildCreated, token, onUnauthorized }) {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  // Form states
  const [name, setName] = useState("");
  const [ageMonths, setAgeMonths] = useState("");
  const [gender, setGender] = useState("Male");
  const [familyIncome, setFamilyIncome] = useState("Low");
  const [village, setVillage] = useState("");
  const [district, setDistrict] = useState("");
  const [state, setState] = useState("");
  
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [muac, setMuac] = useState("");
  const [hemoglobin, setHemoglobin] = useState("");
  const [dietaryHabits, setDietaryHabits] = useState("Adequate");
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const validateStep1 = () => {
    return name && ageMonths && gender && familyIncome && village && district && state;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep1() || !weight || !height || !muac) {
      alert("Please fill in all required fields.");
      return;
    }

    setSubmitting(true);

    try {
      // Step 1: Create child profile
      const childRes = await fetch(`${API_URL}/api/children`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          name,
          gender,
          age_months: parseFloat(ageMonths),
          family_income: familyIncome,
          village,
          district,
          state
        })
      });

      if (childRes.status === 401) {
        onUnauthorized();
        return;
      }

      if (!childRes.ok) {
        throw new Error("Failed to register child profile.");
      }

      const newChild = await childRes.json();
      const childId = newChild.id;

      // Step 2: Upload measurements & optional photo
      const formData = new FormData();
      formData.append("weight_kg", parseFloat(weight));
      formData.append("height_cm", parseFloat(height));
      formData.append("muac_cm", parseFloat(muac));
      if (hemoglobin) {
        formData.append("hemoglobin_gdl", parseFloat(hemoglobin));
      }
      formData.append("dietary_habits", dietaryHabits);
      if (photo) {
        formData.append("image", photo);
      }

      const recordRes = await fetch(`${API_URL}/api/children/${childId}/records`, {
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
        throw new Error("Failed to submit health measurements.");
      }

      const newRecord = await recordRes.json();
      setResult({ childId, record: newRecord });
      setStep(3);

    } catch (err) {
      console.error(err);
      alert(err.message || "An error occurred during registration.");
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setName("");
    setAgeMonths("");
    setGender("Male");
    setFamilyIncome("Low");
    setVillage("");
    setDistrict("");
    setState("");
    setWeight("");
    setHeight("");
    setMuac("");
    setHemoglobin("");
    setDietaryHabits("Adequate");
    setPhoto(null);
    setPhotoPreview(null);
    setResult(null);
    setStep(1);
  };

  return (
    <div className="glass-panel form-wizard-card">
      {/* Wizard Header Progress */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px', position: 'relative' }}>
        <div style={{ position: 'absolute', top: '15px', left: '10%', right: '10%', height: '2px', background: 'var(--card-border)', zorder: -1 }} />
        <div style={{ position: 'absolute', top: '15px', left: '10%', width: step === 1 ? '0%' : (step === 2 ? '40%' : '80%'), height: '2px', background: 'var(--primary-color)', zorder: -1, transition: 'var(--transition-smooth)' }} />

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', zIndex: 2 }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '16px', background: step >= 1 ? 'var(--primary-gradient)' : 'var(--card-bg)', border: '2px solid var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>1</div>
          <span style={{ fontSize: '0.8rem', color: step >= 1 ? '#fff' : 'var(--text-muted)' }}>Profile</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', zIndex: 2 }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '16px', background: step >= 2 ? 'var(--primary-gradient)' : 'var(--card-bg)', border: `2px solid ${step >= 2 ? 'var(--primary-color)' : 'var(--card-border)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>2</div>
          <span style={{ fontSize: '0.8rem', color: step >= 2 ? '#fff' : 'var(--text-muted)' }}>Metrics</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', zIndex: 2 }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '16px', background: step >= 3 ? 'var(--primary-gradient)' : 'var(--card-bg)', border: `2px solid ${step >= 3 ? 'var(--primary-color)' : 'var(--card-border)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>3</div>
          <span style={{ fontSize: '0.8rem', color: step >= 3 ? '#fff' : 'var(--text-muted)' }}>Result</span>
        </div>
      </div>

      {step === 1 && (
        <div className="fade-in">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText color="var(--primary-color)" /> Child Profile Details
          </h3>
          <div className="form-grid">
            <div className="form-group">
              <label>{t.name} *</label>
              <input type="text" className="form-control" value={name} onChange={(e) => setName(e.target.value)} placeholder="Full Name" required />
            </div>

            <div className="form-group">
              <label>{t.age} *</label>
              <input type="number" className="form-control" value={ageMonths} onChange={(e) => setAgeMonths(e.target.value)} placeholder="0 - 60 months" min="0" max="60" required />
            </div>

            <div className="form-group">
              <label>{t.gender} *</label>
              <select className="form-control" value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="Male">{t.male}</option>
                <option value="Female">{t.female}</option>
              </select>
            </div>

            <div className="form-group">
              <label>{t.income} *</label>
              <select className="form-control" value={familyIncome} onChange={(e) => setFamilyIncome(e.target.value)}>
                <option value="Low">{t.low}</option>
                <option value="Medium">{t.medium}</option>
                <option value="High">{t.high}</option>
              </select>
            </div>

            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><MapPin size={16} /> Location</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginTop: '4px' }}>
                <input type="text" className="form-control" value={village} onChange={(e) => setVillage(e.target.value)} placeholder={t.village} required />
                <input type="text" className="form-control" value={district} onChange={(e) => setDistrict(e.target.value)} placeholder={t.district} required />
                <input type="text" className="form-control" value={state} onChange={(e) => setState(e.target.value)} placeholder={t.state} required />
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '30px' }}>
            <button className="btn" onClick={() => setStep(2)} disabled={!validateStep1()}>
              Next Step
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="fade-in">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Activity color="var(--secondary-color)" /> Physical Measurements
          </h3>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label>{t.weight} *</label>
                <input type="number" step="0.01" className="form-control" value={weight} onChange={(e) => setWeight(e.target.value)} placeholder="e.g. 8.5" required />
              </div>

              <div className="form-group">
                <label>{t.height} *</label>
                <input type="number" step="0.1" className="form-control" value={height} onChange={(e) => setHeight(e.target.value)} placeholder="e.g. 74.5" required />
              </div>

              <div className="form-group">
                <label>{t.muac} *</label>
                <input type="number" step="0.1" className="form-control" value={muac} onChange={(e) => setMuac(e.target.value)} placeholder="e.g. 12.2" required />
              </div>

              <div className="form-group">
                <label>{t.hemoglobin}</label>
                <input type="number" step="0.1" className="form-control" value={hemoglobin} onChange={(e) => setHemoglobin(e.target.value)} placeholder="e.g. 10.5" />
              </div>

              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label>{t.diet} *</label>
                <select className="form-control" value={dietaryHabits} onChange={(e) => setDietaryHabits(e.target.value)}>
                  <option value="Poor">{t.poor}</option>
                  <option value="Adequate">{t.adequate}</option>
                  <option value="Good">{t.good}</option>
                </select>
              </div>

              {/* Photo Input section */}
              <div className="photo-upload-section" onClick={() => document.getElementById("photoFile").click()}>
                <input type="file" id="photoFile" accept="image/*" onChange={handlePhotoChange} style={{ display: 'none' }} />
                {photoPreview ? (
                  <>
                    <img src={photoPreview} alt="Preview" className="photo-upload-preview" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Click to replace photo</span>
                  </>
                ) : (
                  <>
                    <Camera size={36} color="var(--text-muted)" />
                    <div style={{ textAlign: 'center' }}>
                      <h5 style={{ fontWeight: '600' }}>{t.photo}</h5>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Upload child photo for visual wasting checks</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '30px' }}>
              <button type="button" className="btn btn-secondary" onClick={() => setStep(1)}>
                Back
              </button>
              <button type="submit" className="btn" disabled={submitting}>
                {submitting ? (
                  <>
                    <RefreshCw className="pulse-severe" size={18} style={{ animation: 'spin 1s linear infinite' }} />
                    {t.loading}
                  </>
                ) : (
                  t.submit
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {step === 3 && result && (
        <div className="fade-in" style={{ textAlign: 'center', padding: '10px 0' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '32px', background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px auto' }}>
            <CheckCircle size={36} />
          </div>

          <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '8px' }}>Analysis Complete</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '30px' }}>Child health measurements successfully recorded and analyzed by AI.</p>

          <div className="glass-panel" style={{ padding: '24px', maxWidth: '400px', margin: '0 auto 30px auto', borderStyle: 'solid' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t.name}</span>
              <span style={{ fontWeight: 'bold' }}>{name}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t.status}</span>
              <span className={`status-badge ${result.record.status === 'Normal' ? 'normal' : (result.record.status === 'Mild Malnutrition' ? 'mild' : (result.record.status === 'Moderate Malnutrition' ? 'moderate' : 'severe'))}`}>
                {result.record.status === 'Normal' ? t.normal : (result.record.status === 'Mild Malnutrition' ? t.mild : (result.record.status === 'Moderate Malnutrition' ? t.moderate : t.severe))}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t.risk_score}</span>
              <span style={{ fontWeight: 'bold', color: 'var(--primary-color)' }}>{result.record.risk_score}%</span>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
            <button className="btn btn-secondary" onClick={resetForm}>
              Register Another Child
            </button>
            <button className="btn" onClick={() => onChildCreated(result.childId)}>
              {t.view_details}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
