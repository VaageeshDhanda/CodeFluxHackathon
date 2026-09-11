const API_URL = 'http://127.0.0.1:8000';
const LPU_UNIV_ID = 1;

// --- Auth & Session Helpers ---
function getLoggedInUser() {
    const userStr = localStorage.getItem('hostlehive_user');
    return userStr ? JSON.parse(userStr) : null;
}

function checkAuthGuard() {
    const user = getLoggedInUser();
    const path = window.location.pathname;
    if (!user && !path.includes('login.html') && !path.includes('signup.html')) {
        window.location.href = 'login.html';
    }
}

async function handleSecureLogin() {
    const emailInput = document.getElementById('login-email').value.trim();
    const passwordInput = document.getElementById('login-password').value;
    const errorBanner = document.getElementById('error-banner');
    
    if(errorBanner) errorBanner.classList.add('hidden');

    if (!emailInput || !passwordInput) {
        if(errorBanner) {
            errorBanner.textContent = "Please fill in all required fields.";
            errorBanner.classList.remove('hidden');
        }
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: emailInput, password: passwordInput })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('hostlehive_user', JSON.stringify(data.user));
            
            if (data.user.is_admin) {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'index.html';
            }
        } else {
            if(errorBanner) {
                errorBanner.textContent = data.detail || "Authentication failed.";
                errorBanner.classList.remove('hidden');
            }
        }
    } catch (error) {
        if(errorBanner) {
            errorBanner.textContent = "Unable to connect to server.";
            errorBanner.classList.remove('hidden');
        }
    }
}

async function handleSignup() {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const roll = document.getElementById('signup-roll').value;

    if (!name || !email || !roll) return alert("All fields are required");

    const mockUser = { id: 2, name: name, email: email, university_id: LPU_UNIV_ID, is_admin: false };
    localStorage.setItem('hostlehive_user', JSON.stringify(mockUser));
    alert("Account registered successfully!");
    window.location.href = 'index.html';
}

function handleLogout() {
    localStorage.removeItem('hostlehive_user');
    window.location.href = 'login.html';
}

// --- Mode Switcher Logic ---
let isPartnerMode = false;

function initHomeModeUI() {
    const savedMode = localStorage.getItem('hostlehive_mode') === 'partner';
    if (savedMode) toggleUserMode(true);
}

function toggleUserMode(forcedState = null) {
    isPartnerMode = forcedState !== null ? forcedState : !isPartnerMode;
    localStorage.setItem('hostlehive_mode', isPartnerMode ? 'partner' : 'customer');

    const slider = document.getElementById('mode-pill-slider');
    const lblCust = document.getElementById('label-customer');
    const lblPart = document.getElementById('label-partner');
    const viewCust = document.getElementById('view-customer-home');
    const viewPart = document.getElementById('view-partner-home');

    if (isPartnerMode) {
        if (slider) slider.className = "mode-pill-slider partner";
        if (lblCust) lblCust.classList.remove('active');
        if (lblPart) lblPart.classList.add('active');
        if (viewCust) viewCust.classList.add('hidden');
        if (viewPart) viewPart.classList.remove('hidden');
        loadAvailablePartnerJobs();
    } else {
        if (slider) slider.className = "mode-pill-slider customer";
        if (lblPart) lblPart.classList.remove('active');
        if (lblCust) lblCust.classList.add('active');
        if (viewPart) viewPart.classList.add('hidden');
        if (viewCust) viewCust.classList.remove('hidden');
    }
}

// --- Partner Feed ---
let isOnline = true;
function toggleOnlineStatus() {
    isOnline = !isOnline;
    const badge = document.getElementById('status-badge');
    if (badge) {
        badge.textContent = isOnline ? "ONLINE" : "OFFLINE";
        badge.className = isOnline ? "partner-toggle online" : "partner-toggle";
    }
    if (isOnline) loadAvailablePartnerJobs();
}

async function loadAvailablePartnerJobs() {
    if (!isOnline) return;
    const container = document.getElementById('jobs-container');
    if (!container) return;
    
    try {
        const res = await fetch(`${API_URL}/delivery/requests/available?university_id=${LPU_UNIV_ID}`);
        const jobs = await res.json();
        
        container.innerHTML = '';
        if (jobs.length === 0) {
            container.innerHTML = `<p style="color: var(--text-muted); font-size: 14px;">No delivery jobs right now.</p>`;
            return;
        }

        jobs.forEach(job => {
            container.innerHTML += `
                <div class="job-card">
                    <div class="job-route">📍 Loc ${job.pickup_location_id} → 🏠 Loc ${job.drop_location_id}</div>
                    <div class="job-details">
                        <span>Fee + Tip</span>
                        <span class="job-price">₹${job.total_fee}</span>
                    </div>
                    <button onclick="acceptPartnerJob(${job.id})" style="padding: 8px; font-size: 14px;">ACCEPT JOB</button>
                </div>
            `;
        });
    } catch (e) {
        container.innerHTML = `<p style="color: red;">Failed to load feed</p>`;
    }
}

