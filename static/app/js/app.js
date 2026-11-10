/**
 * Utkal Hospital & Medical Research Centre - Core Application Engine
 * Integrates with FastAPI RESTful API endpoints at /api/v1
 * Complete Role-Based Access Control (Admin, Doctor, Receptionist, Patient)
 * All Indian Doctors, Indian Patients, Rupees (₹ INR), and Live Interactive Telemetry
 */

const API_BASE = '/api/v1';

// Format Indian Currency (₹)
function formatINR(val) {
  const num = Number(val || 0);
  return '₹' + num.toLocaleString('en-IN', {
    maximumFractionDigits: 2,
    minimumFractionDigits: Number.isInteger(num) ? 0 : 2
  });
}

// Global Application State
const appState = {
  token: localStorage.getItem('medflow_token') || '',
  user: JSON.parse(localStorage.getItem('medflow_user') || 'null') || {
    id: 1,
    full_name: 'Hospital Administrator',
    email: 'admin@hospital.com',
    role: 'admin'
  },
  currentPage: 'dashboard',
  hospitalSettings: JSON.parse(localStorage.getItem('utkal_hospital_branding') || 'null') || {
    name: 'Utkal Hospital & Medical Research Centre',
    shortName: 'Utkal Hospital',
    subtitle: 'Premier Multi-Specialty Tertiary Care & Research Institute',
    address: 'Niladri Vihar, Chandrasekharpur, Bhubaneswar, Odisha 751021',
    phone: '+91 674 274 0100 / 1800 120 8855',
    email: 'contact@utkalhospital.com',
  },
  patients: [],
  doctors: [],
  appointments: [],
  prescriptions: [],
  labTests: [],
  invoices: [],
  medicines: [],
};

// Toast Notification
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span style="font-size:16px;">${type === 'success' ? '✓' : (type === 'error' ? '✕' : '⚠')}</span>
    <span style="flex:1;">${message}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Apply Dynamic Hospital Branding Across the Entire App
function applyHospitalBranding() {
  const s = appState.hospitalSettings;
  const brandNameEl = document.getElementById('brandHospitalName');
  const brandSubEl = document.getElementById('brandHospitalSubtitle');
  const navHospEl = document.getElementById('navHospitalName');
  const bannerHospEl = document.getElementById('bannerHospitalName');
  
  if (brandNameEl) brandNameEl.innerText = s.shortName || s.name;
  if (brandSubEl) brandSubEl.innerText = s.subtitle;
  if (navHospEl) navHospEl.innerText = s.shortName || s.name;
  if (bannerHospEl) bannerHospEl.innerText = s.name;
  document.title = `${s.name} | Hospital & Clinic Management System`;

  // Pre-fill settings form
  const inpName = document.getElementById('settingHospitalNameInput');
  const inpSub = document.getElementById('settingHospitalSubtitleInput');
  const inpAddr = document.getElementById('settingHospitalAddressInput');
  const inpPhone = document.getElementById('settingHospitalPhoneInput');
  const inpEmail = document.getElementById('settingHospitalEmailInput');

  if (inpName) inpName.value = s.name;
  if (inpSub) inpSub.value = s.subtitle;
  if (inpAddr) inpAddr.value = s.address;
  if (inpPhone) inpPhone.value = s.phone;
  if (inpEmail) inpEmail.value = s.email;
}

// API Helper with Token Handling
async function apiRequest(endpoint, method = 'GET', body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (appState.token) {
    headers['Authorization'] = `Bearer ${appState.token}`;
  }

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (res.status === 401 && !endpoint.includes('/auth/login')) {
      // Re-prompt login or try with stored token
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Session expired. Please sign in again.');
    }

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || `HTTP Error ${res.status}`);
    }
    return data;
  } catch (err) {
    console.warn(`API call error on ${endpoint}:`, err);
    throw err;
  }
}

// Navigation Tab Switcher
function switchPage(pageId) {
  // Access control guard
  if (appState.user && appState.user.role === 'patient') {
    if (['patients', 'doctors', 'pharmacy'].includes(pageId)) {
      showToast('Access restricted: Patients can only view personal health modules.', 'warning');
      pageId = 'dashboard';
    }
  }

  appState.currentPage = pageId;
  document.querySelectorAll('.page-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  const activePage = document.getElementById(`page-${pageId}`);
  const activeNav = document.getElementById(`nav-${pageId}`);
  if (activePage) activePage.classList.add('active');
  if (activeNav) activeNav.classList.add('active');

  // Load appropriate data
  if (pageId === 'dashboard') loadDashboardData();
  else if (pageId === 'patients') loadPatientsData();
  else if (pageId === 'doctors') loadDoctorsData();
  else if (pageId === 'appointments') loadAppointmentsData();
  else if (pageId === 'prescriptions') loadPrescriptionsData();
  else if (pageId === 'lab-reports') loadLabReportsData();
  else if (pageId === 'billing') loadBillingData();
  else if (pageId === 'pharmacy') loadPharmacyData();
  else if (pageId === 'settings') loadSettingsData();
}

// ================= ROLE-BASED ACCESS CONTROL (RBAC) & LOGIN GATE =================

const USER_PRESETS = {
  admin: { email: 'admin@hospital.com', pwd: 'admin123', label: 'Admin (Medical Superintendent)', roleName: 'Admin' },
  doctor: { email: 'doctor@hospital.com', pwd: 'doctor123', label: 'Doctor (Dr. Swastik Bhardwaj)', roleName: 'Doctor' },
  receptionist: { email: 'receptionist@hospital.com', pwd: 'reception123', label: 'Receptionist (Front Desk)', roleName: 'Receptionist' },
  patient: { email: 'patient@hospital.com', pwd: 'patient123', label: 'Patient (Ramesh Chandra Pradhan)', roleName: 'Patient' },
};

let currentGateRole = 'admin';
let patientDirectoryCache = [];

function selectLoginGatePreset(role) {
  currentGateRole = role;
  document.querySelectorAll('.login-preset-card').forEach(c => c.classList.remove('active'));
  const card = document.getElementById(`presetCard-${role}`);
  if (card) card.classList.add('active');

  const p = USER_PRESETS[role] || USER_PRESETS.admin;
  const emailInp = document.getElementById('loginGateEmail');
  const pwdInp = document.getElementById('loginGatePassword');
  const hintBadge = document.getElementById('loginGateHintBadge');
  const patientPicker = document.getElementById('gatePatientPickerSection');

  if (role === 'patient') {
    if (patientPicker) patientPicker.style.display = 'block';
    populateGatePatientDropdown();
    if (pwdInp) pwdInp.value = 'patient123';
    if (hintBadge) hintBadge.innerHTML = `Default: <strong>patient123</strong> (Click to fill)`;
  } else {
    if (patientPicker) patientPicker.style.display = 'none';
    if (emailInp) emailInp.value = p.email;
    if (pwdInp) pwdInp.value = '';
    if (hintBadge) hintBadge.innerHTML = `Demo: <strong>${p.pwd}</strong> (Click to fill)`;
  }

  if (pwdInp) pwdInp.focus();
}

async function populateGatePatientDropdown(list = null) {
  const select = document.getElementById('gatePatientSelect');
  if (!select) return;

  let patients = list || patientDirectoryCache;
  if (!patients || patients.length === 0) {
    try {
      patients = await apiRequest('/patients/portal-accounts/directory');
      patientDirectoryCache = patients || [];
    } catch (e) {
      console.warn('Failed loading gate patients dropdown:', e);
    }
  }

  if (patients && patients.length > 0) {
    select.innerHTML = patients.map((p, idx) => `
      <option value="${p.email || ''}" ${idx === 0 ? 'selected' : ''}>
        ${p.full_name} (${p.mrn} • ${p.email || 'patient_' + p.patient_id + '@utkalhospital.com'})
      </option>
    `).join('');

    const emailInp = document.getElementById('loginGateEmail');
    if (emailInp && select.value) {
      emailInp.value = select.value;
    }
  }
}

function onGatePatientSelected(patientEmail) {
  if (!patientEmail) return;
  const emailInp = document.getElementById('loginGateEmail');
  const pwdInp = document.getElementById('loginGatePassword');
  if (emailInp) emailInp.value = patientEmail;
  if (pwdInp) pwdInp.value = 'patient123';
  const hintBadge = document.getElementById('loginGateHintBadge');
  if (hintBadge) hintBadge.innerHTML = `Password: <strong>patient123</strong> (Click to fill)`;
}

function fillGateDemoPassword() {
  const p = USER_PRESETS[currentGateRole] || USER_PRESETS.admin;
  const pwdInp = document.getElementById('loginGatePassword');
  if (pwdInp) pwdInp.value = (currentGateRole === 'patient') ? 'patient123' : p.pwd;
}

function openLoginScreen(targetRole = null) {
  const gate = document.getElementById('loginScreenGate');
  if (gate) gate.style.display = 'flex';
  const alertBox = document.getElementById('loginGateAlert');
  if (alertBox) alertBox.style.display = 'none';

  selectLoginGatePreset(targetRole || (appState.user ? appState.user.role : 'admin'));
}

function closeLoginScreen() {
  const gate = document.getElementById('loginScreenGate');
  if (gate) gate.style.display = 'none';
}

// Open Login / Role Switch Modal requiring User ID and Password
function openLoginModal(targetRole = null) {
  openLoginScreen(targetRole);
}

// Preset button click inside modal
function selectRolePreset(role) {
  openLoginScreen(role);
}

// Quick fill current role password
function fillCurrentPassword() {
  fillGateDemoPassword();
}

// Legacy helper compatibility
function fillCredentials(email, pwd) {
  const emailInp = document.getElementById('loginGateEmail');
  const pwdInp = document.getElementById('loginGatePassword');
  if (emailInp) emailInp.value = email;
  if (pwdInp) pwdInp.value = pwd;
}

// Perform real authentication via POST /api/v1/auth/login
async function authenticateUser(email, password) {
  const alertBoxGate = document.getElementById('loginGateAlert');
  const alertBoxModal = document.getElementById('loginModalAlert');
  const submitBtn = document.getElementById('loginGateSubmitBtn');
  
  if (alertBoxGate) alertBoxGate.style.display = 'none';
  if (alertBoxModal) alertBoxModal.style.display = 'none';
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerText = 'Verifying credentials...';
  }

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      const msg = data.detail || 'Incorrect User ID / Email or Password.';
      if (alertBoxGate) {
        alertBoxGate.style.display = 'block';
        alertBoxGate.innerHTML = `⚠️ <strong>Authentication Failed:</strong> ${msg}`;
      }
      if (alertBoxModal) {
        alertBoxModal.style.display = 'block';
        alertBoxModal.innerHTML = `⚠️ <strong>Authentication Failed:</strong> ${msg}`;
      }
      throw new Error(msg);
    }

    appState.token = data.access_token;
    appState.user = data.user;
    localStorage.setItem('medflow_token', data.access_token);
    localStorage.setItem('medflow_user', JSON.stringify(data.user));

    closeLoginScreen();
    closeModal('modalLogin');
    updateUserUI();
    applyRolePermissions(data.user.role);
    showToast(`✓ Welcome ${data.user.full_name} (${data.user.role.toUpperCase()})!`, 'success');

    // Switch to dashboard and reload data for new role
    switchPage('dashboard');
  } catch (err) {
    console.warn('Authentication error:', err.message);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerText = 'Sign In & Access Portal →';
    }
  }
}

