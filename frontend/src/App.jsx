import React, { useState, useEffect } from "react";
import { translations } from "./i18n/i18n";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import DataEntryForm from "./components/DataEntryForm";
import ChildDetails from "./components/ChildDetails";
import AlertsPanel from "./components/AlertsPanel";
import AuthPage from "./components/AuthPage";
import { auth } from "./firebase";
import { PrivacyPolicyModal, TermsOfServiceModal, ContactSupportModal } from "./components/LegalModals";
import { LayoutDashboard, UserPlus, AlertCircle, Search, Globe, ChevronRight, HeartHandshake, LogOut } from "lucide-react";
import API_URL from "./api";

export default function App() {
  const [language, setLanguage] = useState("en");
  const [activeView, setActiveView] = useState("dashboard");
  const [selectedChildId, setSelectedChildId] = useState(null);

  // Auth states
  const [token, setToken] = useState(localStorage.getItem("poshanai_token"));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("poshanai_user");
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Modal states
  const [showPrivacy, setShowPrivacy] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const [showContact, setShowContact] = useState(false);
  
  // Children list for quick-search
  const [children, setChildren] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  const t = translations[language] || translations["en"];

  const handleLogin = (newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    setActiveView("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("poshanai_token");
    localStorage.removeItem("poshanai_user");
    setToken(null);
    setUser(null);
    auth.signOut().catch(console.error);
  };

  // Validate token on mount / token change
  useEffect(() => {
    const validateToken = async () => {
      if (!token) return;
      try {
        const res = await fetch(`${API_URL}/api/auth/me`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        if (res.status === 401) {
          console.warn("Session expired or invalid token.");
          handleLogout();
        } else if (res.ok) {
          const userData = await res.json();
          setUser(userData);
          localStorage.setItem("poshanai_user", JSON.stringify(userData));
        } else {
          console.error("Failed to sync profile. Backend might be down.");
        }
      } catch (err) {
        console.error("Token validation failed (connectivity issue):", err);
      }
    };
    validateToken();
  }, [token]);

  const fetchChildren = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_URL}/api/children`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (res.status === 401) {
        handleLogout();
        return;
      }
      if (res.ok) {
        const data = await res.json();
        setChildren(data);
      }
    } catch (e) {
      console.error("Error fetching children list:", e);
    }
  };

  useEffect(() => {
    fetchChildren();
  }, [activeView, token]); // Re-fetch whenever view or token changes

  // Filter children based on search query
  const filteredChildren = searchQuery.trim() === "" 
    ? [] 
    : children.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleSelectChild = (id) => {
    setSelectedChildId(id);
    setActiveView("child-details");
    setSearchQuery(""); // Clear search
  };

  // Gate app access with AuthPage if not authenticated
  if (!token) {
    return <AuthPage onLogin={handleLogin} />;
  }

  return (
    <>
      {/* Legal / Support Modals */}
      {showPrivacy  && <PrivacyPolicyModal   onClose={() => setShowPrivacy(false)}  />}
      {showTerms   && <TermsOfServiceModal   onClose={() => setShowTerms(false)}   />}
      {showContact && <ContactSupportModal   onClose={() => setShowContact(false)} />}

      <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar" style={{ display: 'flex', flexDirection: 'column' }}>
        <div>
          <div className="sidebar-logo">
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--primary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', fontWeight: 'bold' }}>
              ⚕️
            </div>
            <h1>PoshanAI</h1>
          </div>

          {/* User Profile display */}
          {user && (
            <div style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', marginBottom: '20px', border: '1px solid var(--card-border)' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#fff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                👤 {user.full_name}
              </div>
              {user.center_name && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  🏢 {user.center_name}
                </div>
              )}
            </div>
          )}

          {/* Sidebar Search Bar */}
          <div style={{ position: 'relative', marginBottom: '24px' }}>
            <div style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-muted)' }}>
              <Search size={16} />
            </div>
            <input 
              type="text" 
              placeholder={t.search_child} 
              className="form-control"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '36px', fontSize: '0.85rem', width: '100%', height: '38px' }}
            />

            {/* Search Dropdown list */}
            {filteredChildren.length > 0 && (
              <div style={{ position: 'absolute', top: '42px', left: 0, right: 0, background: '#1e293b', border: '1px solid var(--card-border)', borderRadius: '8px', zIndex: 110, maxHeight: '200px', overflowY: 'auto', boxShadow: '0 10px 25px rgba(0,0,0,0.3)' }}>
                {filteredChildren.map(c => (
                  <div 
                    key={c.id} 
                    onClick={() => handleSelectChild(c.id)}
                    style={{ padding: '10px 14px', cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.03)', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.05)'}
                    onMouseLeave={(e) => e.target.style.background = 'transparent'}
                  >
                    <span>{c.name}</span>
                    <ChevronRight size={14} color="var(--text-muted)" />
                  </div>
                ))}
              </div>
            )}
          </div>

          <ul className="sidebar-menu">
            <li 
              className={`sidebar-item ${activeView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveView("dashboard")}
            >
              <LayoutDashboard size={20} />
              <span>{t.dashboard}</span>
            </li>
            <li 
              className={`sidebar-item ${activeView === 'register' ? 'active' : ''}`}
              onClick={() => setActiveView("register")}
            >
              <UserPlus size={20} />
              <span>{t.register}</span>
            </li>
            <li 
              className={`sidebar-item ${activeView === 'alerts' ? 'active' : ''}`}
              onClick={() => setActiveView("alerts")}
            >
              <AlertCircle size={20} />
              <span>{t.alerts}</span>
            </li>
          </ul>
        </div>

        {/* Bottom portion of sidebar */}
        <div style={{ marginTop: 'auto' }}>
          <div 
            className="sidebar-item"
            onClick={handleLogout}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '10px 16px', 
              borderRadius: '8px', 
              cursor: 'pointer', 
              color: '#f87171', 
              marginBottom: '20px', 
              transition: 'background 0.2s ease' 
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
          >
            <LogOut size={20} />
            <span>Sign Out</span>
          </div>

          {/* Footer info in sidebar */}
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', borderTop: '1px solid var(--card-border)', paddingTop: '16px' }}>
            <div>Poshan Abhiyaan Helper</div>
            <div style={{ marginTop: '4px', opacity: 0.7 }}>Powered by Scikit-Learn & OpenCV</div>
          </div>
        </div>
      </aside>

      {/* Main Panel Content Area */}
      <main className="main-content">
        {/* Top Navbar Header */}
        <header className="header">
          <div className="header-title-container">
            <h2>{t.title}</h2>
            <p>{t.subtitle}</p>
          </div>

          <div className="header-actions">
            {/* Language Selector Dropdown */}
            <div className="lang-selector-container">
              <Globe size={16} color="var(--primary-color)" />
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{t.language}:</span>
              <select 
                className="lang-select" 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="te">తెలుగు (Telugu)</option>
                <option value="ta">தமிழ் (Tamil)</option>
              </select>
            </div>
          </div>
        </header>

        {/* Dynamic Route Content */}
        <div className="page-content">
          {activeView === "dashboard" && (
            <AnalyticsDashboard 
              t={t} 
              onViewChild={handleSelectChild} 
              token={token}
              onUnauthorized={handleLogout}
            />
          )}

          {activeView === "register" && (
            <DataEntryForm 
              t={t} 
              onChildCreated={handleSelectChild} 
              token={token}
              onUnauthorized={handleLogout}
            />
          )}

          {activeView === "alerts" && (
            <AlertsPanel 
              t={t} 
              onViewChild={handleSelectChild} 
              token={token}
              onUnauthorized={handleLogout}
            />
          )}

          {activeView === "child-details" && (
            <ChildDetails 
              t={t} 
              childId={selectedChildId} 
              onBack={() => setActiveView("dashboard")} 
              token={token}
              onUnauthorized={handleLogout}
            />
          )}
        </div>

        {/* Copyright Footer */}
        <footer className="app-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HeartHandshake size={15} color="var(--primary-color)" />
            <span>
              &copy; {new Date().getFullYear()} <strong style={{ color: 'var(--text-primary)' }}>PoshanAI</strong>. All rights reserved.
            </span>
          </div>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <FooterLink onClick={() => setShowPrivacy(true)}>Privacy Policy</FooterLink>
            <span style={{ opacity: 0.3, fontSize: '0.7rem' }}>|</span>
            <FooterLink onClick={() => setShowTerms(true)}>Terms of Service</FooterLink>
            <span style={{ opacity: 0.3, fontSize: '0.7rem' }}>|</span>
            <FooterLink onClick={() => setShowContact(true)}>Contact Support</FooterLink>
            <span style={{ opacity: 0.3, fontSize: '0.7rem' }}>|</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Built for <strong style={{ color: '#a78bfa' }}>Anganwadi &amp; ICDS</strong> workers across India</span>
          </div>
        </footer>
      </main>
      </div>
    </>
  );
}

function FooterLink({ onClick, children }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: 'none', border: 'none', cursor: 'pointer',
        color: 'var(--text-muted)', fontSize: '0.75rem',
        padding: '2px 0', transition: 'color 0.2s ease',
        textDecoration: 'underline', textDecorationColor: 'transparent',
        textUnderlineOffset: '3px'
      }}
      onMouseEnter={(e) => { e.currentTarget.style.color = '#a5b4fc'; e.currentTarget.style.textDecorationColor = '#a5b4fc'; }}
      onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.textDecorationColor = 'transparent'; }}
    >
      {children}
    </button>
  );
}
