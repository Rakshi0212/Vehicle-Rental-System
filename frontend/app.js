/* ==========================================================================
   VEHICLE RENTAL SYSTEM CONTROLLER (app.js)
   AJAX Operations, Dynamic Table Rendering, Charting & State Management
   DBMS Project - ad034
   ========================================================================== */

const API_BASE = 'http://127.0.0.1:5000/api';

// Global State
let customers = [];
let vehicles = [];
let rentals = [];
let activeTab = 'dashboard-tab';
let availabilityChart = null;

// Initial Setup
document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initTabs();
    checkDbConnection();
    loadAllData();
});

// Live clock helper
function initClock() {
    const clockEl = document.getElementById('liveClock');
    setInterval(() => {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString();
    }, 1000);
}

// Tab navigation handler
function initTabs() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const titles = {
        'dashboard-tab': { title: 'Dashboard Overview', subtitle: 'Summary stats and fleet diagnostics' },
        'customers-tab': { title: 'Customers Registry', subtitle: 'Manage driver profiles and licenses' },
        'vehicles-tab': { title: 'Fleet Registry', subtitle: 'Browse and manage vehicles' },
        'bookings-tab': { title: 'Bookings & Rentals Console', subtitle: 'Dispatch and log transactions' },
        'procedures-tab': { title: 'Database Stored Procedures', subtitle: 'Execute and test compiled SQL routines' },
        'workbench-tab': { title: 'SQL Workbench', subtitle: 'Run ad-hoc queries and generate report sets' }
    };

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            activeTab = targetTab;
            
            // Switch navigation states
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Switch visible view content
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(targetTab).classList.add('active');
            
            // Update page headers
            document.getElementById('viewTitle').textContent = titles[targetTab].title;
            document.getElementById('viewSubtitle').textContent = titles[targetTab].subtitle;
            
            // Refresh data on view switch
            loadAllData();
        });
    });
}

// Check Database mode and update status cards
async function checkDbConnection() {
    try {
        const res = await fetch(`${API_BASE}/config`);
        const data = await res.json();
        
        const indicator = document.getElementById('statusIndicator');
        const title = document.getElementById('statusTitle');
        const desc = document.getElementById('statusDesc');
        const banner = document.getElementById('mockWarningBanner');
        
        // Populate modal configs
        document.getElementById('cfgHost').value = data.config.host;
        document.getElementById('cfgUser').value = data.config.user;
        document.getElementById('cfgDatabase').value = data.config.database;
        document.getElementById('cfgPort').value = data.config.port;

        if (data.is_mock) {
            indicator.className = 'status-indicator warning';
            title.textContent = 'Simulated Database';
            desc.textContent = 'MySQL offline (fallback)';
            banner.classList.remove('hidden');
        } else {
            indicator.className = 'status-indicator connected';
            title.textContent = 'MySQL Online';
            desc.textContent = 'Connected successfully';
            banner.classList.add('hidden');
        }
    } catch (err) {
        console.error('Error connecting to backend API:', err);
        showSystemAlert('System offline. Please run the Flask server in backend/app.py first.', 'danger');
    }
}

// Fetch all database records
async function loadAllData() {
    try {
        await Promise.all([
            fetchCustomers(),
            fetchVehicles(),
            fetchRentals()
        ]);
        updateDashboardStats();
        populateDropdowns();
        renderCharts();
    } catch (err) {
        console.error('Error loading data:', err);
    }
}

// ----------------- CUSTOMER API CALLS & CRUD -----------------
async function fetchCustomers() {
    const res = await fetch(`${API_BASE}/customers`);
    customers = await res.json();
    renderCustomersTable();
}