// Dynamically transform UI based on authenticated role
function applyRolePermissions(role) {
  // Update Navbar Role Pill highlight
  document.querySelectorAll('.role-pill-btn').forEach(btn => btn.classList.remove('active'));
  const activeBtn = document.getElementById(`roleBtn-${role}`);
  if (activeBtn) activeBtn.classList.add('active');

  const navPatients = document.getElementById('nav-patients');
  const navAppointments = document.getElementById('nav-appointments');
  const navDoctors = document.getElementById('nav-doctors');
  const navPrescriptions = document.getElementById('nav-prescriptions');
  const navLabReports = document.getElementById('nav-lab-reports');
  const navBilling = document.getElementById('nav-billing');
  const navPharmacy = document.getElementById('nav-pharmacy');
  const navSettings = document.getElementById('nav-settings');

  const navTextDashboard = document.getElementById('navTextDashboard');
  const navTextAppointments = document.getElementById('navTextAppointments');
  const navTextPrescriptions = document.getElementById('navTextPrescriptions');
  const navTextLabReports = document.getElementById('navTextLabReports');
  const navTextBilling = document.getElementById('navTextBilling');
  const navTextPatients = document.getElementById('navTextPatients');
  const navTextDoctors = document.getElementById('navTextDoctors');
  const navTextSettings = document.getElementById('navTextSettings');

  const btnRegPatient = document.getElementById('btnRegisterPatientBanner');
  const btnBookAppointment = document.getElementById('btnBookAppointmentBanner');
  const btnIssuePrescription = document.getElementById('btnIssuePrescription');
  const btnOrderLabTest = document.getElementById('btnOrderLabTest');
  const btnCreateInvoice = document.getElementById('btnCreateInvoice');
  const btnAddMedicine = document.getElementById('btnAddMedicine');
  const sectionHospitalBranding = document.getElementById('sectionHospitalBranding');
  const clinicalVolumeSection = document.getElementById('clinicalVolumeSection');
  const billingKpiSection = document.getElementById('billingKpiSection');
  const dashboardMainSplit = document.getElementById('dashboardMainSplit');
  const activityFeedTitle = document.getElementById('activityFeedTitle');

  const t1 = document.getElementById('kpiTitle1');
  const t2 = document.getElementById('kpiTitle2');
  const t3 = document.getElementById('kpiTitle3');
  const t4 = document.getElementById('kpiTitle4');
  const s1 = document.getElementById('kpiSub1');
  const s2 = document.getElementById('kpiSub2');
  const s3 = document.getElementById('kpiSub3');
  const s4 = document.getElementById('kpiSub4');

  const welcomeTitle = document.getElementById('dashboardWelcomeTitle');
  const welcomeSub = document.getElementById('dashboardWelcomeSubtitle');

  if (role === 'patient') {
    // ================= PATIENT VIEW (STRICT PATIENT PORTAL ISOLATION) =================
    // Sidebar: Hide Admin/Staff modules completely
    if (navPatients) navPatients.style.display = 'none';
    if (navDoctors) navDoctors.style.display = 'none';
    if (navPharmacy) navPharmacy.style.display = 'none';

    // Show patient personal care modules
    if (navAppointments) navAppointments.style.display = 'flex';
    if (navPrescriptions) navPrescriptions.style.display = 'flex';
    if (navLabReports) navLabReports.style.display = 'flex';
    if (navBilling) navBilling.style.display = 'flex';
    if (navSettings) navSettings.style.display = 'flex';

    // Rename navigation strictly to Patient perspective
    if (navTextDashboard) navTextDashboard.innerText = 'My Health Portal';
    if (navTextAppointments) navTextAppointments.innerText = 'My Appointments';
    if (navTextPrescriptions) navTextPrescriptions.innerText = 'My Prescriptions (Rx)';
    if (navTextLabReports) navTextLabReports.innerText = 'My Lab Reports';
    if (navTextBilling) navTextBilling.innerText = 'My Bills & Payments';
    if (navTextSettings) navTextSettings.innerText = 'My Account & Security';

    // Dashboard Banner
    if (btnRegPatient) btnRegPatient.style.display = 'none';
    if (btnBookAppointment) {
      btnBookAppointment.style.display = 'inline-flex';
      btnBookAppointment.innerHTML = `
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        Book Consultation
      `;
    }
    if (welcomeTitle) welcomeTitle.innerText = `Welcome, ${appState.user.full_name} // Patient Portal`;
    if (welcomeSub) welcomeSub.innerHTML = `Personal Electronic Health Record | <span style="font-weight:700; color:#0F766E;">Utkal Hospital & Medical Research Centre</span>`;

    // Patient Dashboard KPIs
    if (t1) t1.innerText = 'My Total Consultations';
    if (t2) t2.innerText = 'My Upcoming Visits';
    if (t3) t3.innerText = 'My Total Medical Bills';
    if (t4) t4.innerText = 'Pending Diagnostic Reports';

    if (s1) s1.innerText = 'Past consultations on record';
    if (s2) s2.innerText = 'Scheduled & confirmed visits';
    if (s3) s3.innerText = 'Total bills in Indian Rupees (₹)';
    if (s4) s4.innerText = 'Awaiting laboratory analysis';

    // Hide hospital-wide operational metrics from patient
    if (btnIssuePrescription) btnIssuePrescription.style.display = 'none';
    if (btnOrderLabTest) btnOrderLabTest.style.display = 'none';
    if (btnCreateInvoice) btnCreateInvoice.style.display = 'none';
    if (btnAddMedicine) btnAddMedicine.style.display = 'none';
    if (sectionHospitalBranding) sectionHospitalBranding.style.display = 'none';
    if (billingKpiSection) billingKpiSection.style.display = 'none';
    if (clinicalVolumeSection) clinicalVolumeSection.style.display = 'none';
    if (dashboardMainSplit) dashboardMainSplit.style.gridTemplateColumns = '1fr';
    if (activityFeedTitle) activityFeedTitle.innerText = 'My Personal Healthcare Timeline';

    // If currently on an inaccessible page, redirect to dashboard
    if (['patients', 'doctors', 'pharmacy'].includes(appState.currentPage)) {
      switchPage('dashboard');
    }

  } else if (role === 'doctor') {
    // ================= DOCTOR VIEW =================
    if (navPatients) navPatients.style.display = 'flex';
    if (navAppointments) navAppointments.style.display = 'flex';
    if (navDoctors) navDoctors.style.display = 'flex';
    if (navPrescriptions) navPrescriptions.style.display = 'flex';
    if (navLabReports) navLabReports.style.display = 'flex';
    if (navBilling) navBilling.style.display = 'none';
    if (navPharmacy) navPharmacy.style.display = 'none';
    if (navSettings) navSettings.style.display = 'flex';

    if (navTextDashboard) navTextDashboard.innerText = 'Doctor Workstation';
    if (navTextPatients) navTextPatients.innerText = 'My Clinical Patients';
    if (navTextAppointments) navTextAppointments.innerText = 'My OPD Consultations';
    if (navTextDoctors) navTextDoctors.innerText = 'Doctors Faculty';
    if (navTextPrescriptions) navTextPrescriptions.innerText = 'Prescriptions Issued (Rx)';
    if (navTextLabReports) navTextLabReports.innerText = 'Diagnostic Investigations';
    if (navTextSettings) navTextSettings.innerText = 'Account Settings';

    if (btnRegPatient) btnRegPatient.style.display = 'none';
    if (btnBookAppointment) {
      btnBookAppointment.style.display = 'inline-flex';
      btnBookAppointment.innerHTML = `
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        Schedule Consultation
      `;
    }

    if (welcomeTitle) welcomeTitle.innerText = `Clinical Workstation // ${appState.user.full_name}`;
    if (welcomeSub) welcomeSub.innerHTML = `Physician Clinical Workstation | <span style="font-weight:700; color:#0F766E;">Utkal Hospital</span>`;

    if (t1) t1.innerText = 'My Active Patients';
    if (t2) t2.innerText = "Today's Consultations";
    if (t3) t3.innerText = 'Prescriptions Written';
    if (t4) t4.innerText = 'Pending Diagnostic Tests';

    if (s1) s1.innerText = 'Patients under direct clinical care';
    if (s2) s2.innerText = 'Scheduled consultations today';
    if (s3) s3.innerText = 'Active prescriptions issued';
    if (s4) s4.innerText = 'Specimens in diagnostic queue';

    if (btnIssuePrescription) btnIssuePrescription.style.display = 'inline-flex';
    if (btnOrderLabTest) btnOrderLabTest.style.display = 'inline-flex';
    if (btnCreateInvoice) btnCreateInvoice.style.display = 'none';
    if (btnAddMedicine) btnAddMedicine.style.display = 'none';

    if (sectionHospitalBranding) sectionHospitalBranding.style.display = 'none';
    if (billingKpiSection) billingKpiSection.style.display = 'none';
    if (clinicalVolumeSection) clinicalVolumeSection.style.display = 'block';
    if (dashboardMainSplit) dashboardMainSplit.style.gridTemplateColumns = '2fr 1fr';
    if (activityFeedTitle) activityFeedTitle.innerText = 'Physician Activity Feed';

  } else if (role === 'receptionist') {
    // ================= RECEPTIONIST VIEW =================
    if (navPatients) navPatients.style.display = 'flex';
    if (navAppointments) navAppointments.style.display = 'flex';
    if (navDoctors) navDoctors.style.display = 'flex';
    if (navPrescriptions) navPrescriptions.style.display = 'none';
    if (navLabReports) navLabReports.style.display = 'none';
    if (navBilling) navBilling.style.display = 'flex';
    if (navPharmacy) navPharmacy.style.display = 'none';
    if (navSettings) navSettings.style.display = 'flex';

    if (navTextDashboard) navTextDashboard.innerText = 'Front Desk Dashboard';
    if (navTextPatients) navTextPatients.innerText = 'Patient Registration & Check-in';
    if (navTextAppointments) navTextAppointments.innerText = 'Appointments & Check-in';
    if (navTextDoctors) navTextDoctors.innerText = 'Doctors Faculty Roster';
    if (navTextBilling) navTextBilling.innerText = 'Cash Counter & Invoices';
    if (navTextSettings) navTextSettings.innerText = 'Account Settings';

    if (btnRegPatient) btnRegPatient.style.display = 'inline-flex';
    if (btnBookAppointment) {
      btnBookAppointment.style.display = 'inline-flex';
      btnBookAppointment.innerHTML = `
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        Book Appointment
      `;
    }

    if (welcomeTitle) welcomeTitle.innerText = `Front Desk Operations Terminal`;
    if (welcomeSub) welcomeSub.innerHTML = `Reception & Patient Registration | <span style="font-weight:700; color:#0F766E;">Utkal Hospital</span>`;

    if (t1) t1.innerText = 'Active Patients Registered';
    if (t2) t2.innerText = "Today's Appointments";
    if (t3) t3.innerText = 'Billing Collected (Month)';
    if (t4) t4.innerText = 'Front Desk Alerts';

    if (s1) s1.innerText = 'Live EHR patient count';
    if (s2) s2.innerText = 'Scheduled & confirmed visits';
    if (s3) s3.innerText = '↑ Indian Rupees (INR)';
    if (s4) s4.innerText = 'Patient queue & check-in flags';

    if (btnIssuePrescription) btnIssuePrescription.style.display = 'none';
    if (btnOrderLabTest) btnOrderLabTest.style.display = 'none';
    if (btnCreateInvoice) btnCreateInvoice.style.display = 'inline-flex';
    if (btnAddMedicine) btnAddMedicine.style.display = 'inline-flex';

    if (sectionHospitalBranding) sectionHospitalBranding.style.display = 'none';
    if (billingKpiSection) billingKpiSection.style.display = 'grid';
    if (clinicalVolumeSection) clinicalVolumeSection.style.display = 'block';
    if (dashboardMainSplit) dashboardMainSplit.style.gridTemplateColumns = '2fr 1fr';
    if (activityFeedTitle) activityFeedTitle.innerText = 'Hospital Front Desk Events';

  } else {
    // ================= ADMIN VIEW (FULL ACCESS) =================
    if (navPatients) navPatients.style.display = 'flex';
    if (navAppointments) navAppointments.style.display = 'flex';
    if (navDoctors) navDoctors.style.display = 'flex';
    if (navPrescriptions) navPrescriptions.style.display = 'flex';
    if (navLabReports) navLabReports.style.display = 'flex';
    if (navBilling) navBilling.style.display = 'flex';
    if (navPharmacy) navPharmacy.style.display = 'flex';
    if (navSettings) navSettings.style.display = 'flex';

    if (navTextDashboard) navTextDashboard.innerText = 'Dashboard';
    if (navTextPatients) navTextPatients.innerText = 'Patients Directory';
    if (navTextAppointments) navTextAppointments.innerText = 'Appointments & Visits';
    if (navTextDoctors) navTextDoctors.innerText = 'Doctors & Faculty';
    if (navTextPrescriptions) navTextPrescriptions.innerText = 'Prescriptions (℞)';
    if (navTextLabReports) navTextLabReports.innerText = 'Diagnostic Lab Reports';
    if (navTextBilling) navTextBilling.innerText = 'Billing & Invoices';
    if (navTextPharmacy) navTextPharmacy.innerText = 'Pharmacy Stock';
    if (navTextSettings) navTextSettings.innerText = 'Settings & Hospital Name';

    if (btnRegPatient) btnRegPatient.style.display = 'inline-flex';
    if (btnBookAppointment) {
      btnBookAppointment.style.display = 'inline-flex';
      btnBookAppointment.innerHTML = `
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        Book Appointment
      `;
    }

    if (welcomeTitle) welcomeTitle.innerText = `Executive Command Dashboard // Real-Time Telemetry`;
    if (welcomeSub) welcomeSub.innerHTML = `Operational pulse of <span style="font-weight:700; color:#0F766E;">Utkal Hospital & Medical Research Centre</span>`;

    if (t1) t1.innerText = 'Active Patients Registered';
    if (t2) t2.innerText = "Today's Appointments";
    if (t3) t3.innerText = 'Revenue Collected (Month)';
    if (t4) t4.innerText = 'Critical Lab & Inventory Alerts';

    if (s1) s1.innerText = '↑ Live record count';
    if (s2) s2.innerText = 'Scheduled & Confirmed';
    if (s3) s3.innerText = '↑ Indian Rupees (INR)';
    if (s4) s4.innerText = 'Live DB Flags Requiring Action';

    if (btnIssuePrescription) btnIssuePrescription.style.display = 'inline-flex';
    if (btnOrderLabTest) btnOrderLabTest.style.display = 'inline-flex';
    if (btnCreateInvoice) btnCreateInvoice.style.display = 'inline-flex';
    if (btnAddMedicine) btnAddMedicine.style.display = 'inline-flex';

    if (sectionHospitalBranding) sectionHospitalBranding.style.display = 'block';
    if (billingKpiSection) billingKpiSection.style.display = 'grid';
    if (clinicalVolumeSection) clinicalVolumeSection.style.display = 'block';
    if (dashboardMainSplit) dashboardMainSplit.style.gridTemplateColumns = '2fr 1fr';
    if (activityFeedTitle) activityFeedTitle.innerText = 'Live Clinical Activity Feed';
  }
}

