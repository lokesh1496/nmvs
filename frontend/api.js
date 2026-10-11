/**
 * NMVS Enterprise Console - Frontend Backend API Connector
 * Provides unified, resilient communication between the UI and FastAPI backend (:8000)
 */

(function (window) {
  'use strict';

  // Determine API Base URL
  const getInitialBaseUrl = () => {
    if (window.__NMVS_API_BASE__) return window.__NMVS_API_BASE__;
    const stored = localStorage.getItem('NMVS_API_BASE');
    if (stored) return stored;
    if (window.location.port === '8000') return window.location.origin;
    return 'http://localhost:8000';
  };

  const NMVS_API = {
    baseUrl: getInitialBaseUrl(),
    isOnline: false,
    pingInterval: null,
    listeners: [],

    setBaseUrl(url) {
      this.baseUrl = url.replace(/\/+$/, '');
      localStorage.setItem('NMVS_API_BASE', this.baseUrl);
      this.checkHealth();
    },

    onStatusChange(fn) {
      if (typeof fn === 'function') {
        this.listeners.push(fn);
      }
    },

    notifyStatus(online, data) {
      this.isOnline = online;
      this.listeners.forEach((fn) => {
        try {
          fn(online, data);
        } catch (e) {
          console.error('Status listener error:', e);
        }
      });
      this.updateHeaderBadges(online, data);
    },

    async request(endpoint, options = {}) {
      const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
      const defaultHeaders = {
        'Accept': 'application/json',
      };
      const token = this.getAuthToken();
      if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
      }
      if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        defaultHeaders['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
      }

      options.headers = { ...defaultHeaders, ...options.headers };

      try {
        const response = await fetch(url, options);
        if (!response.ok) {
          let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
          try {
            const errJson = await response.json();
            if (errJson && errJson.detail) {
              errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
            }
          } catch (_) {}
          throw new Error(errorDetail);
        }
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
          return await response.json();
        }
        return await response.text();
      } catch (err) {
        console.warn(`[NMVS API] Request to ${endpoint} failed:`, err.message);
        throw err;
      }
    },

    // Health Check
    async checkHealth() {
      try {
        const data = await this.request('/health');
        this.notifyStatus(true, data);
        return data;
      } catch (err) {
        this.notifyStatus(false, { error: err.message });
        return null;
      }
    },

    // Auth Token & Session Management
    getAuthToken() {
      return localStorage.getItem('NMVS_AUTH_TOKEN') || sessionStorage.getItem('NMVS_AUTH_TOKEN') || null;
    },

    getStoredUser() {
      const u = localStorage.getItem('NMVS_AUTH_USER') || sessionStorage.getItem('NMVS_AUTH_USER');
      if (!u) return null;
      try {
        return JSON.parse(u);
      } catch (_) {
        return null;
      }
    },

    setSession(token, user, remember = true) {
      const store = remember ? localStorage : sessionStorage;
      store.setItem('NMVS_AUTH_TOKEN', token);
      store.setItem('NMVS_AUTH_USER', JSON.stringify(user));
      if (remember) {
        sessionStorage.removeItem('NMVS_AUTH_TOKEN');
        sessionStorage.removeItem('NMVS_AUTH_USER');
      } else {
        localStorage.removeItem('NMVS_AUTH_TOKEN');
        localStorage.removeItem('NMVS_AUTH_USER');
      }
      this.updateUserHeader();
    },

    logout() {
      localStorage.removeItem('NMVS_AUTH_TOKEN');
      localStorage.removeItem('NMVS_AUTH_USER');
      sessionStorage.removeItem('NMVS_AUTH_TOKEN');
      sessionStorage.removeItem('NMVS_AUTH_USER');
      this.updateUserHeader();
      this.showToast('Logged out of NMVS Console', 'info');
      setTimeout(() => {
        const dest = window.location.port === '8000' ? '/login' : '../login.html';
        window.location.href = dest;
      }, 500);
    },

    async login(username, password, remember = true) {
      const data = await this.request('/auth/login', {
        method: 'POST',
        body: { username, password },
      });
      if (!data || !data.access_token || !data.user) {
        throw new Error('Login response did not include an authenticated user profile.');
      }
      this.setSession(data.access_token, data.user, remember);
      return data;
    },

    async register(userData) {
      return await this.request('/auth/register', {
        method: 'POST',
        body: userData,
      });
    },

    async getMe() {
      return await this.request('/auth/me');
    },

    async changePassword(data) {
      return await this.request('/auth/change-password', {
        method: 'POST',
        body: data,
      });
    },

    async restoreSession() {
      const token = this.getAuthToken();
      if (!token || this.getStoredUser()) return;

      const store = localStorage.getItem('NMVS_AUTH_TOKEN') ? localStorage : sessionStorage;
      try {
        const user = await this.getMe();
        if (!user || !user.username) {
          throw new Error('The authenticated user profile is missing.');
        }
        store.setItem('NMVS_AUTH_USER', JSON.stringify(user));
        this.updateUserHeader();
      } catch (err) {
        store.removeItem('NMVS_AUTH_TOKEN');
        store.removeItem('NMVS_AUTH_USER');
        this.updateUserHeader();
        console.warn('[NMVS Auth] Could not restore the saved session:', err.message);
        this.showToast('Your saved sign-in has expired. Please sign in again.', 'warning');
      }
    },

    async forgotPassword(email) {
      return await this.request('/auth/forgot-password', {
        method: 'POST',
        body: { email },
      });
    },

    async verifyResetOtp(email, otp) {
      return await this.request('/auth/verify-reset-otp', {
        method: 'POST',
        body: { email, otp },
      });
    },

    async resetPassword(data) {
      return await this.request('/auth/reset-password', {
        method: 'POST',
        body: data,
      });
    },

    // Dashboard Endpoints
    async getDashboardOverview() {
      return await this.request('/dashboard/overview');
    },

    async getDashboardStats() {
      return await this.request('/dashboard/stats');
    },

    // Devices Endpoints
    async getDevices() {
      return await this.request('/devices/');
    },

    async getDevice(id) {
      return await this.request(`/devices/${id}`);
    },

    async createDevice(deviceData) {
      return await this.request('/devices/', {
        method: 'POST',
        body: deviceData,
      });
    },

    async updateDevice(id, updateData) {
      return await this.request(`/devices/${id}`, {
        method: 'PUT',
        body: updateData,
      });
    },

    async deleteDevice(id) {
      return await this.request(`/devices/${id}`, {
        method: 'DELETE',
      });
    },

    async redetectDevice(id) {
      return await this.request(`/devices/${id}/redetect`, {
        method: 'POST',
      });
    },

    async detectIp(ip) {
      return await this.request(`/devices/detect/${encodeURIComponent(ip)}`);
    },

    // Monitoring Endpoints
    async checkDevice(ip) {
      return await this.request(`/monitoring/check/${encodeURIComponent(ip)}`);
    },

    async getMonitoringHistory(ip, limit = 20) {
      return await this.request(`/monitoring/history/${encodeURIComponent(ip)}?limit=${limit}`);
    },

    async getAllMonitoringHistory(limit = 100) {
      return await this.request(`/monitoring/history?limit=${limit}`);
    },

    // Speed Monitoring Endpoints
    async runSpeedTest(ip = 'internet') {
      return await this.request('/speed-monitoring/run', {
        method: 'POST',
        body: { ip: ip || 'internet' },
      });
    },

    async runLiveSpeedTest(ip = 'internet') {
      return await this.request(`/speed-monitoring/live?ip=${encodeURIComponent(ip || 'internet')}`);
    },

    async getSpeedHistory(limit = 20, ip = null) {
      let q = `limit=${limit}`;
      if (ip) q += `&ip=${encodeURIComponent(ip)}`;
      return await this.request(`/speed-monitoring/history?${q}`);
    },

    async deleteSpeedHistory(id) {
      return await this.request(`/speed-monitoring/history/${id}`, {
        method: 'DELETE',
      });
    },

    // Alerts Endpoints
    async getAlerts(params = {}) {
      const sp = new URLSearchParams();
      if (params.status) sp.append('status', params.status);
      if (params.severity) sp.append('severity', params.severity);
      if (params.alert_type) sp.append('alert_type', params.alert_type);
      if (params.limit) sp.append('limit', params.limit);
      const qs = sp.toString();
      return await this.request(`/alerts${qs ? '?' + qs : ''}`);
    },

    async getAlertsSummary() {
      return await this.request('/alerts/summary');
    },

    async ackAlert(alertId) {
      return await this.request(`/alerts/${alertId}/acknowledge`, {
        method: 'PUT',
      });
    },

    async resolveAlert(alertId) {
      return await this.request(`/alerts/${alertId}/resolve`, {
        method: 'PUT',
      });
    },

    async deleteAlert(alertId) {
      return await this.request(`/alerts/${alertId}`, {
        method: 'DELETE',
      });
    },

    // Topology Endpoints
    async getTopology(options = {}) {
      const sp = new URLSearchParams();
      if (options.refresh_status !== undefined) sp.append('refresh_status', options.refresh_status);
      if (options.include_wan !== undefined) sp.append('include_wan', options.include_wan);
      if (options.connected_only !== undefined) sp.append('connected_only', options.connected_only);
      const qs = sp.toString();
      return await this.request(`/topology${qs ? '?' + qs : ''}`);
    },

    async refreshTopology(connectedOnly = true) {
      return await this.request(`/topology/refresh?connected_only=${connectedOnly}`, {
        method: 'POST',
      });
    },

    async getTopologySummary(connectedOnly = true) {
      return await this.request(`/topology/summary?connected_only=${connectedOnly}`);
    },

    async getSubnets(connectedOnly = true) {
      return await this.request(`/topology/subnets?connected_only=${connectedOnly}`);
    },

    // Discovery
    async scanNetwork(network) {
      return await this.request(`/discovery/scan?network=${encodeURIComponent(network)}`);
    },

    async pingDevice(ip) {
      return await this.request(`/discovery/ping/${encodeURIComponent(ip)}`);
    },

    // Metrics
    async getMetricsSummary() {
      return await this.request('/metrics/summary');
    },

    async getMetricsUptime(hours = 24) {
      return await this.request(`/metrics/uptime?hours=${hours}`);
    },

    // Reports URLs
    getDevicesCsvUrl() {
      return `${this.baseUrl}/reports/devices/csv`;
    },

    getExecutivePdfUrl() {
      return `${this.baseUrl}/reports/executive/pdf`;
    },

    // Helper: Seed sample fleet if database has 0 devices
    async seedSampleFleet() {
      const sampleDevices = [
        { name: 'CR-01-DC1', ip: '10.240.0.1', device_type: 'Core Router' },
        { name: 'AS-Floor1-01', ip: '10.240.10.1', device_type: 'Access Switch' },
        { name: 'AS-Floor2-02', ip: '10.240.10.2', device_type: 'Access Switch' },
        { name: 'FW-Edge-Alpha', ip: '10.240.0.254', device_type: 'Firewall & Security' },
        { name: 'AP-Lobby-West', ip: '10.240.20.10', device_type: 'Wireless AP' },
        { name: 'AP-Exec-Floor3', ip: '10.240.20.11', device_type: 'Wireless AP' },
        { name: 'Storage-SAN-01', ip: '10.240.30.5', device_type: 'Storage & NAS' },
        { name: 'Telemetry-Worker-1', ip: '192.168.1.104', device_type: 'Probe Server' },
      ];

      const results = [];
      for (const dev of sampleDevices) {
        try {
          const res = await this.createDevice(dev);
          results.push(res);
        } catch (e) {
          console.log(`Notice seeding ${dev.name}:`, e.message);
        }
      }
      return results;
    },

    // UI Toast Notification
    showToast(message, type = 'info') {
      let toastContainer = document.getElementById('nmvs-toast-container');
      if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'nmvs-toast-container';
        toastContainer.className = 'fixed bottom-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none';
        document.body.appendChild(toastContainer);
      }

      const toast = document.createElement('div');
      toast.className = `pointer-events-auto px-4 py-3 rounded-xl shadow-xl flex items-center gap-3 text-sm font-medium transition-all duration-300 transform translate-y-4 opacity-0 text-white`;

      let icon = 'info';
      if (type === 'success') {
        toast.className += ' bg-[#006971] border border-[#22c7d6]/40 shadow-[0_4px_16px_rgba(0,105,113,0.4)]';
        icon = 'check_circle';
      } else if (type === 'error') {
        toast.className += ' bg-[#ba1a1a] border border-white/20 shadow-[0_4px_16px_rgba(186,26,26,0.4)]';
        icon = 'error';
      } else if (type === 'warning') {
        toast.className += ' bg-[#2a57c2] border border-white/20 shadow-[0_4px_16px_rgba(42,87,194,0.4)]';
        icon = 'warning';
      } else {
        toast.className += ' bg-[#17233F] border border-white/20 shadow-[0_4px_16px_rgba(23,35,63,0.5)]';
        icon = 'info';
      }

      toast.innerHTML = `
        <span class="material-symbols-outlined text-[20px]">${icon}</span>
        <div class="flex-1">${message}</div>
        <button class="text-white/60 hover:text-white transition-colors" onclick="this.parentElement.remove()">
          <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
      `;

      toastContainer.appendChild(toast);
      requestAnimationFrame(() => {
        toast.classList.remove('translate-y-4', 'opacity-0');
      });

      setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
      }, 4000);
    },

    // Update Header Status Badges Across Pages
    updateHeaderBadges(online, data) {
      const badges = document.querySelectorAll('[data-nmvs-connection-badge]');
      badges.forEach((badge) => {
        if (online) {
          badge.className = 'hidden sm:flex items-center gap-space-xs px-space-md py-1 rounded-full bg-[#131C33] border border-white/10 cursor-pointer hover:bg-[#1a2646] transition-colors';
          badge.title = `Backend Connected: ${this.baseUrl} (Click for Settings)`;
          badge.innerHTML = `
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-tertiary-container opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-tertiary-container shadow-[0_0_8px_rgba(62,200,193,0.8)]"></span>
            </span>
            <span class="font-code-sm text-code-sm font-medium text-surface-variant tracking-tight">API Connected :8000</span>
          `;
        } else {
          badge.className = 'hidden sm:flex items-center gap-space-xs px-space-md py-1 rounded-full bg-error-container/20 border border-error/40 cursor-pointer hover:bg-error-container/30 transition-colors';
          badge.title = `Backend Offline: Click to retry or configure connection to ${this.baseUrl}`;
          badge.innerHTML = `
            <span class="relative flex h-2 w-2">
              <span class="relative inline-flex rounded-full h-2 w-2 bg-error shadow-[0_0_8px_rgba(186,26,26,0.8)]"></span>
            </span>
            <span class="font-code-sm text-code-sm font-medium text-error tracking-tight">API Offline (Retry)</span>
          `;
        }
      });
    },

    // Navigation Wiring
    setupNavigation() {
      // Find current page path
      const currentPath = window.location.pathname.toLowerCase();
      let activeSection = 'dashboard';
      if (currentPath.includes('fleet') || currentPath.includes('device')) activeSection = 'devices';
      else if (currentPath.includes('topology')) activeSection = 'topology';
      else if (currentPath.includes('speed') || currentPath.includes('probe')) activeSection = 'speed-monitoring';

      // Detect relative basePath
      let relDashboard = '../nmvs_network_visibility_monitoring_dashboard/code.html';
      let relDevices = '../nmvs_device_management_fleet_inventory/code.html';
      let relTopology = '../nmvs_interactive_network_topology/code.html';
      let relSpeed = '../nmvs_speed_monitoring_historical_telemetry_probe_1/code.html';

      // If loaded directly from single directory or root
      if (currentPath.endsWith('index.html') || currentPath === '/' || currentPath.endsWith('dashboard')) {
        relDashboard = './nmvs_network_visibility_monitoring_dashboard/code.html';
        relDevices = './nmvs_device_management_fleet_inventory/code.html';
        relTopology = './nmvs_interactive_network_topology/code.html';
        relSpeed = './nmvs_speed_monitoring_historical_telemetry_probe_1/code.html';
      }

      // If running on FastAPI server routes
      if (window.location.port === '8000') {
        relDashboard = '/ui';
        relDevices = '/devices-view';
        relTopology = '/topology-view';
        relSpeed = '/speed-monitoring-view';
      }

      const pathMap = {
        'dashboard': relDashboard,
        'devices': relDevices,
        'monitoring': relDashboard,
        'speed-monitoring': relSpeed,
        'topology': relTopology,
        'alerts': relDashboard + '#alerts',
        'reports': 'javascript:NMVS_API.openReportsModal();',
        'settings': 'javascript:NMVS_API.openAccountSettingsModal();',
      };

      document.querySelectorAll('header nav a[data-path]').forEach((link) => {
        const path = link.getAttribute('data-path');
        if (pathMap[path]) {
          link.href = pathMap[path];
        }

        // Highlight active link
        if (path === activeSection) {
          link.className = 'px-space-md py-1.5 rounded-lg transition-all bg-[#202D4B] text-primary-container ring-1 ring-primary-container/40 font-semibold';
          link.setAttribute('aria-current', 'page');
        } else {
          link.className = 'px-space-md py-1.5 rounded-lg text-surface-variant hover:text-white transition-all font-body-sm text-body-sm';
          link.removeAttribute('aria-current');
        }
      });

      // Tag the connection badge
      const headerRight = document.querySelector('header .flex.items-center.gap-space-md');
      if (headerRight) {
        let badge = headerRight.querySelector('.rounded-full.bg-\\[\\#131C33\\]');
        if (badge) {
          badge.setAttribute('data-nmvs-connection-badge', 'true');
          badge.addEventListener('click', () => {
            if (!this.isOnline) {
              this.showToast('Rechecking backend at ' + this.baseUrl + '...', 'info');
              this.checkHealth().then((ok) => {
                if (ok) this.showToast('Connected to NMVS Backend!', 'success');
                else this.openSettingsModal();
              });
            } else {
              this.openSettingsModal();
            }
          });
        }
      }

      this.updateUserHeader();
    },

    updateUserHeader() {
      const user = this.getStoredUser();
      const loginUrl = window.location.port === '8000' ? '/login' : '../login.html';
      
      const userContainer = document.querySelector('header .flex.items-center.gap-space-sm.pl-space-xs');
      if (userContainer) {
        if (user) {
          userContainer.className = 'flex items-center gap-space-sm pl-space-xs border-l border-white/10 cursor-pointer group relative';
          userContainer.title = `Signed in as ${user.username} (${user.email || ''}). Click to Sign Out.`;
          userContainer.onclick = () => {
            if (confirm(`Signed in as '${user.username}'. Do you want to sign out?`)) {
              this.logout();
            }
          };
          userContainer.innerHTML = `
            <div class="hidden md:flex flex-col text-right">
              <span class="font-title-sm text-title-sm text-white leading-tight font-semibold">${user.username}</span>
              <span class="font-label-sm text-label-sm text-tertiary-container leading-none">Online &bull; Logout</span>
            </div>
            <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center ring-2 ring-primary-container/40 group-hover:ring-primary-container transition-all">
              <span class="material-symbols-outlined text-on-primary text-[18px]">verified_user</span>
            </div>
          `;
        } else {
          userContainer.className = 'flex items-center gap-space-sm pl-space-xs border-l border-white/10 cursor-pointer group';
          userContainer.title = 'Click to Sign In';
          userContainer.onclick = () => {
            window.location.href = loginUrl;
          };
          userContainer.innerHTML = `
            <div class="hidden md:flex flex-col text-right">
              <span class="font-title-sm text-title-sm text-white leading-tight">Operator</span>
              <span class="font-label-sm text-label-sm text-primary-container leading-none">Sign In</span>
            </div>
            <div class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center ring-1 ring-white/20 group-hover:bg-primary-container group-hover:text-black transition-all">
              <span class="material-symbols-outlined text-[18px]">login</span>
            </div>
          `;
        }
      }
    },

    // Modal: Settings & Backend URL Config
    async openAccountSettingsModal() {
      if (document.getElementById('nmvs-account-settings-modal')) return;

      const token = this.getAuthToken();
      if (!token) {
        this.showToast('Sign in to view account and profile settings.', 'warning');
        return;
      }

      const modal = document.createElement('div');
      modal.id = 'nmvs-account-settings-modal';
      modal.className = 'fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-[#0a1122]/70 backdrop-blur-md';
      modal.innerHTML = `
        <section role="dialog" aria-modal="true" aria-labelledby="nmvs-account-settings-title" class="w-full max-w-lg bg-[#17233F] text-white rounded-2xl shadow-2xl border border-white/10 overflow-hidden">
          <header class="p-5 border-b border-white/10 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary-container">
                <span class="material-symbols-outlined">manage_accounts</span>
              </div>
              <div>
                <h2 id="nmvs-account-settings-title" class="font-bold text-base">Account &amp; Profile Settings</h2>
                <p class="text-xs text-surface-variant/80">Manage your NMVS account details and password.</p>
              </div>
            </div>
            <button type="button" data-close-account-settings aria-label="Close" class="p-1 rounded-lg text-surface-variant hover:text-white hover:bg-white/10">
              <span class="material-symbols-outlined">close</span>
            </button>
          </header>
          <div class="p-5 flex flex-col gap-5">
            <div>
              <h3 class="text-sm font-semibold mb-3">Profile</h3>
              <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <div class="p-3 rounded-xl bg-[#121B31]">
                  <dt class="text-xs text-surface-variant/70">Username</dt>
                  <dd id="nmvs-account-username" class="mt-1 font-medium break-all">Loading...</dd>
                </div>
                <div class="p-3 rounded-xl bg-[#121B31]">
                  <dt class="text-xs text-surface-variant/70">Email</dt>
                  <dd id="nmvs-account-email" class="mt-1 font-medium break-all">Loading...</dd>
                </div>
                <div class="p-3 rounded-xl bg-[#121B31]">
                  <dt class="text-xs text-surface-variant/70">Account status</dt>
                  <dd id="nmvs-account-status" class="mt-1 font-medium">Loading...</dd>
                </div>
                <div class="p-3 rounded-xl bg-[#121B31]">
                  <dt class="text-xs text-surface-variant/70">Member since</dt>
                  <dd id="nmvs-account-created" class="mt-1 font-medium">Loading...</dd>
                </div>
              </dl>
            </div>
            <form id="nmvs-change-password-form" class="flex flex-col gap-3 border-t border-white/10 pt-4">
              <h3 class="text-sm font-semibold">Change password</h3>
              <label class="flex flex-col gap-1 text-xs text-surface-variant">
                Current password
                <input name="current_password" type="password" required autocomplete="current-password" class="px-3 py-2.5 rounded-xl bg-[#121B31] border border-white/10 text-sm text-white focus:outline-none focus:border-primary-container" />
              </label>
              <label class="flex flex-col gap-1 text-xs text-surface-variant">
                New password
                <input name="new_password" type="password" required minlength="8" maxlength="128" autocomplete="new-password" class="px-3 py-2.5 rounded-xl bg-[#121B31] border border-white/10 text-sm text-white focus:outline-none focus:border-primary-container" />
              </label>
              <label class="flex flex-col gap-1 text-xs text-surface-variant">
                Confirm new password
                <input name="confirm_password" type="password" required minlength="8" maxlength="128" autocomplete="new-password" class="px-3 py-2.5 rounded-xl bg-[#121B31] border border-white/10 text-sm text-white focus:outline-none focus:border-primary-container" />
              </label>
              <p class="text-[11px] text-surface-variant/70">Use at least 8 characters, including uppercase, lowercase, a number, and a symbol.</p>
              <button type="submit" class="mt-1 px-4 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-white text-sm font-semibold">Update password</button>
            </form>
          </div>
        </section>`;
      document.body.appendChild(modal);

      const closeModal = () => modal.remove();
      modal.querySelectorAll('[data-close-account-settings]').forEach(button => {
        button.addEventListener('click', closeModal);
      });
      modal.addEventListener('click', event => {
        if (event.target === modal) closeModal();
      });

      try {
        const user = await this.getMe();
        modal.querySelector('#nmvs-account-username').textContent = user.username;
        modal.querySelector('#nmvs-account-email').textContent = user.email;
        modal.querySelector('#nmvs-account-status').textContent = user.is_active ? 'Active' : 'Inactive';
        modal.querySelector('#nmvs-account-created').textContent = user.created_at
          ? new Date(user.created_at).toLocaleDateString()
          : '—';
        const store = localStorage.getItem('NMVS_AUTH_TOKEN') ? localStorage : sessionStorage;
        store.setItem('NMVS_AUTH_USER', JSON.stringify(user));
        this.updateUserHeader();
      } catch (err) {
        this.showToast(`Could not load account profile: ${err.message}`, 'error');
        closeModal();
        return;
      }

      modal.querySelector('#nmvs-change-password-form').addEventListener('submit', async event => {
        event.preventDefault();
        const form = event.currentTarget;
        const submit = form.querySelector('button[type="submit"]');
        const formData = new FormData(form);
        const newPassword = formData.get('new_password');
        if (newPassword !== formData.get('confirm_password')) {
          this.showToast('New password and confirmation do not match.', 'error');
          return;
        }

        submit.disabled = true;
        submit.textContent = 'Updating...';
        try {
          const result = await this.changePassword({
            current_password: formData.get('current_password'),
            new_password: newPassword,
            confirm_password: formData.get('confirm_password'),
          });
          form.reset();
          this.showToast(result.message || 'Password updated successfully.', 'success');
        } catch (err) {
          this.showToast(`Could not update password: ${err.message}`, 'error');
        } finally {
          submit.disabled = false;
          submit.textContent = 'Update password';
        }
      });
    },

    // Modal: Settings & Backend URL Config
    openSettingsModal() {
      let modal = document.getElementById('nmvs-settings-modal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'nmvs-settings-modal';
        modal.className = 'fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-[#0a1122]/70 backdrop-blur-md transition-all';
        modal.innerHTML = `
          <div class="w-full max-w-md bg-[#17233F] text-white rounded-2xl shadow-2xl border border-white/10 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div class="p-5 border-b border-white/10 flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center text-primary-container">
                  <span class="material-symbols-outlined text-[20px]">tune</span>
                </div>
                <div class="flex flex-col">
                  <h3 class="font-headline-md font-bold text-base leading-tight">Backend API Settings</h3>
                  <span class="text-xs text-surface-variant/80">Configure NMVS FastAPI Connection</span>
                </div>
              </div>
              <button class="p-1 rounded-lg text-surface-variant hover:text-white hover:bg-white/10" onclick="document.getElementById('nmvs-settings-modal').remove()">
                <span class="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <div class="p-5 flex flex-col gap-4">
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-surface-variant uppercase tracking-wider">FastAPI Endpoint URL</label>
                <input id="nmvs-api-url-input" type="text" value="${this.baseUrl}" class="w-full px-3.5 py-2.5 rounded-xl bg-[#121B31] border border-white/10 text-white font-mono text-sm focus:outline-none focus:border-primary-container" />
                <span class="text-[11px] text-surface-variant/70">Default: http://localhost:8000</span>
              </div>
              <div class="flex items-center justify-between p-3 rounded-xl bg-[#121B31] border border-white/5">
                <div class="flex flex-col">
                  <span class="text-xs font-medium text-white">Status</span>
                  <span id="nmvs-modal-status-text" class="text-[11px] ${this.isOnline ? 'text-tertiary-container' : 'text-error'} font-semibold">
                    ${this.isOnline ? '● Online & Connected' : '● Offline / Unreachable'}
                  </span>
                </div>
                <button id="nmvs-test-conn-btn" class="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-all">
                  Test Connection
                </button>
              </div>
              <div class="flex flex-col gap-1.5 pt-2 border-t border-white/10">
                <span class="text-xs text-surface-variant">Fleet Quick Actions:</span>
                <button id="nmvs-seed-fleet-btn" class="w-full py-2 px-3 rounded-xl bg-[#202D4B] hover:bg-[#28385d] text-primary-container border border-primary-container/30 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all">
                  <span class="material-symbols-outlined text-[16px]">playlist_add</span>
                  Populate Demo Fleet Devices in DB
                </button>
              </div>
            </div>
            <div class="p-4 bg-[#121B31] border-t border-white/10 flex items-center justify-end gap-2">
              <button class="px-4 py-2 rounded-xl text-surface-variant hover:text-white text-xs font-medium" onclick="document.getElementById('nmvs-settings-modal').remove()">
                Cancel
              </button>
              <button id="nmvs-save-settings-btn" class="px-4 py-2 rounded-xl bg-primary text-white hover:bg-primary/90 text-xs font-semibold shadow-md">
                Save &amp; Reconnect
              </button>
            </div>
          </div>
        `;
        document.body.appendChild(modal);

        // Bind modal actions
        const input = document.getElementById('nmvs-api-url-input');
        const testBtn = document.getElementById('nmvs-test-conn-btn');
        const saveBtn = document.getElementById('nmvs-save-settings-btn');
        const seedBtn = document.getElementById('nmvs-seed-fleet-btn');
        const statusText = document.getElementById('nmvs-modal-status-text');

        testBtn.onclick = async () => {
          testBtn.innerText = 'Testing...';
          const tempBase = input.value.trim().replace(/\/+$/, '');
          try {
            const res = await fetch(`${tempBase}/health`);
            if (res.ok) {
              statusText.className = 'text-[11px] text-tertiary-container font-semibold';
              statusText.innerText = '● Online & Connected (:8000)';
              NMVS_API.showToast('Backend is responding healthy!', 'success');
            } else {
              throw new Error(`HTTP ${res.status}`);
            }
          } catch (e) {
            statusText.className = 'text-[11px] text-error font-semibold';
            statusText.innerText = '● Failed: ' + e.message;
            NMVS_API.showToast('Could not reach backend: ' + e.message, 'error');
          } finally {
            testBtn.innerText = 'Test Connection';
          }
        };

        saveBtn.onclick = () => {
          const newUrl = input.value.trim();
          if (newUrl) {
            NMVS_API.setBaseUrl(newUrl);
            modal.remove();
            NMVS_API.showToast('API URL saved. Reconnected.', 'success');
            setTimeout(() => window.location.reload(), 500);
          }
        };

        seedBtn.onclick = async () => {
          seedBtn.innerText = 'Seeding devices...';
          seedBtn.disabled = true;
          try {
            const seeded = await NMVS_API.seedSampleFleet();
            NMVS_API.showToast(`Seeded ${seeded.length} devices into database!`, 'success');
            modal.remove();
            setTimeout(() => window.location.reload(), 800);
          } catch (e) {
            NMVS_API.showToast('Seeding error: ' + e.message, 'error');
            seedBtn.innerText = 'Populate Demo Fleet Devices in DB';
            seedBtn.disabled = false;
          }
        };
      }
    },

    // Reports Modal
    openReportsModal() {
      let modal = document.getElementById('nmvs-reports-modal');
      if (modal) modal.remove();

      modal = document.createElement('div');
      modal.id = 'nmvs-reports-modal';
      modal.className = 'fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-[#0a1122]/70 backdrop-blur-md transition-all';
      modal.innerHTML = `
        <div class="w-full max-w-md bg-[#17233F] text-white rounded-2xl shadow-2xl border border-white/10 overflow-hidden">
          <div class="p-5 border-b border-white/10 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <div class="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center text-primary-container">
                <span class="material-symbols-outlined text-[20px]">analytics</span>
              </div>
              <div>
                <h3 class="font-headline-md font-bold text-base leading-tight">Generate Reports</h3>
                <span class="text-xs text-surface-variant/80">Export network telemetry data from backend</span>
              </div>
            </div>
            <button class="p-1 rounded-lg text-surface-variant hover:text-white" onclick="document.getElementById('nmvs-reports-modal').remove()">
              <span class="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>
          <div class="p-5 flex flex-col gap-3">
            <a href="${this.getDevicesCsvUrl()}" target="_blank" download class="p-3.5 rounded-xl bg-[#121B31] hover:bg-[#1c2949] border border-white/10 flex items-center justify-between transition-all group">
              <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-container text-[24px]">description</span>
                <div class="flex flex-col">
                  <span class="text-sm font-semibold text-white group-hover:text-primary-container transition-colors">Fleet Inventory CSV</span>
                  <span class="text-xs text-surface-variant/80">All registered devices, IPs, and hardware</span>
                </div>
              </div>
              <span class="material-symbols-outlined text-surface-variant group-hover:text-white text-[18px]">download</span>
            </a>
            <a href="${this.getExecutivePdfUrl()}" target="_blank" download class="p-3.5 rounded-xl bg-[#121B31] hover:bg-[#1c2949] border border-white/10 flex items-center justify-between transition-all group">
              <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-secondary-container text-[24px]">picture_as_pdf</span>
                <div class="flex flex-col">
                  <span class="text-sm font-semibold text-white group-hover:text-secondary-container transition-colors">Executive Summary PDF</span>
                  <span class="text-xs text-surface-variant/80">Full network health, SLA scores, &amp; metrics</span>
                </div>
              </div>
              <span class="material-symbols-outlined text-surface-variant group-hover:text-white text-[18px]">download</span>
            </a>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
    },

    // Initialization
    init() {
      this.setupNavigation();
      this.restoreSession();
      this.checkHealth();
      if (!this.pingInterval) {
        this.pingInterval = setInterval(() => this.checkHealth(), 12000);
      }
    },
  };

  window.NMVS_API = NMVS_API;

  document.addEventListener('DOMContentLoaded', () => {
    NMVS_API.init();
  });
})(window);