function renderCustomersTable() {
    const tbody = document.querySelector('#customersTable tbody');
    tbody.innerHTML = '';
    
    customers.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${c.customer_id}</td>
            <td><strong>${escapeHtml(c.name)}</strong></td>
            <td>${escapeHtml(c.phone)}</td>
            <td><code class="code-license">${escapeHtml(c.license_number)}</code></td>
            <td class="actions-cell">
                <button class="btn-icon-edit" onclick="openCustomerModal(${c.customer_id})" title="Edit"><i class="fa-solid fa-pencil"></i></button>
                <button class="btn-icon-delete" onclick="deleteCustomer(${c.customer_id})" title="Delete"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function openCustomerModal(id = null) {
    const modal = document.getElementById('customerModal');
    const title = document.getElementById('customerModalTitle');
    const form = document.getElementById('customerForm');
    
    form.reset();
    document.getElementById('custFormId').value = id || '';
    
    if (id) {
        title.textContent = 'Edit Customer Profile';
        const c = customers.find(item => item.customer_id === id);
        if (c) {
            document.getElementById('custFormName').value = c.name;
            document.getElementById('custFormPhone').value = c.phone;
            document.getElementById('custFormLicense').value = c.license_number;
        }
    } else {
        title.textContent = 'Add New Customer';
    }
    
    modal.classList.add('active');
}

function closeCustomerModal() {
    document.getElementById('customerModal').classList.remove('active');
}

async function submitCustomerForm(e) {
    e.preventDefault();
    const id = document.getElementById('custFormId').value;
    const name = document.getElementById('custFormName').value;
    const phone = document.getElementById('custFormPhone').value;
    const license = document.getElementById('custFormLicense').value;
    
    const payload = { name, phone, license_number: license };
    const url = id ? `${API_BASE}/customers/${id}` : `${API_BASE}/customers`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (res.ok) {
            showSystemAlert(data.message || 'Operation completed successfully!', 'success');
            closeCustomerModal();
            loadAllData();
        } else {
            showSystemAlert(data.error || 'Failed to submit profile details.', 'danger');
        }
    } catch (err) {
        showSystemAlert('An error occurred during submission.', 'danger');
    }
}