function updateUserUI() {
  const nameEl = document.getElementById('navUserName');
  const roleEl = document.getElementById('navUserRole');
  const avatarEl = document.getElementById('navUserAvatar');
  if (nameEl) nameEl.innerText = appState.user.full_name;
  if (roleEl) roleEl.innerText = appState.user.role.toUpperCase();
  if (avatarEl) {
    const parts = (appState.user.full_name || 'AD').replace(/^(Dr\.|Mr\.|Mrs\.|Ms\.)\s*/i, '').trim().split(' ');
    const initials = parts.length > 1 ? (parts[0][0] + parts[1][0]) : parts[0].substring(0, 2);
    avatarEl.innerText = initials.toUpperCase();
  }
}

// 1. Dashboard Module Loader
async function loadDashboardData() {
  try {
    const data = await apiRequest('/dashboard/admin');
    const { kpis, appointments_by_day, recent_activity, alerts } = data;

    const pEl = document.getElementById('kpiPatients');
    const aEl = document.getElementById('kpiAppointments');
    const rEl = document.getElementById('kpiRevenue');
    const alEl = document.getElementById('kpiAlerts');

    if (pEl) pEl.innerText = kpis.total_patients;
    if (aEl) aEl.innerText = kpis.today_appointments;
    if (rEl) rEl.innerText = formatINR(kpis.revenue_this_month);
    if (alEl) alEl.innerText = alerts ? alerts.length : 0;

    // Render Dynamic Clinical Visits Bar Chart from DB
    if (appState.user.role !== 'patient') {
      renderClinicalVolumeChart(appointments_by_day);
    }

    // Populate Real Activity Feed
    const feedEl = document.getElementById('recentActivityFeed');
    if (feedEl) {
      if (recent_activity && recent_activity.length > 0) {
        feedEl.innerHTML = recent_activity.map(act => `
          <div style="display:flex; align-items:flex-start; gap:12px; padding:12px 0; border-bottom:1px solid #F1F5F9;">
            <div style="width:36px; height:36px; border-radius:8px; background:${act.badge_color}18; color:${act.badge_color}; display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0;">
              ${act.type === 'appointment' ? '📅' : (act.type === 'prescription' ? '💊' : '🔬')}
            </div>
            <div style="flex:1; min-width:0;">
              <div style="font-size:13px; font-weight:700; color:#0F172A; margin-bottom:2px;">${act.title}</div>
              <div style="font-size:12px; color:#475569; line-height:1.4;">${act.description}</div>
              <div style="font-size:11px; color:#94A3B8; margin-top:4px;">${act.timestamp}</div>
            </div>
          </div>
        `).join('');
      } else {
        feedEl.innerHTML = '<div style="padding:20px; text-align:center; color:#94A3B8; font-size:13px;">No recent activity logged yet.</div>';
      }
    }

    // Populate Real Alerts Box
    const alertBox = document.getElementById('dashboardAlertsBox');
    if (alertBox) {
      if (alerts && alerts.length > 0) {
        alertBox.innerHTML = alerts.map(al => `
          <div style="background:${al.severity === 'error' ? '#FEE2E2' : '#FEF3C7'}; border:1px solid ${al.severity === 'error' ? '#FCA5A5' : '#FDE68A'}; border-radius:10px; padding:12px 16px; margin-bottom:10px; display:flex; align-items:center; justify-content:space-between; gap:12px;">
            <div style="font-size:13px; color:${al.severity === 'error' ? '#991B1B' : '#92400E'};">
              <strong>${al.title}:</strong> ${al.message}
            </div>
            <span class="badge ${al.severity === 'error' ? 'badge-cancelled' : 'badge-pending'}">${al.severity.toUpperCase()}</span>
          </div>
        `).join('');
      } else {
        alertBox.innerHTML = '';
      }
    }
  } catch (e) {
    console.error('Failed loading dashboard:', e);
  }
}

// Render Real DB Clinical Volume Bar Chart
function renderClinicalVolumeChart(dataPoints) {
  const chartEl = document.getElementById('clinicalVolumeChart');
  if (!chartEl) return;

  if (!dataPoints || dataPoints.length === 0) {
    chartEl.innerHTML = '<div style="margin:auto; color:#94A3B8; font-size:12px;">No historical volume data available.</div>';
    return;
  }

  const values = dataPoints.map(p => p.value || 0);
  const maxVal = Math.max(...values, 5);

  chartEl.innerHTML = dataPoints.map(p => {
    const pct = Math.max(8, Math.round((p.value / maxVal) * 160));
    return `
      <div class="chart-bar-col">
        <div class="chart-bar-tooltip">${p.label}: ${p.value} visits</div>
        <div class="chart-bar-fill" style="height:${pct}px;"></div>
        <span style="font-size:10px; font-weight:600; color:#64748B; white-space:nowrap;">${p.label}</span>
      </div>
    `;
  }).join('');
}

// 2. Patients Module Loader
async function loadPatientsData(search = '') {
  try {
    const data = await apiRequest(`/patients/?page=1&page_size=30${search ? `&search=${encodeURIComponent(search)}` : ''}`);
    appState.patients = data.items || [];
    renderPatientsTable(appState.patients);
  } catch (e) {
    console.error('Error loading patients:', e);
  }
}

