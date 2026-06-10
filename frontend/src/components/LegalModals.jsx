import React from "react";
import Modal from "./Modal";

export function PrivacyPolicyModal({ onClose }) {
  return (
    <Modal title="Privacy Policy" icon="🔒" onClose={onClose}>
      <p style={{ color: "#94a3b8", fontSize: "0.82rem", marginBottom: "20px" }}>
        Last updated: June 2026 &nbsp;·&nbsp; Effective immediately
      </p>

      <Section title="1. Introduction">
        PoshanAI ("we", "our", "us") is an AI-powered child malnutrition detection system developed
        to support Anganwadi workers, NGOs, healthcare workers, and government agencies across India.
        We are committed to protecting the privacy of all individuals whose data is collected through
        this platform, including children, parents/guardians, and healthcare workers.
      </Section>

      <Section title="2. Information We Collect">
        We collect the following categories of information for the sole purpose of malnutrition
        detection and nutritional guidance:
        <ul style={{ marginTop: "10px", paddingLeft: "20px", display: "flex", flexDirection: "column", gap: "6px" }}>
          <li><strong style={{ color: "#e2e8f0" }}>Child Profile Data:</strong> Name, age, gender, village, district, and state.</li>
          <li><strong style={{ color: "#e2e8f0" }}>Health Measurements:</strong> Weight, height, MUAC, hemoglobin levels, and dietary habits.</li>
          <li><strong style={{ color: "#e2e8f0" }}>Optional Photographs:</strong> Child photographs used only for AI-based visual malnutrition assessment.</li>
          <li><strong style={{ color: "#e2e8f0" }}>Family Information:</strong> Family income category for nutritional scheme eligibility matching.</li>
        </ul>
      </Section>

      <Section title="3. How We Use Your Data">
        All collected data is used exclusively for:
        <ul style={{ marginTop: "10px", paddingLeft: "20px", display: "flex", flexDirection: "column", gap: "6px" }}>
          <li>AI-based malnutrition classification (Normal / MAM / SAM)</li>
          <li>WHO Z-score growth tracking and chart generation</li>
          <li>Personalised dietary recommendations based on region and age</li>
          <li>Government nutrition scheme eligibility determination (ICDS, POSHAN Abhiyaan)</li>
          <li>Aggregate, anonymised analytics for public health reporting</li>
        </ul>
        <p style={{ marginTop: "12px" }}>
          We do <strong style={{ color: "#f87171" }}>not</strong> sell, rent, or share individual child
          data with third parties for commercial purposes.
        </p>
      </Section>

      <Section title="4. Data Storage & Security">
        All data is stored in a secured database. Health records and photographs are accessible
        only to authorised healthcare workers registered on the platform. We implement
        industry-standard encryption and access controls to protect sensitive health information.
      </Section>

      <Section title="5. Children's Privacy">
        This platform is designed specifically to handle data related to children under 5 years of
        age for healthcare purposes. All data is treated with the highest sensitivity under applicable
        Indian data protection regulations and the DPDP Act 2023.
      </Section>

      <Section title="6. Data Retention">
        Child health records are retained for a minimum of 5 years to enable longitudinal growth
        tracking. You may request deletion of a child's record by contacting your local Anganwadi
        supervisor or our support team.
      </Section>

      <Section title="7. Contact">
        For privacy-related queries, please contact us at{" "}
        <a href="mailto:luffy67mon@gmail.com" style={{ color: "#818cf8" }}>luffy67mon@gmail.com</a>.
      </Section>
    </Modal>
  );
}

export function TermsOfServiceModal({ onClose }) {
  return (
    <Modal title="Terms of Service" icon="📋" onClose={onClose}>
      <p style={{ color: "#94a3b8", fontSize: "0.82rem", marginBottom: "20px" }}>
        Last updated: June 2026 &nbsp;·&nbsp; Please read these terms carefully before using PoshanAI.
      </p>

      <Section title="1. Acceptance of Terms">
        By accessing or using the PoshanAI platform, you agree to be bound by these Terms of Service.
        If you do not agree to these terms, please discontinue use of the platform immediately.
      </Section>

      <Section title="2. Intended Use">
        PoshanAI is intended for use by:
        <ul style={{ marginTop: "10px", paddingLeft: "20px", display: "flex", flexDirection: "column", gap: "6px" }}>
          <li>Authorised Anganwadi workers and supervisors</li>
          <li>Government health department officials</li>
          <li>Registered NGOs and healthcare organisations</li>
          <li>Public health researchers (with appropriate data access approval)</li>
        </ul>
        Unauthorised access or use of this system for any purpose other than child health monitoring
        is strictly prohibited.
      </Section>

      <Section title="3. Medical Disclaimer">
        <span style={{ color: "#fbbf24", fontWeight: "600" }}>⚠️ Important: </span>
        PoshanAI provides AI-assisted malnutrition screening and nutritional guidance.
        It is <strong style={{ color: "#f87171" }}>not a substitute</strong> for professional medical
        diagnosis, treatment, or clinical advice. All AI predictions must be reviewed and validated
        by a qualified healthcare professional before any medical decision is made.
      </Section>

      <Section title="4. Data Accuracy">
        Users are responsible for entering accurate child health measurements. PoshanAI's AI
        classification accuracy depends directly on the correctness of input data. Inaccurate or
        falsified entries may result in incorrect recommendations and are the sole responsibility
        of the entering user.
      </Section>

      <Section title="5. Intellectual Property">
        All software, AI models, design assets, and content on this platform are the intellectual
        property of PoshanAI and its developers. Unauthorised reproduction, distribution, or reverse
        engineering of any component is prohibited.
      </Section>

      <Section title="6. Limitation of Liability">
        PoshanAI and its developers shall not be liable for any indirect, incidental, or consequential
        damages arising from use of the platform, including but not limited to misclassification of
        nutritional status or reliance on AI-generated dietary recommendations without clinical review.
      </Section>

      <Section title="7. Modifications">
        We reserve the right to modify these Terms at any time. Continued use of the platform after
        changes constitutes acceptance of the revised Terms.
      </Section>

      <Section title="8. Governing Law">
        These Terms are governed by the laws of India. Any disputes shall be subject to the
        jurisdiction of courts in New Delhi, India.
      </Section>
    </Modal>
  );
}