async function deleteCustomer(id) {
    if (!confirm('Are you sure you want to delete this customer? All associated bookings/rentals will also be removed.')) return;
    try {
        const res = await fetch(`${API_BASE}/customers/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            showSystemAlert(data.message || 'Customer profile deleted successfully!', 'success');
            loadAllData();
        } else {
            showSystemAlert(data.error || 'Failed to delete customer.', 'danger');
        }
    } catch (err) {
        showSystemAlert('Error sending delete request.', 'danger');
    }
}

function filterCustomers() {
    const term = document.getElementById('searchCustomer').value.toLowerCase();
    const rows = document.querySelectorAll('#customersTable tbody tr');
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}


// ----------------- VEHICLE API CALLS & CRUD -----------------
async function fetchVehicles() {
    const res = await fetch(`${API_BASE}/vehicles`);
    vehicles = await res.json();
    renderVehiclesTable();
}

function renderVehiclesTable() {
    const tbody = document.querySelector('#vehiclesTable tbody');
    tbody.innerHTML = '';
    
    vehicles.forEach(v => {
        const tr = document.createElement('tr');
        const statusClass = v.status.toLowerCase();
        tr.innerHTML = `
            <td>${v.vehicle_id}</td>
            <td><strong>${escapeHtml(v.model)}</strong></td>
            <td><span class="text-secondary">${escapeHtml(v.type)}</span></td>
            <td>$${parseFloat(v.rental_price_per_day).toFixed(2)}</td>
            <td><span class="badge ${statusClass}">${v.status}</span></td>
            <td class="actions-cell">
                <button class="btn-icon-edit" onclick="openVehicleModal(${v.vehicle_id})" title="Edit"><i class="fa-solid fa-pencil"></i></button>
                <button class="btn-icon-delete" onclick="deleteVehicle(${v.vehicle_id})" title="Delete"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function openVehicleModal(id = null) {
    const modal = document.getElementById('vehicleModal');
    const title = document.getElementById('vehicleModalTitle');
    const form = document.getElementById('vehicleForm');
    
    form.reset();
    document.getElementById('vehFormId').value = id || '';
    
    if (id) {
        title.textContent = 'Modify Vehicle Details';
        const v = vehicles.find(item => item.vehicle_id === id);
        if (v) {
            document.getElementById('vehFormModel').value = v.model;
            document.getElementById('vehFormType').value = v.type;
            document.getElementById('vehFormPrice').value = v.rental_price_per_day;
            document.getElementById('vehFormStatus').value = v.status;
        }
    } else {
        title.textContent = 'Add New Fleet Vehicle';
        document.getElementById('vehFormStatus').value = 'Available';
    }
    
    modal.classList.add('active');
}

function closeVehicleModal() {
    document.getElementById('vehicleModal').classList.remove('active');
}

async function submitVehicleForm(e) {
    e.preventDefault();
    const id = document.getElementById('vehFormId').value;
    const model = document.getElementById('vehFormModel').value;
    const type = document.getElementById('vehFormType').value;
    const rental_price_per_day = document.getElementById('vehFormPrice').value;
    const status = document.getElementById('vehFormStatus').value;
    
    const payload = { model, type, rental_price_per_day, status };
    const url = id ? `${API_BASE}/vehicles/${id}` : `${API_BASE}/vehicles`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (res.ok) {
            showSystemAlert(data.message || 'Vehicle details saved successfully!', 'success');
            closeVehicleModal();
            loadAllData();
        } else {
            showSystemAlert(data.error || 'Failed to submit vehicle details.', 'danger');
        }
    } catch (err) {
        showSystemAlert('An error occurred during submission.', 'danger');
    }
}

async function deleteVehicle(id) {
    if (!confirm('Are you sure you want to delete this vehicle? Booking entries and maintenance history will also be removed.')) return;
    try {
        const res = await fetch(`${API_BASE}/vehicles/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            showSystemAlert(data.message || 'Vehicle removed from fleet registry!', 'success');
            loadAllData();
        } else {
            showSystemAlert(data.error || 'Failed to delete vehicle.', 'danger');
        }
    } catch (err) {
        showSystemAlert('Error sending delete request.', 'danger');
    }
}

function filterVehicles() {
    const term = document.getElementById('searchVehicle').value.toLowerCase();
    const rows = document.querySelectorAll('#vehiclesTable tbody tr');
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

// ----------------- RENTALS & BOOKINGS API CALLS -----------------
async function fetchRentals() {
    const res = await fetch(`${API_BASE}/rentals`);
    rentals = await res.json();
    renderRentalsTable();
}

function renderRentalsTable() {
    const tbody = document.querySelector('#rentalsTable tbody');
    tbody.innerHTML = '';
    
    rentals.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><code>#RN-${r.rental_id}</code></td>
            <td><strong>${escapeHtml(r.customer_name)}</strong></td>
            <td>${escapeHtml(r.vehicle_model)}</td>
            <td>${formatDateString(r.start_date)}</td>
            <td>${formatDateString(r.end_date)}</td>
            <td class="total-amount-col">
                <strong>$${parseFloat(r.total_amount).toFixed(2)}</strong>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function createBooking(e) {
    e.preventDefault();
    const customer_id = document.getElementById('bookingCustomer').value;
    const vehicle_id = document.getElementById('bookingVehicle').value;
    const start_date = document.getElementById('bookingStartDate').value;
    const end_date = document.getElementById('bookingEndDate').value;
    
    const payload = { customer_id, vehicle_id, start_date, end_date };
    
    try {
        const res = await fetch(`${API_BASE}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (res.ok) {
            showSystemAlert(data.message || 'Booking made successfully!', 'success');
            document.getElementById('bookingForm').reset();
            loadAllData();
        } else {
            // This catches trigger signaling or validation failures
            showSystemAlert(data.error || 'Failed to log booking details.', 'danger');
        }
    } catch (err) {
        showSystemAlert('An error occurred while dispatching booking.', 'danger');
    }
}

// ----------------- DROPDOWNS & DASHBOARD UTILITIES -----------------
function populateDropdowns() {
    const custDropdown = document.getElementById('bookingCustomer');
    const vehDropdown = document.getElementById('bookingVehicle');
    const procRentalDropdown = document.getElementById('procRentalId');
    
    // Maintain selections if possible
    const prevCust = custDropdown.value;
    const prevVeh = vehDropdown.value;
    const prevRental = procRentalDropdown.value;
    
    // 1. Customer Dropdowns
    custDropdown.innerHTML = '<option value="" disabled selected>Choose a customer...</option>';
    customers.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.customer_id;
        opt.textContent = `${c.name} (ID: ${c.customer_id})`;
        custDropdown.appendChild(opt);
    });
    custDropdown.value = prevCust || '';
    
    // 2. Vehicle Dropdowns
    vehDropdown.innerHTML = '<option value="" disabled selected>Choose a vehicle...</option>';
    vehicles.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v.vehicle_id;
        opt.textContent = `${v.model} (${v.type}) - ${v.status}`;
        vehDropdown.appendChild(opt);
    });
    vehDropdown.value = prevVeh || '';
    
    // 3. Rental Dropdowns (for CalculateRentalCharge stored procedure)
    procRentalDropdown.innerHTML = '<option value="" disabled selected>Choose a rental...</option>';
    rentals.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.rental_id;
        opt.textContent = `Rental #${r.rental_id} (${r.customer_name} - ${r.vehicle_model})`;
        procRentalDropdown.appendChild(opt);
    });
    procRentalDropdown.value = prevRental || '';
}