function renderPatientsTable(list) {
  const tbody = document.getElementById('patientsTableBody');
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:30px; color:#94A3B8;">No matching patient records found.</td></tr>';
    return;
  }

  tbody.innerHTML = list.map(p => {
    const loginUser = p.portal_username || p.email || `patient_${p.id}@utkalhospital.com`;
    const hasPortal = p.has_portal_account || Boolean(p.user_id);
    return `
      <tr>
        <td>
          <div style="display:flex; align-items:center; gap:10px;">
            <div class="avatar" style="background:#0D9488; color:#FFF; font-weight:700;">${p.full_name[0]}</div>
            <div>
              <div style="font-weight:700; color:var(--text-primary);">${p.full_name}</div>
              <div style="font-size:11px; color:var(--text-muted); font-family:'JetBrains Mono',monospace;">MRN: UTK-${1000 + p.id} (ID: #${p.id})</div>
            </div>
          </div>
        </td>
        <td>
          <div style="font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700; color:var(--primary);">
            <code>${loginUser}</code>
          </div>
          <div style="margin-top:3px;">
            <span class="badge ${hasPortal ? 'badge-confirmed' : 'badge-scheduled'}" style="font-size:9px;">
              ${hasPortal ? 'PORTAL ACTIVE' : 'NO PORTAL'}
            </span>
          </div>
        </td>
        <td>
          <div style="font-weight:600;">${p.gender}</div>
          <div style="font-size:11px; color:var(--text-muted);">${p.address || 'Odisha, India'} (DOB: ${p.date_of_birth})</div>
        </td>
        <td>${p.phone}</td>
        <td><span class="badge" style="background:#FEE2E2; color:#B91C1C; font-weight:700;">${p.blood_group || 'O+'}</span></td>
        <td><span style="color:${p.allergies && p.allergies !== 'None' ? '#DC2626' : '#10B981'}; font-size:12px; font-weight:600;">${p.allergies || 'None'}</span></td>
        <td>
          <div style="display:flex; gap:6px; flex-wrap:wrap;">
            <button type="button" class="btn btn-outline btn-sm" onclick="viewPatientDetail(${p.id})">EHR Chart</button>
            <button type="button" class="btn btn-primary btn-sm" onclick="quickLoginAsPatient('${loginUser}', 'patient123')" title="Instantly log in as this patient">Sign In →</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// View Comprehensive Patient EHR Chart Modal
async function viewPatientDetail(patientId) {
  try {
    const summary = await apiRequest(`/patients/${patientId}/dashboard`);
    const pat = appState.patients.find(p => p.id === patientId) || summary;

    const titleEl = document.getElementById('chartPatientTitle');
    const subEl = document.getElementById('chartPatientSubtitle');
    const bodyEl = document.getElementById('patientChartBody');

    if (titleEl) titleEl.innerText = `EHR Chart: ${summary.full_name} (MRN: UTK-${1000 + summary.patient_id})`;
    if (subEl) subEl.innerText = `DOB: ${pat.date_of_birth || '-'} | Blood Group: ${pat.blood_group || 'O+'} | Phone: ${pat.phone || '-'}`;

    if (bodyEl) {
      bodyEl.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin-bottom:20px;">
          <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:11px; color:#64748B; font-weight:600;">Total Clinical Visits</div>
            <div style="font-size:20px; font-weight:800; color:#0D9488;">${summary.total_visits}</div>
          </div>
          <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:11px; color:#64748B; font-weight:600;">Active Prescriptions</div>
            <div style="font-size:20px; font-weight:800; color:#3B82F6;">${summary.active_prescriptions_count}</div>
          </div>
          <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:11px; color:#64748B; font-weight:600;">Pending Lab Reports</div>
            <div style="font-size:20px; font-weight:800; color:#F59E0B;">${summary.pending_reports_count}</div>
          </div>
          <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:11px; color:#64748B; font-weight:600;">Unpaid Invoices</div>
            <div style="font-size:20px; font-weight:800; color:#EF4444;">${summary.unpaid_invoices_count}</div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:20px;">
          <div style="background:#FFF; border:1px solid #E2E8F0; border-radius:8px; padding:14px;">
            <h4 style="font-size:13px; font-weight:700; margin-bottom:8px; color:#0F172A;">Medical History & Comorbidities</h4>
            <p style="font-size:12px; color:#475569; line-height:1.5;">${pat.medical_history || 'No chronic comorbidities recorded.'}</p>
          </div>
          <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:14px;">
            <h4 style="font-size:13px; font-weight:700; margin-bottom:8px; color:#991B1B;">⚠️ Drug Allergies & Contraindications</h4>
            <p style="font-size:12px; color:#B91C1C; font-weight:600;">${pat.allergies || 'No known drug allergies reported.'}</p>
          </div>
        </div>

        <h4 style="font-size:14px; font-weight:700; margin-bottom:8px; color:#0F172A;">Recent Appointments & Consultations</h4>
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:20px;">
          ${summary.upcoming_appointments && summary.upcoming_appointments.length > 0 ? summary.upcoming_appointments.map(a => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #E2E8F0;">
              <div>
                <strong>${a.date || a.appointment_date} at ${a.time_slot}</strong> with ${typeof a.doctor === 'string' ? a.doctor : (a.doctor?.full_name || 'Attending Physician')}
                <div style="font-size:11px; color:#64748B;">Reason: ${a.reason}</div>
              </div>
              <span class="badge badge-${a.status}">${(a.status || '').toUpperCase()}</span>
            </div>
          `).join('') : '<div style="font-size:12px; color:#94A3B8;">No recent appointment history.</div>'}
        </div>

        <h4 style="font-size:14px; font-weight:700; margin-bottom:8px; color:#0F172A;">Active Prescriptions (℞)</h4>
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:20px;">
          ${summary.recent_prescriptions && summary.recent_prescriptions.length > 0 ? summary.recent_prescriptions.map(pr => `
            <div style="padding:8px 0; border-bottom:1px solid #E2E8F0;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <strong>℞ #${pr.id} (${pr.date || pr.prescription_date})</strong>
                  <span style="font-size:12px; color:#0F766E; margin-left:8px;">Prescribed by ${typeof pr.doctor === 'string' ? pr.doctor : (pr.doctor?.full_name || 'Physician')}</span>
                </div>
                <a href="${API_BASE}/prescriptions/${pr.id}/pdf" target="_blank" download class="btn btn-outline btn-sm">🖨️ Download PDF</a>
              </div>
              <div style="font-size:12px; color:#475569; margin-top:4px;">
                ${pr.instructions || 'Follow prescribed medical regime'} (${pr.items_count || 1} medication items)
              </div>
            </div>
          `).join('') : '<div style="font-size:12px; color:#94A3B8;">No active prescriptions recorded.</div>'}
        </div>

        <h4 style="font-size:14px; font-weight:700; margin-bottom:8px; color:#0F172A;">Diagnostic Lab Tests</h4>
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px;">
          ${summary.recent_reports && summary.recent_reports.length > 0 ? summary.recent_reports.map(lr => `
            <div style="padding:8px 0; border-bottom:1px solid #E2E8F0; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <strong>${lr.test_type.toUpperCase()}</strong> (${lr.scheduled_date})
                <div style="font-size:12px; color:#475569;">${lr.findings || 'Pending specimen analysis'}</div>
              </div>
              <span class="badge badge-${lr.status}">${lr.status}</span>
            </div>
          `).join('') : '<div style="font-size:12px; color:#94A3B8;">No diagnostic reports ordered.</div>'}
        </div>
      `;
    }

    openModal('modalPatientChart');
  } catch (e) {
    showToast(e.message, 'error');
  }
}

// 3. Doctors Module Loader
async function loadDoctorsData(search = '') {
  try {
    const data = await apiRequest('/doctors/?page=1&page_size=20');
    appState.doctors = data.items || [];
    renderDoctorsGrid(appState.doctors, search);
  } catch (e) {
    console.error('Error loading doctors:', e);
  }
}

function renderDoctorsGrid(list, search = '') {
  const grid = document.getElementById('doctorsGrid');
  if (!grid) return;

  const q = search.toLowerCase();
  const filtered = list.filter(d => 
    !q || d.full_name.toLowerCase().includes(q) || 
    d.specialization.toLowerCase().includes(q) ||
    (d.department && d.department.name.toLowerCase().includes(q))
  );

  if (filtered.length === 0) {
    grid.innerHTML = '<div style="grid-column:1/-1; padding:30px; text-align:center; color:#94A3B8;">No matching doctors found.</div>';
    return;
  }

  grid.innerHTML = filtered.map(d => `
    <div class="card">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
        <div class="avatar" style="width:44px; height:44px; font-size:16px; background:#0D9488; font-weight:700;">
          ${d.full_name.replace('Dr. ', '')[0] || 'D'}
        </div>
        <div>
          <div style="font-weight:700; color:#0F172A; font-size:15px;">${d.full_name}</div>
          <div style="font-size:13px; color:#0D9488; font-weight:600;">${d.specialization}</div>
        </div>
      </div>
      <div style="font-size:12px; color:#475569; line-height:1.7;">
        <div><strong>Department:</strong> ${d.department ? d.department.name : 'Specialty Clinic'}</div>
        <div><strong>Qualification:</strong> ${d.qualification}</div>
        <div><strong>Experience:</strong> ${d.experience_years} Years of Practice</div>
        <div><strong>Consultation Fee:</strong> <span style="color:#10B981; font-weight:700; font-size:14px;">${formatINR(d.consultation_fee)}</span></div>
        <div><strong>Available Hours:</strong> ${d.working_hours_start} - ${d.working_hours_end}</div>
      </div>
      <button type="button" class="btn btn-outline btn-sm" style="width:100%; margin-top:14px;" onclick="openBookModalForDoctor(${d.id})">Book Consultation</button>
    </div>
  `).join('');
}

// 4. Appointments Module Loader
async function loadAppointmentsData(search = '') {
  try {
    const data = await apiRequest('/appointments/?page=1&page_size=50');
    appState.appointments = data.items || [];
    renderAppointmentsTable(appState.appointments, search);
  } catch (e) {
    console.error('Error loading appointments:', e);
  }
}

function renderAppointmentsTable(list, search = '') {
  const tbody = document.getElementById('appointmentsTableBody');
  if (!tbody) return;

  const isPatient = (appState.user.role === 'patient');
  const actionHeader = document.getElementById('appointmentsActionHeader');
  if (actionHeader) {
    actionHeader.style.display = isPatient ? 'none' : 'table-cell';
  }

  const q = search.toLowerCase();
  const filtered = list.filter(a => {
    if (!q) return true;
    const patName = (a.patient ? a.patient.full_name : '').toLowerCase();
    const docName = (a.doctor ? a.doctor.full_name : '').toLowerCase();
    const reason = (a.reason || '').toLowerCase();
    return patName.includes(q) || docName.includes(q) || reason.includes(q);
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="${isPatient ? 6 : 7}" style="text-align:center; padding:30px; color:#94A3B8;">No appointments found.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(a => `
    <tr>
      <td><strong>#${a.id}</strong></td>
      <td><strong>${a.patient ? a.patient.full_name : 'Patient'}</strong></td>
      <td>${a.doctor ? a.doctor.full_name : 'Doctor'}</td>
      <td>${a.appointment_date} at <strong>${a.time_slot}</strong></td>
      <td>
        ${a.reason}
        ${a.diagnosis ? `<div style="font-size:11px; color:#10B981; font-weight:600; margin-top:2px;">Dx: ${a.diagnosis}</div>` : ''}
      </td>
      <td><span class="badge badge-${a.status}">${a.status.replace('_', ' ').toUpperCase()}</span></td>
      ${!isPatient ? `
        <td>
          ${a.status !== 'completed' ? `
            <button type="button" class="btn btn-primary btn-sm" onclick="openCompleteVisitModal(${a.id})">Complete Visit</button>
          ` : `
            <span style="color:#10B981; font-size:12px; font-weight:700;">Diagnosis Saved ✓</span>
          `}
        </td>
      ` : ''}
    </tr>
  `).join('');
}

// Open Dedicated Complete Visit Modal
function openCompleteVisitModal(appId) {
  const app = appState.appointments.find(a => a.id === appId);
  if (!app) return;

  const idInp = document.getElementById('compAppointmentId');
  const sumDiv = document.getElementById('compVisitSummary');
  const diagInp = document.getElementById('compDiagnosisInput');
  const notesInp = document.getElementById('compNotesInput');

  if (idInp) idInp.value = appId;
  if (diagInp) diagInp.value = app.diagnosis || '';
  if (notesInp) notesInp.value = app.notes || '';

  if (sumDiv) {
    sumDiv.innerHTML = `
      <div><strong>Appointment ID:</strong> #${app.id} | <strong>Date:</strong> ${app.appointment_date} at ${app.time_slot}</div>
      <div><strong>Patient:</strong> ${app.patient ? app.patient.full_name : 'Patient'}</div>
      <div><strong>Attending Doctor:</strong> ${app.doctor ? app.doctor.full_name : 'Doctor'}</div>
      <div><strong>Reason:</strong> ${app.reason}</div>
    `;
  }

  openModal('modalCompleteVisit');
}

// 5. Prescriptions Module Loader
async function loadPrescriptionsData(search = '') {
  try {
    const data = await apiRequest('/prescriptions/?page=1&page_size=30');
    appState.prescriptions = data.items || [];
    renderPrescriptionsTable(appState.prescriptions, search);
  } catch (e) {
    console.error('Error loading prescriptions:', e);
  }
}

function renderPrescriptionsTable(list, search = '') {
  const tbody = document.getElementById('prescriptionsTableBody');
  if (!tbody) return;

  const q = search.toLowerCase();
  const filtered = list.filter(p => {
    if (!q) return true;
    const patName = (p.patient ? p.patient.full_name : '').toLowerCase();
    const docName = (p.doctor ? p.doctor.full_name : '').toLowerCase();
    return patName.includes(q) || docName.includes(q);
  });

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:30px; color:#94A3B8;">No prescriptions found.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(p => `
    <tr>
      <td><strong>℞ #${p.id}</strong></td>
      <td><strong>${p.patient ? p.patient.full_name : 'Patient'}</strong></td>
      <td>${p.doctor ? p.doctor.full_name : 'Doctor'}</td>
      <td>${p.prescription_date}</td>
      <td>${p.items ? p.items.map(i => `<span style="display:inline-block; background:#F1F5F9; padding:2px 8px; border-radius:4px; margin:2px; font-size:12px;">${i.medicine_name} (${i.dosage})</span>`).join('') : '-'}</td>
      <td>
        <a href="${API_BASE}/prescriptions/${p.id}/pdf" target="_blank" download class="btn btn-outline btn-sm">
          🖨️ Download PDF
        </a>
      </td>
    </tr>
  `).join('');
}

// 6. Lab Reports Module Loader
async function loadLabReportsData(search = '') {
  try {
    const data = await apiRequest('/lab-tests/?page=1&page_size=30');
    appState.labTests = data.items || [];
    renderLabReportsTable(appState.labTests, search);
  } catch (e) {
    console.error('Error loading lab reports:', e);
  }
}

function renderLabReportsTable(list, search = '') {
  const tbody = document.getElementById('labReportsTableBody');
  if (!tbody) return;

  const isPatient = (appState.user.role === 'patient');
  const actionHeader = document.getElementById('labActionHeader');
  if (actionHeader) {
    actionHeader.style.display = isPatient ? 'none' : 'table-cell';
  }

  const q = search.toLowerCase();
  const filtered = list.filter(t => {
    if (!q) return true;
    const patName = (t.patient ? t.patient.full_name : '').toLowerCase();
    const modality = (t.test_type || '').toLowerCase();
    const findings = (t.findings || '').toLowerCase();
    return patName.includes(q) || modality.includes(q) || findings.includes(q);
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="${isPatient ? 7 : 8}" style="text-align:center; padding:30px; color:#94A3B8;">No diagnostic lab tests found.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(t => `
    <tr>
      <td><strong>#${t.id}</strong></td>
      <td><strong>${t.patient ? t.patient.full_name : 'Patient'}</strong></td>
      <td><span class="badge" style="background:#E0F2FE; color:#0369A1; font-weight:700;">${t.test_type.toUpperCase()}</span></td>
      <td>${t.doctor ? t.doctor.full_name : 'Physician'}</td>
      <td>${t.scheduled_date}</td>
      <td><span class="badge badge-${t.status}">${t.status.replace('_', ' ').toUpperCase()}</span></td>
      <td>
        ${t.critical_value ? `<span class="badge badge-critical" style="margin-right:6px;">ABNORMAL / CRITICAL</span>` : ''}
        ${t.findings || '<span style="color:#94A3B8; font-style:italic;">Awaiting specimen analysis</span>'}
      </td>
      ${!isPatient ? `
        <td>
          <button type="button" class="btn btn-outline btn-sm" onclick="openUpdateLabModal(${t.id})">Update Findings</button>
        </td>
      ` : ''}
    </tr>
  `).join('');
}

// Open Dedicated Lab Update Modal
function openUpdateLabModal(testId) {
  const test = appState.labTests.find(t => t.id === testId);
  if (!test) return;

  const idInp = document.getElementById('labTestId');
  const sumDiv = document.getElementById('labTestSummary');
  const findInp = document.getElementById('labFindingsInput');
  const statSelect = document.getElementById('labStatusSelect');
  const critInp = document.getElementById('labCriticalInput');

  if (idInp) idInp.value = testId;
  if (findInp) findInp.value = test.findings || '';
  if (statSelect) statSelect.value = test.status || 'completed';
  if (critInp) critInp.checked = !!test.critical_value;

  if (sumDiv) {
    sumDiv.innerHTML = `
      <div><strong>Diagnostic Order ID:</strong> #${test.id} | <strong>Scheduled:</strong> ${test.scheduled_date}</div>
      <div><strong>Patient:</strong> ${test.patient ? test.patient.full_name : 'Patient'}</div>
      <div><strong>Modality / Specimen:</strong> <span class="badge" style="background:#E0F2FE; color:#0369A1;">${test.test_type.toUpperCase()}</span></div>
    `;
  }

  openModal('modalUpdateLab');
}

// 7. Billing Module Loader (All in Indian Rupees ₹)
async function loadBillingData(search = '') {
  try {
    const invoicesData = await apiRequest('/billing/invoices?page=1&page_size=40');
    appState.invoices = invoicesData.items || [];

    if (appState.user.role !== 'patient') {
      const revData = await apiRequest('/billing/revenue-summary');
      const revTodayEl = document.getElementById('revToday');
      const revMonthEl = document.getElementById('revMonth');
      const revPendingEl = document.getElementById('revPending');

      if (revTodayEl) revTodayEl.innerText = formatINR(revData.revenue_today);
      if (revMonthEl) revMonthEl.innerText = formatINR(revData.revenue_this_month);
      if (revPendingEl) revPendingEl.innerText = formatINR(revData.pending_payments_amount);
    }

    renderBillingTable(appState.invoices, search);
  } catch (e) {
    console.error('Error loading billing:', e);
  }
}

function renderBillingTable(list, search = '') {
  const tbody = document.getElementById('billingTableBody');
  if (!tbody) return;

  const q = search.toLowerCase();
  const filtered = list.filter(inv => {
    if (!q) return true;
    const invNo = (inv.invoice_number || '').toLowerCase();
    const patName = (inv.patient ? inv.patient.full_name : '').toLowerCase();
    const method = (inv.payment_method || '').toLowerCase();
    return invNo.includes(q) || patName.includes(q) || method.includes(q);
  });

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:30px; color:#94A3B8;">No invoices found.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(inv => `
    <tr>
      <td><code style="font-weight:700; color:#0D9488;">${inv.invoice_number}</code></td>
      <td><strong>${inv.patient ? inv.patient.full_name : 'Patient'}</strong></td>
      <td><strong style="font-size:14px; color:#0F172A;">${formatINR(inv.total)}</strong></td>
      <td><span style="color:#10B981; font-weight:600;">${formatINR(inv.amount_paid)}</span></td>
      <td><span class="badge" style="background:#F1F5F9; color:#475569;">${inv.payment_method.toUpperCase()}</span></td>
      <td><span class="badge badge-${inv.payment_status}">${inv.payment_status.toUpperCase()}</span></td>
      <td>
        ${inv.payment_status !== 'paid' ? `
          <button type="button" class="btn btn-primary btn-sm" onclick="openRecordPaymentModal(${inv.id})">${appState.user.role === 'patient' ? 'Pay Online' : 'Record Payment'}</button>
        ` : `<span style="color:#10B981; font-weight:700; font-size:12px;">Paid in Full ✓</span>`}
      </td>
    </tr>
  `).join('');
}

// Open Dedicated Record Payment Modal
function openRecordPaymentModal(invoiceId) {
  const inv = appState.invoices.find(i => i.id === invoiceId);
  if (!inv) return;

  const idInp = document.getElementById('payInvoiceId');
  const sumDiv = document.getElementById('payInvoiceSummary');
  const methodSelect = document.getElementById('payMethodSelect');
  const amtInp = document.getElementById('payAmountInput');

  const balance = Math.max(0, inv.total - inv.amount_paid);

  if (idInp) idInp.value = invoiceId;
  if (amtInp) amtInp.value = balance.toFixed(2);
  if (methodSelect) methodSelect.value = inv.payment_method || 'cash';

  if (sumDiv) {
    sumDiv.innerHTML = `
      <div><strong>Invoice:</strong> ${inv.invoice_number}</div>
      <div><strong>Patient:</strong> ${inv.patient ? inv.patient.full_name : 'Patient'}</div>
      <div style="margin-top:6px; display:flex; gap:16px;">
        <span>Total Bill: <strong>${formatINR(inv.total)}</strong></span>
        <span>Already Paid: <strong style="color:#10B981;">${formatINR(inv.amount_paid)}</strong></span>
        <span>Balance Due: <strong style="color:#EF4444;">${formatINR(balance)}</strong></span>
      </div>
    `;
  }

  openModal('modalRecordPayment');
}

// 8. Pharmacy Module Loader
async function loadPharmacyData(search = '') {
  try {
    const data = await apiRequest('/pharmacy/medicines?page=1&page_size=40');
    const lowStock = await apiRequest('/pharmacy/alerts/low-stock');
    appState.medicines = data.items || [];

    const alertBanner = document.getElementById('pharmacyAlertBanner');
    if (alertBanner) {
      if (lowStock && lowStock.length > 0) {
        alertBanner.style.display = 'block';
        alertBanner.innerHTML = `
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <div>
              <strong>⚠️ Low Stock Clinical Warning:</strong> ${lowStock.length} medicines below mandatory reorder thresholds (${lowStock.map(m => m.name).join(', ')}).
            </div>
            <button type="button" class="btn btn-sm btn-outline" style="border-color:#FCA5A5; color:#991B1B;" onclick="switchPage('pharmacy')">Review Inventory</button>
          </div>
        `;
      } else {
        alertBanner.style.display = 'none';
      }
    }

    renderPharmacyTable(appState.medicines, search);
  } catch (e) {
    console.error('Error loading pharmacy:', e);
  }
}

function renderPharmacyTable(list, search = '') {
  const tbody = document.getElementById('pharmacyTableBody');
  if (!tbody) return;

  const q = search.toLowerCase();
  const filtered = list.filter(m => {
    if (!q) return true;
    const name = (m.name || '').toLowerCase();
    const generic = (m.generic_name || '').toLowerCase();
    const cat = (m.category || '').toLowerCase();
    return name.includes(q) || generic.includes(q) || cat.includes(q);
  });

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:30px; color:#94A3B8;">No medicines found in catalog.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(m => `
    <tr>
      <td><strong>${m.name}</strong></td>
      <td>${m.generic_name}</td>
      <td><span class="badge" style="background:#CCFBF1; color:#0D9488; font-weight:600;">${m.category}</span></td>
      <td>${m.unit}</td>
      <td><strong style="font-size:14px;">${m.total_stock}</strong></td>
      <td>${m.reorder_level}</td>
      <td>
        <span class="badge ${m.is_low_stock ? 'badge-low-stock' : 'badge-completed'}">
          ${m.is_low_stock ? 'LOW STOCK' : 'IN STOCK'}
        </span>
      </td>
      <td>
        <button type="button" class="btn btn-outline btn-sm" onclick="openStockInModal(${m.id})">+ Stock In</button>
      </td>
    </tr>
  `).join('');
}

// Open Dedicated Pharmacy Stock-In Modal
function openStockInModal(medId) {
  const med = appState.medicines.find(m => m.id === medId);
  if (!med) return;

  const idInp = document.getElementById('stockMedId');
  const sumDiv = document.getElementById('stockMedSummary');
  const batchInp = document.getElementById('stockBatchNo');
  const expInp = document.getElementById('stockExpiryDate');

  if (idInp) idInp.value = medId;

  if (batchInp) batchInp.value = `BAT-UTK-${Date.now().toString().slice(-6)}`;
  if (expInp) {
    const nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    expInp.value = nextYear.toISOString().split('T')[0];
  }

  if (sumDiv) {
    sumDiv.innerHTML = `
      <div><strong>Medicine:</strong> ${med.name} (${med.generic_name})</div>
      <div><strong>Category:</strong> ${med.category} | <strong>Unit:</strong> ${med.unit}</div>
      <div style="margin-top:4px;">Current Stock Balance: <strong>${med.total_stock}</strong> (Reorder Threshold: ${med.reorder_level})</div>
    `;
  }

  openModal('modalStockIn');
}

// 9. Settings Module Loader
function loadSettingsData() {
  applyHospitalBranding();

  const nameInp = document.getElementById('settingProfileName');
  const phoneInp = document.getElementById('settingProfilePhone');
  const emailInp = document.getElementById('settingProfileEmail');
  const roleInp = document.getElementById('settingProfileRole');

  if (nameInp) nameInp.value = appState.user.full_name || '';
  if (phoneInp) phoneInp.value = appState.user.phone || '';
  if (emailInp) emailInp.value = appState.user.email || '';
  if (roleInp) roleInp.value = (appState.user.role || 'ADMIN').toUpperCase();
}

// Modal Form Controls
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('active');
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('active');
}

// Open Book Modal and dynamically populate patient & doctor select options
async function openBookModal() {
  await ensurePatientsAndDoctorsLoaded();
  populateAppointmentDropdowns();
  
  const dateInput = document.getElementById('bookDateInput');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }
  
  openModal('modalBookAppointment');
}

async function openBookModalForDoctor(doctorId) {
  await openBookModal();
  const docSelect = document.getElementById('bookDoctorSelect');
  if (docSelect) docSelect.value = doctorId;
}

function openRegisterPatientModal() {
  const pwdInput = document.getElementById('regPassword');
  if (pwdInput && !pwdInput.value) pwdInput.value = 'patient123';
  openModal('modalRegisterPatient');
}

function fillDefaultRegPassword() {
  const pInput = document.getElementById('regPassword');
  if (pInput) pInput.value = 'patient123';
}

// Patient Directory Modal & Quick Login Handlers
async function openPatientDirectoryModal() {
  openModal('modalPatientDirectory');
  await fetchAndRenderPatientDirectory();
}

async function fetchAndRenderPatientDirectory() {
  const tbody = document.getElementById('patientDirectoryTableBody');
  const countBadge = document.getElementById('patientDirCountBadge');
  if (tbody) tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">Fetching patient accounts directory...</td></tr>';

  try {
    const list = await apiRequest('/patients/portal-accounts/directory');
    patientDirectoryCache = list || [];
    if (countBadge) countBadge.innerText = `${patientDirectoryCache.length} Verified Accounts`;
    renderPatientDirectoryRows(patientDirectoryCache);
    populateGatePatientDropdown(patientDirectoryCache);
  } catch (err) {
    console.error('Error fetching patient directory:', err);
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:#EF4444;">Failed to load patient directory: ${err.message}</td></tr>`;
  }
}