export function ContactSupportModal({ onClose }) {
  return (
    <Modal title="Contact Support" icon="🤝" onClose={onClose}>
      <p style={{ color: "#94a3b8", marginBottom: "24px" }}>
        Our team is here to help Anganwadi workers, healthcare officials, and NGOs get the most
        out of PoshanAI. Reach us through any of the channels below.
      </p>

      {/* Contact Cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "28px" }}>
        <ContactCard
          emoji="📧"
          label="Email Support"
          value="luffy67mon@gmail.com"
          href="mailto:luffy67mon@gmail.com"
          subtext="Response within 24 hours (Mon–Fri)"
          color="#6366f1"
        />
        <ContactCard
          emoji="📞"
          label="Helpline (Toll-Free)"
          value="1800-XXX-XXXX"
          href="tel:1800XXXXXXX"
          subtext="Available 9 AM – 6 PM, Monday to Saturday"
          color="#a855f7"
        />
        <ContactCard
          emoji="🌐"
          label="Official Website"
          value="www.poshanai.in"
          href="https://poshanai.in"
          subtext="Documentation, user guides & release notes"
          color="#06b6d4"
        />
        <ContactCard
          emoji="📍"
          label="Nodal Office"
          value="Ministry of Women & Child Development"
          subtext="Shastri Bhavan, New Delhi – 110 001, India"
          color="#10b981"
        />
      </div>

      <div style={{
        background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.2)",
        borderRadius: "12px", padding: "18px 20px"
      }}>
        <p style={{ fontWeight: "600", color: "#a5b4fc", marginBottom: "8px", fontSize: "0.9rem" }}>
          📌 For Anganwadi Workers
        </p>
        <p style={{ color: "#94a3b8", fontSize: "0.87rem", lineHeight: "1.7" }}>
          If you are an Anganwadi worker experiencing issues with the app, please first contact
          your <strong style={{ color: "#e2e8f0" }}>CDPO (Child Development Project Officer)</strong>{" "}
          or your district-level ICDS supervisor. They have direct access to our technical support
          channel and can escalate on your behalf.
        </p>
      </div>

      <div style={{ marginTop: "20px", padding: "16px 20px", background: "rgba(16,185,129,0.07)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: "12px" }}>
        <p style={{ fontWeight: "600", color: "#34d399", marginBottom: "6px", fontSize: "0.9rem" }}>
          ⚡ Report a Bug or Data Issue
        </p>
        <p style={{ color: "#94a3b8", fontSize: "0.87rem" }}>
          Found an incorrect classification or data sync issue? Email{" "}
          <a href="mailto:bugs@poshanai.in" style={{ color: "#818cf8" }}>bugs@poshanai.in</a>{" "}
          with the Child ID and a screenshot. We typically resolve critical issues within 48 hours.
        </p>
      </div>
    </Modal>
  );
}

// ── Internal helpers ─────────────────────────────────────────────────────────

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: "22px" }}>
      <h3 style={{
        fontSize: "0.95rem", fontWeight: "700", color: "#e2e8f0",
        marginBottom: "8px", paddingBottom: "6px",
        borderBottom: "1px solid rgba(255,255,255,0.06)"
      }}>
        {title}
      </h3>
      <div style={{ color: "#94a3b8", lineHeight: "1.75" }}>{children}</div>
    </div>
  );
}

function ContactCard({ emoji, label, value, href, subtext, color }) {
  return (
    <div style={{
      display: "flex", alignItems: "flex-start", gap: "16px",
      padding: "16px 18px",
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.07)",
      borderRadius: "12px",
      transition: "all 0.2s ease"
    }}>
      <div style={{
        width: "42px", height: "42px", borderRadius: "10px", flexShrink: 0,
        background: `${color}18`, border: `1px solid ${color}30`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: "1.2rem"
      }}>
        {emoji}
      </div>
      <div>
        <div style={{ fontSize: "0.78rem", color: "#64748b", marginBottom: "3px", textTransform: "uppercase", letterSpacing: "0.5px" }}>{label}</div>
        {href ? (
          <a href={href} style={{ color: "#e2e8f0", fontWeight: "600", fontSize: "0.97rem", textDecoration: "none" }}
            onMouseEnter={(e) => e.target.style.color = color}
            onMouseLeave={(e) => e.target.style.color = "#e2e8f0"}
          >
            {value}
          </a>
        ) : (
          <div style={{ color: "#e2e8f0", fontWeight: "600", fontSize: "0.97rem" }}>{value}</div>
        )}
        {subtext && <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "3px" }}>{subtext}</div>}
      </div>
    </div>
  );
}