async function acceptPartnerJob(requestId) {
    const user = getLoggedInUser();
    try {
        const res = await fetch(`${API_URL}/delivery/jobs/${requestId}/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ partner_id: user ? user.id : 2 })
        });
        const data = await res.json();
        if (res.ok) {
            alert(`Job Accepted!\nRecipient OTP: ${data.demo_otp_revealed}`);
            window.location.href = 'activity.html';
        } else {
            alert(data.detail);
        }
    } catch (e) { console.error(e); }
}

// --- Marketplace Listings Logic ---
async function loadMarketplace() {
    const container = document.getElementById('marketplace-container');
    if (!container) return;
    try {
        const res = await fetch(`${API_URL}/marketplace/listings?university_id=${LPU_UNIV_ID}`);
        const listings = await res.json();
        container.innerHTML = '';
        
        if (listings.length === 0) {
            container.innerHTML = `<p style="color: var(--text-muted); font-size: 14px;">No items currently listed.</p>`;
            return;
        }

        listings.forEach(item => {
            container.innerHTML += `
                <div class="job-card" style="border-left-color: #8B5CF6;">
                    <div class="job-route">${item.item_name} (x${item.quantity})</div>
                    <div class="job-details">
                        <span>📍 Location ID: ${item.location_id}</span>
                        <span class="job-price">₹${item.listing_price}</span>
                    </div>
                    <button onclick="triggerSimulatedPayment(1, ${item.listing_price})" style="padding: 8px; font-size: 14px; background: #8B5CF6;">BUY NOW</button>
                </div>
            `;
        });
    } catch (e) {
        container.innerHTML = `<p style="color: red;">Error loading marketplace</p>`;
    }
}

function openCreateListingModal() { const m = document.getElementById('listing-modal'); if(m) m.classList.remove('hidden'); }
function closeCreateListingModal() { const m = document.getElementById('listing-modal'); if(m) m.classList.add('hidden'); }

async function submitNewListing() {
    const user = getLoggedInUser();
    const payload = {
        seller_id: user ? user.id : 2,
        item_name: document.getElementById('list-name').value,
        reference_price: parseFloat(document.getElementById('list-ref').value),
        listing_price: parseFloat(document.getElementById('list-price').value),
        quantity: parseInt(document.getElementById('list-qty').value),
        location_id: parseInt(document.getElementById('list-loc').value)
    };

    try {
        const res = await fetch(`${API_URL}/marketplace/listings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert("Listing published successfully!");
            closeCreateListingModal();
            loadMarketplace();
        } else {
            const err = await res.json();
            alert("Error: " + err.detail);
        }
    } catch (e) { alert("Failed to connect to server"); }
}

// --- Simulated Payments ---
let currentPaymentId = null;
async function triggerSimulatedPayment(payeeId, amount) {
    const user = getLoggedInUser();
    try {
        const res = await fetch(`${API_URL}/payments/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payer_id: user ? user.id : 2, payee_id: payeeId, amount: amount, method: "SIMULATED_UPI" })
        });
        const data = await res.json();
        if(res.ok) {
            currentPaymentId = data.payment_id;
            const amtElem = document.getElementById('payment-amount');
            if(amtElem) amtElem.textContent = `₹${data.amount}`;
            const mod = document.getElementById('payment-modal');
            if(mod) mod.classList.remove('hidden');
        }
    } catch (e) { console.error(e); }
}

async function processSimulatedPayment() {
    if (!currentPaymentId) return;
    try {
        const res = await fetch(`${API_URL}/payments/${currentPaymentId}/complete`, { method: 'POST' });
        if (res.ok) {
            alert("Simulated Payment Successful!");
            closePaymentModal();
            loadMarketplace();
        }
    } catch (e) { console.error(e); }
}

function closePaymentModal() {
    const mod = document.getElementById('payment-modal');
    if(mod) mod.classList.add('hidden');
    currentPaymentId = null;
}

// --- Profile Page Loader ---
function loadProfileData() {
    const user = getLoggedInUser();
    if (user) {
        const nameElem = document.getElementById('profile-name');
        const emailElem = document.getElementById('profile-email');
        if(nameElem) nameElem.textContent = user.name;
        if(emailElem) emailElem.textContent = user.email;
    }
}

async function loadUserProfileListings() {
    const user = getLoggedInUser();
    if (!user) return;

    try {
        const res = await fetch(`${API_URL}/marketplace/user/${user.id}/listings`);
        const data = await res.json();

        const activeContainer = document.getElementById('profile-active-listings');
        const expiredContainer = document.getElementById('profile-expired-listings');
        const completedContainer = document.getElementById('profile-completed-listings');

        if (activeContainer) {
            activeContainer.innerHTML = data.active.length === 0 ? '<p style="color: var(--text-muted); font-size: 13px;">No active listings.</p>' : '';
            data.active.forEach(item => {
                activeContainer.innerHTML += renderListingItemCard(item);
            });
        }

        if (expiredContainer) {
            expiredContainer.innerHTML = data.expired.length === 0 ? '<p style="color: var(--text-muted); font-size: 13px;">No expired listings.</p>' : '';
            data.expired.forEach(item => {
                expiredContainer.innerHTML += renderListingItemCard(item);
            });
        }

        if (completedContainer) {
            completedContainer.innerHTML = data.completed.length === 0 ? '<p style="color: var(--text-muted); font-size: 13px;">No completed listings yet.</p>' : '';
            data.completed.forEach(item => {
                completedContainer.innerHTML += renderListingItemCard(item);
            });
        }
    } catch (e) {
        console.error("Failed to load user listings", e);
    }
}

function renderListingItemCard(item) {
    return `
        <div class="job-card" style="border-left-color: #8B5CF6; padding: 12px; margin-bottom: 8px;">
            <div style="font-weight: 600; font-size: 14px;">${item.item_name} (x${item.quantity})</div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                <span>Price: ₹${item.listing_price}</span>
                <span style="font-weight: bold; color: var(--success);">${item.status}</span>
            </div>
        </div>
    `;
}