function renderPatientDirectoryRows(list) {
  const tbody = document.getElementById('patientDirectoryTableBody');
  if (!tbody) return;

  if (!list || list.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">No matching patient accounts found.</td></tr>';
    return;
  }

  tbody.innerHTML = list.map(p => `
    <tr>
      <td>
        <div style="font-weight:700; color:var(--text-primary);">${p.full_name}</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--text-muted);">${p.mrn} (ID: #${p.patient_id})</div>
      </td>
      <td>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:700; color:var(--primary); font-size:12px;">
          <code>${p.email || 'patient_' + p.patient_id + '@utkalhospital.com'}</code>
        </div>
      </td>
      <td>
        <div>${p.phone}</div>
        <div style="font-size:11px; color:var(--text-muted);">${p.gender} • <span style="font-weight:700; color:#DC2626;">${p.blood_group || 'O+'}</span></div>
      </td>
      <td>
        <div style="font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700; color:var(--text-primary);">
          <code>${p.default_password || 'patient123'}</code>
        </div>
      </td>
      <td>
        <span class="badge ${p.has_portal_account ? 'badge-confirmed' : 'badge-scheduled'}" style="font-size:9px;">
          ${p.has_portal_account ? 'ACTIVE PORTAL' : 'AVAILABLE'}
        </span>
      </td>
      <td>
        <button type="button" class="btn btn-primary btn-sm" onclick="quickLoginAsPatient('${p.email || 'patient_' + p.patient_id + '@utkalhospital.com'}', '${p.default_password || 'patient123'}')">
          Sign In As Patient →
        </button>
      </td>
    </tr>
  `).join('');
}

function filterPatientDirectoryList(q) {
  const term = (q || '').trim().toLowerCase();
  if (!term) {
    renderPatientDirectoryRows(patientDirectoryCache);
    return;
  }
  const filtered = patientDirectoryCache.filter(p =>
    (p.full_name && p.full_name.toLowerCase().includes(term)) ||
    (p.email && p.email.toLowerCase().includes(term)) ||
    (p.mrn && p.mrn.toLowerCase().includes(term)) ||
    (p.phone && p.phone.toLowerCase().includes(term))
  );
  renderPatientDirectoryRows(filtered);
}

async function quickLoginAsPatient(email, password = 'patient123') {
  closeModal('modalPatientDirectory');
  closeLoginScreen();
  await authenticateUser(email, password);
  showToast(`Successfully authenticated as Patient: ${email}`, 'success');
}

// Issue Prescription Modal Controls
async function openCreatePrescriptionModal() {
  await ensurePatientsAndDoctorsLoaded();
  const patSelect = document.getElementById('prescPatientSelect');
  const docSelect = document.getElementById('prescDoctorSelect');
  const instInp = document.getElementById('prescInstructions');
  const container = document.getElementById('prescItemsContainer');

  if (patSelect && appState.patients.length > 0) {
    patSelect.innerHTML = appState.patients.map(p => `
      <option value="${p.id}">${p.full_name} (MRN: UTK-${1000 + p.id}, ${p.gender})</option>
    `).join('');
  }

  if (docSelect && appState.doctors.length > 0) {
    docSelect.innerHTML = appState.doctors.map(d => `
      <option value="${d.id}">${d.full_name} — ${d.specialization}</option>
    `).join('');

    // If current user is a doctor, pre-select their doctor ID
    if (appState.user && appState.user.role === 'doctor') {
      const myDoc = appState.doctors.find(d => d.email === appState.user.email || d.user_id === appState.user.id);
      if (myDoc) docSelect.value = myDoc.id;
    }
  }

  if (instInp) instInp.value = '';
  if (container) {
    container.innerHTML = '';
    addPrescriptionItemRow('Amoxicillin & Potassium Clavulanate 625mg', '625mg', 'Twice daily after meals', '5 days', 10, 'Complete antibiotic schedule');
    addPrescriptionItemRow('Paracetamol 650mg (Dolo)', '650mg', 'Thrice daily if fever > 100°F', '3 days', 9, 'As needed for fever/body pain');
  }

  openModal('modalCreatePrescription');
}