function updateDashboardStats() {
    document.getElementById('statCustomers').textContent = customers.length;
    document.getElementById('statVehicles').textContent = vehicles.length;
    
    // Calculate total rentals and active bookings
    document.getElementById('statRentals').textContent = rentals.length;
    
    const rentedVehiclesCount = vehicles.filter(v => v.status === 'Rented').length;
    document.getElementById('statBookings').textContent = rentedVehiclesCount;
}

// ----------------- STORED PROCEDURES -----------------

// Proc 1: Calculate Rental Charge
async function runCalculateProcedure(e) {
    e.preventDefault();
    const rental_id = document.getElementById('procRentalId').value;
    
    try {
        const res = await fetch(`${API_BASE}/procedures/calculate-charge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rental_id })
        });
        const data = await res.json();
        
        if (res.ok) {
            showSystemAlert(data.message, 'success');
            document.getElementById('calcOutputValue').textContent = `$${parseFloat(data.total_amount).toFixed(2)}`;
            document.getElementById('calcResultBox').classList.remove('hidden');
            loadAllData(); // Refresh totals on tables
        } else {
            showSystemAlert(data.error || 'Failed to execute procedure.', 'danger');
        }
    } catch (err) {
        showSystemAlert('Network error during procedure execution.', 'danger');
    }
}

// Proc 2: Get Vehicle Availability Report
async function runAvailabilityReportProcedure() {
    try {
        const res = await fetch(`${API_BASE}/procedures/availability-report`);
        const reportData = await res.json();
        
        const tbody = document.querySelector('#reportResultTable tbody');
        tbody.innerHTML = '';
        
        reportData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span class="badge ${row.status.toLowerCase()}">${row.status}</span></td>
                <td><strong>${row.vehicle_count}</strong></td>
            `;
            tbody.appendChild(tr);
        });
        
        document.getElementById('reportResultBox').classList.remove('hidden');
        showSystemAlert('Availability report loaded successfully via Stored Procedure.', 'success');
    } catch (err) {
        showSystemAlert('Failed to execute availability report routine.', 'danger');
    }
}

// ----------------- SQL WORKBENCH HANDLERS -----------------
const predefinedQueries = {
    1: `SELECT * \nFROM Vehicle;`,
    
    2: `SELECT * \nFROM Vehicle \nWHERE status = 'Available';`,
    
    3: `SELECT \n    r.rental_id, \n    c.name AS customer_name, \n    c.phone, \n    r.start_date, \n    r.end_date, \n    r.total_amount\nFROM Rental r\nINNER JOIN Booking b ON r.booking_id = b.booking_id\nINNER JOIN Customer c ON b.customer_id = c.customer_id;`,
    
    4: `SELECT \n    r.rental_id, \n    c.name AS customer_name, \n    v.model AS vehicle_model, \n    v.type AS vehicle_type, \n    r.start_date, \n    r.end_date, \n    r.total_amount\nFROM Rental r\nINNER JOIN Booking b ON r.booking_id = b.booking_id\nINNER JOIN Customer c ON b.customer_id = c.customer_id\nINNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id;`,
    
    5: `SELECT \n    v.type AS vehicle_type, \n    COUNT(r.rental_id) AS total_rentals\nFROM Rental r\nINNER JOIN Booking b ON r.booking_id = b.booking_id\nINNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id\nGROUP BY v.type;`,
    
    6: `SELECT \n    v.type AS vehicle_type, \n    COUNT(r.rental_id) AS total_rentals\nFROM Rental r\nINNER JOIN Booking b ON r.booking_id = b.booking_id\nINNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id\nGROUP BY v.type\nHAVING COUNT(r.rental_id) > 15;`,
    
    7: `SELECT * \nFROM Vehicle \nWHERE rental_price_per_day > (\n    SELECT AVG(rental_price_per_day) \n    FROM Vehicle\n);`,
    
    8: `SELECT \n    c1.customer_id, \n    c1.name, \n    (SELECT COUNT(*) FROM Booking b1 WHERE b1.customer_id = c1.customer_id) AS booking_count\nFROM Customer c1\nWHERE (\n    SELECT COUNT(*) \n    FROM Booking b1 \n    WHERE b1.customer_id = c1.customer_id\n) > (\n    SELECT COUNT(*) \n    FROM Booking b2 \n    WHERE b2.customer_id = 2\n);`,
    
    9: `SELECT \n    v.vehicle_id, \n    v.model, \n    v.type, \n    v.status, \n    b.booking_id, \n    b.booking_date\nFROM Vehicle v\nLEFT JOIN Booking b ON v.vehicle_id = b.vehicle_id;`,
    
    10: `SELECT * \nFROM Vehicle v\nWHERE NOT EXISTS (\n    SELECT 1 \n    FROM Booking b \n    WHERE b.vehicle_id = v.vehicle_id\n);`
};