function addPrescriptionItemRow(name = '', dosage = '500mg', freq = 'Twice daily after food', duration = '5 days', qty = 10, notes = '') {
  const container = document.getElementById('prescItemsContainer');
  if (!container) return;
  const rowId = `presc-row-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  const div = document.createElement('div');
  div.id = rowId;
  div.style.background = '#F8FAFC';
  div.style.border = '1px solid #E2E8F0';
  div.style.borderRadius = '8px';
  div.style.padding = '12px';
  div.innerHTML = `
    <div style="display:grid; grid-template-columns: 2fr 1fr 1fr; gap:10px; margin-bottom:8px;">
      <div>
        <label style="font-size:11px; font-weight:700; color:#475569;">Medicine & Salt Name</label>
        <input type="text" class="form-control presc-med-name" placeholder="e.g. Azithromycin 500mg" value="${name}" required style="font-size:13px; padding:6px 10px;">
      </div>
      <div>
        <label style="font-size:11px; font-weight:700; color:#475569;">Dosage</label>
        <input type="text" class="form-control presc-med-dosage" placeholder="e.g. 500mg" value="${dosage}" required style="font-size:13px; padding:6px 10px;">
      </div>
      <div>
        <label style="font-size:11px; font-weight:700; color:#475569;">Quantity</label>
        <input type="number" min="1" class="form-control presc-med-qty" value="${qty}" required style="font-size:13px; padding:6px 10px;">
      </div>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr 2fr auto; gap:10px; align-items:flex-end;">
      <div>
        <label style="font-size:11px; font-weight:700; color:#475569;">Frequency</label>
        <input type="text" class="form-control presc-med-freq" placeholder="e.g. Once daily after food" value="${freq}" required style="font-size:13px; padding:6px 10px;">
      </div>
      <div>
        <label style="font-size:11px; font-weight:700; color:#475569;">Duration</label>
        <input type="text" class="form-control presc-med-duration" placeholder="e.g. 5 days" value="${duration}" required style="font-size:13px; padding:6px 10px;">
      </div>
      <div>
        <label style="font-size:11px; font-weight:700; color:#475569;">Notes / Dietary Guidance</label>
        <input type="text" class="form-control presc-med-notes" placeholder="Optional notes" value="${notes}" style="font-size:13px; padding:6px 10px;">
      </div>
      <button type="button" class="btn btn-outline btn-sm" onclick="document.getElementById('${rowId}').remove()" style="color:#EF4444; border-color:#FCA5A5; padding:6px 10px;">✕</button>
    </div>
  `;
  container.appendChild(div);
}

// Order Diagnostic Lab Test Modal Controls
async function openOrderLabModal() {
  await ensurePatientsAndDoctorsLoaded();
  const patSelect = document.getElementById('orderLabPatientSelect');
  const docSelect = document.getElementById('orderLabDoctorSelect');
  const dateInp = document.getElementById('orderLabDate');
  const notesInp = document.getElementById('orderLabNotes');

  if (patSelect && appState.patients.length > 0) {
    patSelect.innerHTML = appState.patients.map(p => `
      <option value="${p.id}">${p.full_name} (MRN: UTK-${1000 + p.id})</option>
    `).join('');
  }

  if (docSelect && appState.doctors.length > 0) {
    docSelect.innerHTML = appState.doctors.map(d => `
      <option value="${d.id}">${d.full_name} — ${d.specialization}</option>
    `).join('');
    if (appState.user && appState.user.role === 'doctor') {
      const myDoc = appState.doctors.find(d => d.email === appState.user.email || d.user_id === appState.user.id);
      if (myDoc) docSelect.value = myDoc.id;
    }
  }

  if (dateInp) dateInp.value = new Date().toISOString().split('T')[0];
  if (notesInp) notesInp.value = '';

  openModal('modalOrderLabTest');
}

// Generate Billing Invoice Modal Controls
async function openCreateInvoiceModal() {
  await ensurePatientsAndDoctorsLoaded();
  const patSelect = document.getElementById('invPatientSelect');
  const container = document.getElementById('invItemsContainer');
  const discInp = document.getElementById('invDiscountInput');
  const paidInp = document.getElementById('invAmountPaidInput');

  if (patSelect && appState.patients.length > 0) {
    patSelect.innerHTML = appState.patients.map(p => `
      <option value="${p.id}">${p.full_name} (MRN: UTK-${1000 + p.id}, ${p.phone})</option>
    `).join('');
  }

  if (discInp) discInp.value = '0.00';
  if (paidInp) paidInp.value = '0.00';

  if (container) {
    container.innerHTML = '';
    addInvoiceItemRow('Comprehensive OPD Consultation & Clinical Assessment', 1, 800.00);
  }

  openModal('modalCreateInvoice');
}

function addInvoiceItemRow(desc = '', qty = 1, price = 500.00) {
  const container = document.getElementById('invItemsContainer');
  if (!container) return;
  const rowId = `inv-row-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  const div = document.createElement('div');
  div.id = rowId;
  div.style.display = 'grid';
  div.style.gridTemplateColumns = '3fr 1fr 1fr auto';
  div.style.gap = '8px';
  div.style.alignItems = 'center';
  div.innerHTML = `
    <input type="text" class="form-control inv-item-desc" placeholder="Service or Medication Description" value="${desc}" required style="font-size:13px; padding:6px 10px;">
    <input type="number" min="1" class="form-control inv-item-qty" placeholder="Qty" value="${qty}" required style="font-size:13px; padding:6px 10px;">
    <input type="number" min="0" step="0.01" class="form-control inv-item-price" placeholder="Price (₹)" value="${price}" required style="font-size:13px; padding:6px 10px;">
    <button type="button" class="btn btn-outline btn-sm" onclick="document.getElementById('${rowId}').remove()" style="color:#EF4444; border-color:#FCA5A5; padding:6px 10px;">✕</button>
  `;
  container.appendChild(div);
}

// Add New Medicine Modal Controls
function openAddMedicineModal() {
  const nameInp = document.getElementById('newMedName');
  const genInp = document.getElementById('newMedGeneric');
  const catInp = document.getElementById('newMedCategory');
  const reorderInp = document.getElementById('newMedReorder');

  if (nameInp) nameInp.value = '';
  if (genInp) genInp.value = '';
  if (catInp) catInp.value = '';
  if (reorderInp) reorderInp.value = '50';

  openModal('modalAddMedicine');
}

async function ensurePatientsAndDoctorsLoaded() {
  if (appState.user.role !== 'patient') {
    if (!appState.patients || appState.patients.length === 0) {
      const data = await apiRequest('/patients/?page=1&page_size=50');
      appState.patients = data.items || [];
    }
  }
  if (!appState.doctors || appState.doctors.length === 0) {
    const data = await apiRequest('/doctors/?page=1&page_size=30');
    appState.doctors = data.items || [];
  }
}

function populateAppointmentDropdowns() {
  const patSelect = document.getElementById('bookPatientSelect');
  const docSelect = document.getElementById('bookDoctorSelect');

  if (appState.user.role === 'patient') {
    // If patient, find patient record for self
    if (patSelect) {
      patSelect.innerHTML = `<option value="1" selected>${appState.user.full_name} (Self)</option>`;
      patSelect.disabled = true;
    }
  } else {
    if (patSelect) {
      patSelect.disabled = false;
      if (appState.patients.length > 0) {
        patSelect.innerHTML = appState.patients.map(p => `
          <option value="${p.id}">${p.full_name} (MRN: UTK-${1000 + p.id}, ${p.gender})</option>
        `).join('');
      }
    }
  }

  if (docSelect && appState.doctors.length > 0) {
    docSelect.innerHTML = appState.doctors.map(d => `
      <option value="${d.id}">${d.full_name} — ${d.specialization} (${formatINR(d.consultation_fee)})</option>
    `).join('');
  }
}