function selectPredefinedQuery(index) {
    // Clear selection classes
    document.querySelectorAll('.query-link-btn').forEach((btn, idx) => {
        if (idx === (index - 1)) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    });
    
    // Set query text
    document.getElementById('sqlQueryText').value = predefinedQueries[index];
}

async function executeCurrentQuery() {
    const rawSql = document.getElementById('sqlQueryText').value;
    const container = document.getElementById('queryResultContainer');
    
    if (!rawSql.trim()) {
        showSystemAlert('Query string cannot be empty.', 'warning');
        return;
    }
    
    container.innerHTML = '<div class="empty-results-prompt"><i class="fa-solid fa-spinner fa-spin"></i><p>Executing SQL query statement...</p></div>';
    
    try {
        const res = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: rawSql })
        });
        const data = await res.json();
        
        if (data.status === 'success') {
            const records = data.results;
            
            if (!records || records.length === 0) {
                container.innerHTML = `
                    <div class="empty-results-prompt">
                        <i class="fa-solid fa-check"></i>
                        <p>Query statement ran successfully. Zero rows returned.</p>
                    </div>
                `;
                return;
            }
            
            // Build columns list dynamically from keys
            const columns = Object.keys(records[0]);
            
            let html = `
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                ${columns.map(col => `<th>${escapeHtml(col.toUpperCase())}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${records.map(row => `
                                <tr>
                                    ${columns.map(col => {
                                        const val = row[col];
                                        // Highlight specific values like status
                                        if (col.toLowerCase() === 'status') {
                                            const cls = String(val).toLowerCase();
                                            return `<td><span class="badge ${cls}">${val}</span></td>`;
                                        }
                                        return `<td>${val === null ? '<em class="text-muted">NULL</em>' : escapeHtml(String(val))}</td>`;
                                    }).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            container.innerHTML = html;
            showSystemAlert(`Query ran successfully! ${records.length} records returned.`, 'success');
        } else {
            // Show detailed SQL execution errors
            container.innerHTML = `
                <div class="empty-results-prompt text-danger" style="color: var(--danger)">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <p style="margin-top: 10px; font-weight: 600;">SQL Engine Error:</p>
                    <pre style="text-align: left; background-color: #0b0f19; padding: 15px; border-radius: var(--radius-sm); border: 1px solid rgba(239, 68, 68, 0.2); max-width: 100%; white-space: pre-wrap; font-family: monospace;">${escapeHtml(data.error)}</pre>
                </div>
            `;
            showSystemAlert('SQL statement execution failed.', 'danger');
        }
    } catch (err) {
        container.innerHTML = `
            <div class="empty-results-prompt text-danger" style="color: var(--danger)">
                <i class="fa-solid fa-circle-exclamation"></i>
                <p>Failed to connect to backend SQL runner.</p>
            </div>
        `;
    }
}

// ----------------- CONFIG MODAL & CONNECTION PANEL -----------------
function toggleConfigModal() {
    document.getElementById('configModal').classList.toggle('active');
}

async function updateDbConfig(e) {
    e.preventDefault();
    const host = document.getElementById('cfgHost').value;
    const user = document.getElementById('cfgUser').value;
    const password = document.getElementById('cfgPassword').value;
    const database = document.getElementById('cfgDatabase').value;
    const port = document.getElementById('cfgPort').value;
    
    const payload = { host, user, password, database, port };
    
    try {
        const res = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        toggleConfigModal();
        showSystemAlert(data.message, data.is_mock ? 'warning' : 'success');
        checkDbConnection(); // Reload status cards
        loadAllData(); // Refresh dashboard and views
    } catch (err) {
        showSystemAlert('Failed to update credentials.', 'danger');
    }
}

// ----------------- CHARTING (CHART.JS) -----------------
async function renderCharts() {
    try {
        const res = await fetch(`${API_BASE}/procedures/availability-report`);
        const report = await res.json();
        
        const labels = report.map(r => r.status);
        const counts = report.map(r => r.vehicle_count);
        
        // Destruct existing chart to redraw
        if (availabilityChart) {
            availabilityChart.destroy();
        }
        
        const canvas = document.getElementById('fleetChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Custom HSL gradients for chart bars
        const gradAvailable = ctx.createLinearGradient(0, 0, 0, 300);
        gradAvailable.addColorStop(0, 'rgba(34, 197, 94, 0.85)');
        gradAvailable.addColorStop(1, 'rgba(22, 163, 74, 0.45)');
        
        const gradRented = ctx.createLinearGradient(0, 0, 0, 300);
        gradRented.addColorStop(0, 'rgba(59, 130, 246, 0.85)');
        gradRented.addColorStop(1, 'rgba(37, 99, 235, 0.45)');
        
        const gradMaintenance = ctx.createLinearGradient(0, 0, 0, 300);
        gradMaintenance.addColorStop(0, 'rgba(234, 179, 8, 0.85)');
        gradMaintenance.addColorStop(1, 'rgba(202, 138, 4, 0.45)');
        
        const backgrounds = report.map(r => {
            const st = r.status.toLowerCase();
            if (st === 'available') return gradAvailable;
            if (st === 'rented') return gradRented;
            return gradMaintenance;
        });
        
        const borders = report.map(r => {
            const st = r.status.toLowerCase();
            if (st === 'available') return 'rgba(34, 197, 94, 1)';
            if (st === 'rented') return 'rgba(59, 130, 246, 1)';
            return 'rgba(234, 179, 8, 1)';
        });
        
        availabilityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Vehicles',
                    data: counts,
                    backgroundColor: backgrounds,
                    borderColor: borders,
                    borderWidth: 1.5,
                    borderRadius: 8,
                    barThickness: 50
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#111827',
                        titleFont: { family: 'Outfit', size: 14, weight: 'bold' },
                        bodyFont: { family: 'Outfit', size: 13 },
                        borderWidth: 1,
                        borderColor: 'rgba(255,255,255,0.1)'
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af', font: { family: 'Outfit', size: 12, weight: 'medium' } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af', stepSize: 1, font: { family: 'Outfit', size: 12 } },
                        beginAtZero: true
                    }
                }
            }
        });
        
    } catch (err) {
        console.error('Chart rendering failed:', err);
    }
}

// ----------------- ALERT UTILITIES -----------------
function showSystemAlert(message, type = 'primary') {
    // Dismiss old alert container if exists
    const oldAlert = document.querySelector('.system-toast');
    if (oldAlert) oldAlert.remove();
    
    const toast = document.createElement('div');
    toast.className = `system-toast system-toast-${type}`;
    
    // Choose icon
    let icon = 'fa-circle-info';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'warning') icon = 'fa-triangle-exclamation';
    if (type === 'danger') icon = 'fa-circle-xmark';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation slide-in
    setTimeout(() => toast.classList.add('active'), 50);
    
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        toast.classList.remove('active');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ----------------- FORMATTING & SANITIZATION -----------------
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatDateString(dateStr) {
    if (!dateStr) return '';
    try {
        const parts = dateStr.split('T')[0].split('-');
        if (parts.length === 3) {
            const [year, month, day] = parts;
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            return `${day} ${months[parseInt(month, 10) - 1]} ${year}`;
        }
        return dateStr;
    } catch (e) {
        return dateStr;
    }
}