// Event Listeners and Initialization
document.addEventListener('DOMContentLoaded', async () => {
  applyHospitalBranding();
  populateGatePatientDropdown();

  // 0. Wire Fullscreen Login Gate Form Submission
  const loginGateForm = document.getElementById('loginGateForm');
  if (loginGateForm) {
    loginGateForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const email = document.getElementById('loginGateEmail').value.trim();
      const pwd = document.getElementById('loginGatePassword').value;
      await authenticateUser(email, pwd);
    });
  }

  // 0b. Wire Modal Login Form Submission
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const email = document.getElementById('loginEmailInput').value.trim();
      const pwd = document.getElementById('loginPasswordInput').value;
      await authenticateUser(email, pwd);
    });
  }

  // Check authentication session
  if (!appState.token || !appState.user) {
    // Must login first as requested!
    openLoginScreen('admin');
  } else {
    closeLoginScreen();
    updateUserUI();
    applyRolePermissions(appState.user.role || 'admin');
    switchPage('dashboard');
  }

  // 1. Book appointment form submission
  const bookForm = document.getElementById('bookAppointmentForm');
  if (bookForm) {
    bookForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const patientId = parseInt(document.getElementById('bookPatientSelect').value, 10);
      const doctorId = parseInt(document.getElementById('bookDoctorSelect').value, 10);
      const appDate = document.getElementById('bookDateInput').value;
      const slot = document.getElementById('bookSlotSelect').value;
      const reason = document.getElementById('bookReasonInput').value;

      try {
        await apiRequest('/appointments/', 'POST', {
          patient_id: patientId,
          doctor_id: doctorId,
          appointment_date: appDate,
          time_slot: slot,
          reason: reason || 'Routine OPD Consultation'
        });
        showToast('Consultation appointment successfully booked!', 'success');
        closeModal('modalBookAppointment');
        loadAppointmentsData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 2. Register patient form submission
  const regForm = document.getElementById('registerPatientForm');
  if (regForm) {
    regForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const name = document.getElementById('regName').value;
      const dob = document.getElementById('regDob').value;
      const gender = document.getElementById('regGender').value;
      const phone = document.getElementById('regPhone').value;
      const address = document.getElementById('regAddress').value;
      const email = document.getElementById('regEmail').value;
      const blood = document.getElementById('regBlood').value;
      const allergies = document.getElementById('regAllergies').value;
      const password = document.getElementById('regPassword') ? document.getElementById('regPassword').value : 'patient123';
      const emergency = document.getElementById('regEmergency') ? document.getElementById('regEmergency').value : '';
      const history = document.getElementById('regMedicalHistory') ? document.getElementById('regMedicalHistory').value : '';

      try {
        const created = await apiRequest('/patients/', 'POST', {
          full_name: name,
          date_of_birth: dob,
          gender: gender,
          phone: phone,
          address: address || 'Bhubaneswar, Odisha',
          email: email || null,
          password: password || 'patient123',
          blood_group: blood,
          allergies: allergies || 'None',
          emergency_contact: emergency || null,
          medical_history: history || null,
          create_portal_account: true,
        });
        showToast(`Patient ${name} enrolled! Portal Login: ${email} (Password: ${password || 'patient123'})`, 'success');
        closeModal('modalRegisterPatient');
        loadPatientsData();
        loadDashboardData();
        fetchAndRenderPatientDirectory();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 3. Complete visit form submission
  const compForm = document.getElementById('completeVisitForm');
  if (compForm) {
    compForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const appId = parseInt(document.getElementById('compAppointmentId').value, 10);
      const diagnosis = document.getElementById('compDiagnosisInput').value;
      const notes = document.getElementById('compNotesInput').value;

      try {
        await apiRequest(`/appointments/${appId}/complete`, 'POST', {
          diagnosis: diagnosis,
          notes: notes || 'Clinical recommendations provided.'
        });
        showToast(`Appointment #${appId} finalized and diagnosis saved!`, 'success');
        closeModal('modalCompleteVisit');
        loadAppointmentsData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 4. Record invoice payment form submission
  const payForm = document.getElementById('recordPaymentForm');
  if (payForm) {
    payForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const invId = parseInt(document.getElementById('payInvoiceId').value, 10);
      const method = document.getElementById('payMethodSelect').value;
      const amountPaid = parseFloat(document.getElementById('payAmountInput').value);

      const inv = appState.invoices.find(i => i.id === invId);
      const currentPaid = inv ? inv.amount_paid : 0;
      const totalPaid = currentPaid + amountPaid;

      try {
        await apiRequest(`/billing/invoices/${invId}`, 'PATCH', {
          amount_paid: totalPaid,
          payment_method: method
        });
        showToast(`Payment of ${formatINR(amountPaid)} recorded successfully for Invoice #${invId}!`, 'success');
        closeModal('modalRecordPayment');
        loadBillingData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 5. Pharmacy stock-in form submission
  const stockForm = document.getElementById('stockInForm');
  if (stockForm) {
    stockForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const medId = parseInt(document.getElementById('stockMedId').value, 10);
      const batchNo = document.getElementById('stockBatchNo').value;
      const expDate = document.getElementById('stockExpiryDate').value;
      const qty = parseInt(document.getElementById('stockQuantity').value, 10);
      const cost = parseFloat(document.getElementById('stockUnitCost').value);
      const supplier = document.getElementById('stockSupplier').value;

      try {
        await apiRequest('/pharmacy/stock-in', 'POST', {
          medicine_id: medId,
          batch_no: batchNo,
          expiry_date: expDate,
          quantity: qty,
          unit_cost: cost,
          supplier: supplier
        });
        showToast(`Batch ${batchNo} (${qty} units) received into pharmacy inventory!`, 'success');
        closeModal('modalStockIn');
        loadPharmacyData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 6. Update lab test form submission
  const labForm = document.getElementById('updateLabForm');
  if (labForm) {
    labForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const testId = parseInt(document.getElementById('labTestId').value, 10);
      const findings = document.getElementById('labFindingsInput').value;
      const testStatus = document.getElementById('labStatusSelect').value;
      const isCritical = document.getElementById('labCriticalInput').checked;

      try {
        await apiRequest(`/lab-tests/${testId}`, 'PATCH', {
          findings: findings,
          status: testStatus,
          critical_value: isCritical
        });
        showToast(`Lab report #${testId} findings successfully updated!`, 'success');
        closeModal('modalUpdateLab');
        loadLabReportsData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 7. Hospital branding settings form submission
  const hospSettingsForm = document.getElementById('hospitalSettingsForm');
  if (hospSettingsForm) {
    hospSettingsForm.addEventListener('submit', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const name = document.getElementById('settingHospitalNameInput').value.trim();
      const subtitle = document.getElementById('settingHospitalSubtitleInput').value.trim();
      const address = document.getElementById('settingHospitalAddressInput').value.trim();
      const phone = document.getElementById('settingHospitalPhoneInput').value.trim();
      const email = document.getElementById('settingHospitalEmailInput').value.trim();

      appState.hospitalSettings = {
        name: name || 'Utkal Hospital & Medical Research Centre',
        shortName: name.split('&')[0].trim() || 'Utkal Hospital',
        subtitle: subtitle || 'Premier Multi-Specialty Tertiary Care & Research Institute',
        address: address,
        phone: phone,
        email: email,
      };

      localStorage.setItem('utkal_hospital_branding', JSON.stringify(appState.hospitalSettings));
      applyHospitalBranding();
      showToast('Hospital branding & settings successfully saved and applied globally!', 'success');
    });
  }

  // 8. User profile update form submission
  const profileForm = document.getElementById('profileUpdateForm');
  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const fullName = document.getElementById('settingProfileName').value.trim();
      const phone = document.getElementById('settingProfilePhone').value.trim();

      try {
        const updated = await apiRequest('/users/me', 'PATCH', {
          full_name: fullName,
          phone: phone || null,
        });
        appState.user = updated;
        localStorage.setItem('medflow_user', JSON.stringify(updated));
        updateUserUI();
        showToast('Your account profile has been updated!', 'success');
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 9. Change password form submission
  const pwdForm = document.getElementById('changePasswordForm');
  if (pwdForm) {
    pwdForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const currentPwd = document.getElementById('pwdCurrent').value;
      const newPwd = document.getElementById('pwdNew').value;
      const confirmPwd = document.getElementById('pwdConfirm').value;

      if (newPwd !== confirmPwd) {
        showToast('New password and confirmation password do not match!', 'error');
        return;
      }

      try {
        await apiRequest('/users/change-password', 'POST', {
          current_password: currentPwd,
          new_password: newPwd,
        });
        showToast('Password changed successfully!', 'success');
        pwdForm.reset();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 9a. Issue Prescription form submission
  const prescForm = document.getElementById('createPrescriptionForm');
  if (prescForm) {
    prescForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const patientId = parseInt(document.getElementById('prescPatientSelect').value, 10);
      const doctorId = parseInt(document.getElementById('prescDoctorSelect').value, 10);
      const instructions = document.getElementById('prescInstructions').value;

      const container = document.getElementById('prescItemsContainer');
      const rows = container.querySelectorAll('div[id^="presc-row-"]');
      const items = [];
      rows.forEach(r => {
        const name = r.querySelector('.presc-med-name').value.trim();
        const dosage = r.querySelector('.presc-med-dosage').value.trim();
        const freq = r.querySelector('.presc-med-freq').value.trim();
        const dur = r.querySelector('.presc-med-duration').value.trim();
        const qty = parseInt(r.querySelector('.presc-med-qty').value, 10) || 1;
        const notes = r.querySelector('.presc-med-notes').value.trim();
        if (name) {
          items.push({
            medicine_name: name,
            dosage: dosage || '500mg',
            frequency: freq || 'Twice daily',
            duration: dur || '5 days',
            quantity: qty,
            notes: notes || null
          });
        }
      });

      if (items.length === 0) {
        showToast('Please add at least one medication to the prescription!', 'warning');
        return;
      }

      try {
        const created = await apiRequest('/prescriptions/', 'POST', {
          patient_id: patientId,
          doctor_id: doctorId,
          instructions: instructions,
          items: items
        });
        showToast(`Prescription ℞ #${created.id} issued successfully!`, 'success');
        closeModal('modalCreatePrescription');
        loadPrescriptionsData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 9b. Order Lab Test form submission
  const orderLabForm = document.getElementById('orderLabTestForm');
  if (orderLabForm) {
    orderLabForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const patientId = parseInt(document.getElementById('orderLabPatientSelect').value, 10);
      const doctorId = parseInt(document.getElementById('orderLabDoctorSelect').value, 10);
      const testType = document.getElementById('orderLabTypeSelect').value;
      const scheduledDate = document.getElementById('orderLabDate').value;
      const notes = document.getElementById('orderLabNotes').value;

      try {
        await apiRequest('/lab-tests/', 'POST', {
          patient_id: patientId,
          doctor_id: doctorId,
          test_type: testType,
          scheduled_date: scheduledDate,
          notes: notes,
          critical_value: false
        });
        showToast(`Diagnostic ${testType.toUpperCase()} examination scheduled!`, 'success');
        closeModal('modalOrderLabTest');
        loadLabReportsData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 9c. Create Invoice form submission
  const createInvForm = document.getElementById('createInvoiceForm');
  if (createInvForm) {
    createInvForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const patientId = parseInt(document.getElementById('invPatientSelect').value, 10);
      const discount = parseFloat(document.getElementById('invDiscountInput').value) || 0.0;
      const amountPaid = parseFloat(document.getElementById('invAmountPaidInput').value) || 0.0;
      const paymentMethod = document.getElementById('invPaymentMethodSelect').value;

      const container = document.getElementById('invItemsContainer');
      const rows = container.querySelectorAll('div[id^="inv-row-"]');
      const items = [];
      rows.forEach(r => {
        const desc = r.querySelector('.inv-item-desc').value.trim();
        const qty = parseInt(r.querySelector('.inv-item-qty').value, 10) || 1;
        const price = parseFloat(r.querySelector('.inv-item-price').value) || 0.0;
        if (desc) {
          items.push({
            description: desc,
            quantity: qty,
            unit_price: price
          });
        }
      });

      if (items.length === 0) {
        showToast('Please add at least one billable item!', 'warning');
        return;
      }

      try {
        const inv = await apiRequest('/billing/invoices', 'POST', {
          patient_id: patientId,
          discount: discount,
          amount_paid: amountPaid,
          payment_method: paymentMethod,
          items: items
        });
        showToast(`Invoice ${inv.invoice_number} created successfully! Total: ${formatINR(inv.total)}`, 'success');
        closeModal('modalCreateInvoice');
        loadBillingData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 9d. Add Medicine to catalog form submission
  const addMedForm = document.getElementById('addMedicineForm');
  if (addMedForm) {
    addMedForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const name = document.getElementById('newMedName').value.trim();
      const generic = document.getElementById('newMedGeneric').value.trim();
      const category = document.getElementById('newMedCategory').value.trim();
      const unit = document.getElementById('newMedUnit').value.trim();
      const reorder = parseInt(document.getElementById('newMedReorder').value, 10) || 50;

      try {
        await apiRequest('/pharmacy/medicines', 'POST', {
          name: name,
          generic_name: generic,
          category: category,
          unit: unit,
          reorder_level: reorder
        });
        showToast(`Medicine '${name}' added to pharmaceutical formulary!`, 'success');
        closeModal('modalAddMedicine');
        loadPharmacyData();
        loadDashboardData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // 10. Live Global Search Input
  const searchInput = document.getElementById('globalSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      if (appState.currentPage === 'dashboard') {
        handleDashboardSearch(q);
      } else if (appState.currentPage === 'patients') {
        loadPatientsData(q);
      } else if (appState.currentPage === 'appointments') {
        renderAppointmentsTable(appState.appointments, q);
      } else if (appState.currentPage === 'doctors') {
        renderDoctorsGrid(appState.doctors, q);
      } else if (appState.currentPage === 'prescriptions') {
        renderPrescriptionsTable(appState.prescriptions, q);
      } else if (appState.currentPage === 'lab-reports') {
        renderLabReportsTable(appState.labTests, q);
      } else if (appState.currentPage === 'billing') {
        renderBillingTable(appState.invoices, q);
      } else if (appState.currentPage === 'pharmacy') {
        renderPharmacyTable(appState.medicines, q);
      }
    });

    // Also trigger on focus if query already exists
    searchInput.addEventListener('focus', (e) => {
      const q = e.target.value.trim();
      if (q && appState.currentPage === 'dashboard') {
        handleDashboardSearch(q);
      }
    });
  }

  // Load saved theme on DOM ready
  loadSavedTheme();
});

// ========================================================
// AUTH GATE MODE SWITCHER (SIGN IN vs SIGN UP)
// ========================================================

function switchAuthGateMode(mode) {
  const tabIn = document.getElementById('authTabSignIn');
  const tabUp = document.getElementById('authTabSignUp');
  const secIn = document.getElementById('gateSignInSection');
  const secUp = document.getElementById('gateSignUpSection');
  const alertBox = document.getElementById('loginGateAlert');
  if (alertBox) alertBox.style.display = 'none';

  if (mode === 'signup') {
    if (tabIn) tabIn.classList.remove('active');
    if (tabUp) tabUp.classList.add('active');
    if (secIn) secIn.style.display = 'none';
    if (secUp) secUp.style.display = 'block';
  } else {
    if (tabIn) tabIn.classList.add('active');
    if (tabUp) tabUp.classList.remove('active');
    if (secIn) secIn.style.display = 'block';
    if (secUp) secUp.style.display = 'none';
  }
}

async function handleSignUpSubmit(e) {
  e.preventDefault();
  const alertBox = document.getElementById('loginGateAlert');
  const btn = document.getElementById('signupGateSubmitBtn');
  if (alertBox) alertBox.style.display = 'none';

  const fullName = document.getElementById('signupFullName').value.trim();
  const email = document.getElementById('signupEmail').value.trim().toLowerCase();
  const phone = document.getElementById('signupPhone').value.trim();
  const role = document.getElementById('signupRole').value;
  const password = document.getElementById('signupPassword').value;
  const confirmPassword = document.getElementById('signupConfirmPassword').value;

  if (password !== confirmPassword) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.innerHTML = '<strong>Password Mismatch:</strong> Passwords do not match. Please verify.';
    }
    return;
  }

  if (password.length < 6) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.innerHTML = '<strong>Invalid Password:</strong> Password must be at least 6 characters.';
    }
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = 'Creating account...';
  }

  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
        role,
        phone
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Registration failed. Email may already exist.');
    }

    showToast(`Account created successfully! Signing you in as ${fullName}...`, 'success');
    // Automatically authenticate with new credentials
    await authenticateUser(email, password);
  } catch (err) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.innerHTML = `<strong>Registration Failed:</strong> ${err.message}`;
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span class="blade-btn-text">Create Account & Sign In</span> <span class="blade-btn-arrow">→</span>';
    }
  }
}

// ========================================================
// DASHBOARD LIVE OMNISEARCH & QUICK FIND
// ========================================================

function handleDashboardSearch(q) {
  const dropdown = document.getElementById('globalSearchDropdown');
  if (!dropdown) return;

  if (!q) {
    dropdown.style.display = 'none';
    dropdown.innerHTML = '';
    return;
  }

  const query = q.toLowerCase();
  
  // Search Patients
  const matchPatients = (appState.patients || []).filter(p => 
    (p.full_name && p.full_name.toLowerCase().includes(query)) ||
    (p.phone && p.phone.includes(query)) ||
    (p.blood_group && p.blood_group.toLowerCase().includes(query)) ||
    (p.city && p.city.toLowerCase().includes(query))
  ).slice(0, 4);

  // Search Doctors
  const matchDoctors = (appState.doctors || []).filter(d => 
    (d.name && d.name.toLowerCase().includes(query)) ||
    (d.specialization && d.specialization.toLowerCase().includes(query))
  ).slice(0, 3);

  // Search Appointments
  const matchAppts = (appState.appointments || []).filter(a => 
    (a.patient_name && a.patient_name.toLowerCase().includes(query)) ||
    (a.doctor_name && a.doctor_name.toLowerCase().includes(query)) ||
    (a.status && a.status.toLowerCase().includes(query))
  ).slice(0, 3);

  // Search Medicines
  const matchMeds = (appState.medicines || []).filter(m => 
    (m.name && m.name.toLowerCase().includes(query)) ||
    (m.generic_name && m.generic_name.toLowerCase().includes(query)) ||
    (m.category && m.category.toLowerCase().includes(query))
  ).slice(0, 3);

  let html = '';
  const total = matchPatients.length + matchDoctors.length + matchAppts.length + matchMeds.length;

  if (total === 0) {
    html = `<div class="search-empty">No clinical records found matching "<strong>${q}</strong>"</div>`;
  } else {
    html += `<div class="search-header-count">SEARCH RESULTS (${total})</div>`;

    if (matchPatients.length > 0) {
      html += `<div class="search-cat-title">Patients Directory (${matchPatients.length})</div>`;
      matchPatients.forEach(p => {
        html += `
          <div class="search-result-item" onclick="selectSearchPatient(${p.id})">
            <div class="search-res-icon">👤</div>
            <div style="flex:1;">
              <div class="search-res-name">${p.full_name} <span class="search-badge">${p.blood_group || 'O+'}</span></div>
              <div class="search-res-sub">Phone: ${p.phone} • ${p.city || 'Bhubaneswar'}</div>
            </div>
            <button class="btn btn-outline btn-sm">View Chart</button>
          </div>
        `;
      });
    }

    if (matchDoctors.length > 0) {
      html += `<div class="search-cat-title">Consultant Doctors (${matchDoctors.length})</div>`;
      matchDoctors.forEach(d => {
        html += `
          <div class="search-result-item" onclick="selectSearchDoctor('${d.name}')">
            <div class="search-res-icon" style="color:var(--primary);">🩺</div>
            <div style="flex:1;">
              <div class="search-res-name">${d.name}</div>
              <div class="search-res-sub">${d.specialization} • Fee: ₹${d.consultation_fee}</div>
            </div>
            <button class="btn btn-outline btn-sm">View Roster</button>
          </div>
        `;
      });
    }

    if (matchAppts.length > 0) {
      html += `<div class="search-cat-title">Appointments & Visits (${matchAppts.length})</div>`;
      matchAppts.forEach(a => {
        html += `
          <div class="search-result-item" onclick="switchPage('appointments')">
            <div class="search-res-icon" style="color:#3B82F6;">📅</div>
            <div style="flex:1;">
              <div class="search-res-name">${a.patient_name || 'Patient'} with ${a.doctor_name || 'Consultant'}</div>
              <div class="search-res-sub">${a.appointment_date ? a.appointment_date.substring(0, 10) : ''} • Status: ${a.status}</div>
            </div>
            <span class="badge badge-${a.status}">${a.status}</span>
          </div>
        `;
      });
    }

    if (matchMeds.length > 0) {
      html += `<div class="search-cat-title">Pharmacy Formulary (${matchMeds.length})</div>`;
      matchMeds.forEach(m => {
        html += `
          <div class="search-result-item" onclick="switchPage('pharmacy')">
            <div class="search-res-icon" style="color:#F59E0B;">💊</div>
            <div style="flex:1;">
              <div class="search-res-name">${m.name}</div>
              <div class="search-res-sub">${m.generic_name || m.category} • Stock: ${m.total_quantity || 0} ${m.unit}</div>
            </div>
            <button class="btn btn-outline btn-sm">Dispensary</button>
          </div>
        `;
      });
    }
  }

  dropdown.innerHTML = html;
  dropdown.style.display = 'block';
}

function selectSearchPatient(patientId) {
  const dropdown = document.getElementById('globalSearchDropdown');
  if (dropdown) dropdown.style.display = 'none';
  const inp = document.getElementById('globalSearchInput');
  if (inp) inp.value = '';
  openPatientChart(patientId);
}

function selectSearchDoctor(docName) {
  const dropdown = document.getElementById('globalSearchDropdown');
  if (dropdown) dropdown.style.display = 'none';
  const inp = document.getElementById('globalSearchInput');
  if (inp) inp.value = '';
  switchPage('doctors');
  loadDoctorsData(docName);
}

// Close search dropdown on click outside or Escape
document.addEventListener('click', (e) => {
  const searchBox = document.querySelector('.search-box');
  const dropdown = document.getElementById('globalSearchDropdown');
  if (searchBox && dropdown && !searchBox.contains(e.target)) {
    dropdown.style.display = 'none';
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const dropdown = document.getElementById('globalSearchDropdown');
    if (dropdown) dropdown.style.display = 'none';
  }
});

// ========================================================
// THEME CUSTOMIZATION ENGINE (LIGHT, DARK, RED-BLACK, NEON-BLUE, CUSTOM)
// ========================================================

const THEME_CONFIGS = {
  light: {
    name: 'Clinical Light',
    bodyClass: 'theme-light',
    vars: {
      '--primary': '#0D9488',
      '--primary-hover': '#0F766E',
      '--secondary': '#2563EB',
      '--secondary-hover': '#1D4ED8',
      '--bg-main': '#F1F5F9',
      '--bg-card': '#FFFFFF',
      '--bg-subtle': '#F8FAFC',
      '--text-primary': '#0F172A',
      '--text-secondary': '#334155',
      '--text-muted': '#64748B',
      '--border-light': '#E2E8F0',
      '--laser-primary': '#0D9488',
      '--terminal-black': '#0F172A',
    }
  },
  dark: {
    name: 'Midnight Dark',
    bodyClass: 'theme-dark',
    vars: {
      '--primary': '#00E5FF',
      '--primary-hover': '#00B4D8',
      '--secondary': '#38BDF8',
      '--secondary-hover': '#0284C7',
      '--bg-main': '#070B10',
      '--bg-card': '#0E141E',
      '--bg-subtle': '#131B27',
      '--text-primary': '#F8FAFC',
      '--text-secondary': '#CBD5E1',
      '--text-muted': '#64748B',
      '--border-light': '#1C2838',
      '--laser-primary': '#00E5FF',
      '--terminal-black': '#05080D',
    }
  },
  'red-black': {
    name: 'Trauma Red & Black',
    bodyClass: 'theme-red-black',
    vars: {
      '--primary': '#EF4444',
      '--primary-hover': '#DC2626',
      '--secondary': '#B91C1C',
      '--secondary-hover': '#991B1B',
      '--bg-main': '#080808',
      '--bg-card': '#111111',
      '--bg-subtle': '#181818',
      '--text-primary': '#F8FAFC',
      '--text-secondary': '#E5E7EB',
      '--text-muted': '#9CA3AF',
      '--border-light': '#262626',
      '--laser-primary': '#EF4444',
      '--terminal-black': '#000000',
    }
  },
  'neon-blue': {
    name: 'Neon & Blue',
    bodyClass: 'theme-neon-blue',
    vars: {
      '--primary': '#00F5A0',
      '--primary-hover': '#00D88B',
      '--secondary': '#2563EB',
      '--secondary-hover': '#1D4ED8',
      '--bg-main': '#050B14',
      '--bg-card': '#0A1220',
      '--bg-subtle': '#0F1A2C',
      '--text-primary': '#F8FAFC',
      '--text-secondary': '#CBD5E1',
      '--text-muted': '#64748B',
      '--border-light': '#172437',
      '--laser-primary': '#00F5A0',
      '--terminal-black': '#03070E',
    }
  },
  'amber-charcoal': {
    name: 'Amber & Charcoal',
    bodyClass: 'theme-amber-charcoal',
    vars: {
      '--primary': '#F59E0B',
      '--primary-hover': '#D97706',
      '--secondary': '#EAB308',
      '--secondary-hover': '#CA8A04',
      '--bg-main': '#0D0F12',
      '--bg-card': '#14171D',
      '--bg-subtle': '#1B2028',
      '--text-primary': '#F8FAFC',
      '--text-secondary': '#D1D5DB',
      '--text-muted': '#6B7280',
      '--border-light': '#252B36',
      '--laser-primary': '#F59E0B',
      '--terminal-black': '#080A0C',
    }
  },
  'royal-cyan': {
    name: 'Royal Navy & Cyan',
    bodyClass: 'theme-royal-cyan',
    vars: {
      '--primary': '#38BDF8',
      '--primary-hover': '#0284C7',
      '--secondary': '#6366F1',
      '--secondary-hover': '#4F46E5',
      '--bg-main': '#0A1120',
      '--bg-card': '#0F1A30',
      '--bg-subtle': '#162444',
      '--text-primary': '#F8FAFC',
      '--text-secondary': '#CBD5E1',
      '--text-muted': '#64748B',
      '--border-light': '#1E3258',
      '--laser-primary': '#38BDF8',
      '--terminal-black': '#060B14',
    }
  }
};

function applyPresetTheme(themeKey) {
  const cfg = THEME_CONFIGS[themeKey] || THEME_CONFIGS.light;
  const root = document.documentElement;

  for (const [prop, val] of Object.entries(cfg.vars)) {
    root.style.setProperty(prop, val);
  }

  document.body.className = cfg.bodyClass;

  document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
  const activeCard = document.getElementById(`themeCard-${themeKey}`);
  if (activeCard) activeCard.classList.add('active');

  const badge = document.getElementById('activeThemeBadge');
  if (badge) badge.innerText = `Active: ${cfg.name}`;

  localStorage.setItem('utkal_hospital_theme', JSON.stringify({
    mode: 'preset',
    key: themeKey,
    name: cfg.name,
    vars: cfg.vars,
    bodyClass: cfg.bodyClass
  }));

  showToast(`Theme switched to ${cfg.name}`, 'success');
}

function updateCustomColorPreview() {
  const p = document.getElementById('pickerPrimaryColor').value;
  const s = document.getElementById('pickerSecondaryColor').value;
  const textP = document.getElementById('textPrimaryColor');
  const textS = document.getElementById('textSecondaryColor');
  if (textP) textP.value = p;
  if (textS) textS.value = s;
}

function syncColorInput(type, val) {
  if (type === 'primary') {
    const picker = document.getElementById('pickerPrimaryColor');
    if (picker && /^#[0-9A-Fa-f]{6}$/.test(val)) picker.value = val;
  } else if (type === 'secondary') {
    const picker = document.getElementById('pickerSecondaryColor');
    if (picker && /^#[0-9A-Fa-f]{6}$/.test(val)) picker.value = val;
  }
}

function applyCustomThemeFromStudio() {
  const pColor = document.getElementById('pickerPrimaryColor').value || '#0D9488';
  const sColor = document.getElementById('pickerSecondaryColor').value || '#2563EB';
  const bgMode = document.getElementById('selectBackgroundMode').value || 'light';

  const root = document.documentElement;
  root.style.setProperty('--primary', pColor);
  root.style.setProperty('--primary-hover', pColor);
  root.style.setProperty('--laser-primary', pColor);
  root.style.setProperty('--secondary', sColor);
  root.style.setProperty('--secondary-hover', sColor);

  let bgMain = '#F1F5F9';
  let bgCard = '#FFFFFF';
  let bgSubtle = '#F8FAFC';
  let textP = '#0F172A';
  let textS = '#334155';
  let borderL = '#CBD5E1';
  let termB = '#0F172A';
  let bClass = 'theme-custom-light';

  if (bgMode === 'dark') {
    bgMain = '#070B10';
    bgCard = '#0D131C';
    bgSubtle = '#121A26';
    textP = '#F8FAFC';
    textS = '#CBD5E1';
    borderL = '#1C2838';
    termB = '#05080D';
    bClass = 'theme-custom-dark';
  } else if (bgMode === 'black') {
    bgMain = '#000000';
    bgCard = '#0D0D0D';
    bgSubtle = '#161616';
    textP = '#FFFFFF';
    textS = '#E5E7EB';
    borderL = '#262626';
    termB = '#000000';
    bClass = 'theme-custom-black';
  }

  root.style.setProperty('--bg-main', bgMain);
  root.style.setProperty('--bg-card', bgCard);
  root.style.setProperty('--bg-subtle', bgSubtle);
  root.style.setProperty('--text-primary', textP);
  root.style.setProperty('--text-secondary', textS);
  root.style.setProperty('--border-light', borderL);
  root.style.setProperty('--terminal-black', termB);

  document.body.className = bClass;

  document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
  const badge = document.getElementById('activeThemeBadge');
  if (badge) badge.innerText = `Active: Custom (${pColor} / ${bgMode.toUpperCase()})`;

  localStorage.setItem('utkal_hospital_theme', JSON.stringify({
    mode: 'custom',
    pColor,
    sColor,
    bgMode,
    bClass,
    vars: {
      '--primary': pColor,
      '--primary-hover': pColor,
      '--laser-primary': pColor,
      '--secondary': sColor,
      '--secondary-hover': sColor,
      '--bg-main': bgMain,
      '--bg-card': bgCard,
      '--bg-subtle': bgSubtle,
      '--text-primary': textP,
      '--text-secondary': textS,
      '--border-light': borderL,
      '--terminal-black': termB,
    }
  }));

  showToast('Custom hospital theme applied successfully!', 'success');
}

function resetToDefaultTheme() {
  localStorage.removeItem('utkal_hospital_theme');
  applyPresetTheme('light');
}

function loadSavedTheme() {
  const saved = localStorage.getItem('utkal_hospital_theme');
  if (!saved) return;
  try {
    const data = JSON.parse(saved);
    const root = document.documentElement;
    if (data.vars) {
      for (const [prop, val] of Object.entries(data.vars)) {
        root.style.setProperty(prop, val);
      }
    }
    if (data.bodyClass || data.bClass) {
      document.body.className = data.bodyClass || data.bClass;
    }
    const badge = document.getElementById('activeThemeBadge');
    if (badge && data.name) badge.innerText = `Active: ${data.name}`;

    if (data.mode === 'preset' && data.key) {
      document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
      const activeCard = document.getElementById(`themeCard-${data.key}`);
      if (activeCard) activeCard.classList.add('active');
    }
  } catch (e) {
    console.warn('Error applying saved theme:', e);
  }
}

// Call immediately on script execution
loadSavedTheme();
