// Auth + admin panel. Loaded last; gates the app behind /api/me.
(function () {
  'use strict';

  let currentUser = null;

  const api = async (path, opts) => {
    const res = await fetch('/api' + path, Object.assign({ headers: { 'Content-Type': 'application/json' } }, opts || {}));
    let body = null;
    try { body = await res.json(); } catch (e) { body = null; }
    if (!res.ok) throw new Error((body && body.error) || ('Request failed (' + res.status + ')'));
    return body;
  };

  function showApp(user) {
    currentUser = user;
    const screen = document.getElementById('authScreen');
    const shell = document.getElementById('appShell');
    screen.hidden = true;
    shell.hidden = false;
    document.getElementById('sidebarSignOut').hidden = false;
    renderUserChip();
  }

  function showLogin() {
    currentUser = null;
    document.getElementById('authScreen').hidden = false;
    document.getElementById('appShell').hidden = true;
    document.getElementById('sidebarSignOut').hidden = true;
    renderAuthScreen();
  }

  function renderUserChip() {
    const chip = document.getElementById('userChip');
    const head = document.getElementById('userDropdownHead');
    const adminLink = document.getElementById('adminLink');
    if (!currentUser) return;
    const initials = currentUser.name.split(/\s+/).map(function (p) { return p[0]; }).slice(0, 2).join('').toUpperCase();
    chip.textContent = initials + ' ' + currentUser.name;
    chip.title = currentUser.email;
    head.innerHTML = '<strong>' + esc(currentUser.name) + '</strong><small>' + esc(currentUser.role === 'admin' ? 'Administrator' : 'Group Executive') + ' · ' + esc(currentUser.email) + '</small>';
    adminLink.hidden = currentUser.role !== 'admin';
  }

  // ---- Sign-in screen ----
  function loginView() {
    return '<div class="auth-box">' +
      '<div class="auth-brand"><img class="brand-logo" src="anwar_big_logo.avif" alt="Anwar Group logo"><div class="brand-text">ANWAR GROUP<small>MANAGEMENT FINANCE</small></div></div>' +
      '<h1>Sign in</h1>' +
      '<p class="auth-sub">Access the finance dashboard.</p>' +
      '<form id="loginForm" novalidate>' +
      '<label class="auth-label" for="loginEmail">Email</label>' +
      '<input class="auth-input" id="loginEmail" name="email" type="email" autocomplete="username" required placeholder="you@anwargroup.com">' +
      '<label class="auth-label" for="loginPassword">Password</label>' +
      '<input class="auth-input" id="loginPassword" name="password" type="password" autocomplete="current-password" required placeholder="••••••••">' +
      '<p class="auth-error" id="loginError" role="alert" hidden></p>' +
      '<button class="auth-btn" type="submit" id="loginBtn">Sign in</button>' +
      '</form>' +
      '<p class="auth-foot">Forgot your password? Ask an administrator to resend your reset link.</p>' +
      '</div>';
  }

  function resetView(token) {
    return '<div class="auth-box">' +
      '<div class="auth-brand"><img class="brand-logo" src="anwar_big_logo.avif" alt="Anwar Group logo"><div class="brand-text">ANWAR GROUP<small>MANAGEMENT FINANCE</small></div></div>' +
      '<h1>Set your password</h1>' +
      '<p class="auth-sub">Choose a new password to activate your account.</p>' +
      '<form id="resetForm" novalidate>' +
      '<label class="auth-label" for="resetPassword">New password</label>' +
      '<input class="auth-input" id="resetPassword" name="password" type="password" autocomplete="new-password" required minlength="8" placeholder="At least 8 characters">' +
      '<label class="auth-label" for="resetConfirm">Confirm password</label>' +
      '<input class="auth-input" id="resetConfirm" name="confirm" type="password" autocomplete="new-password" required minlength="8" placeholder="Repeat password">' +
      '<p class="auth-error" id="resetError" role="alert" hidden></p>' +
      '<button class="auth-btn" type="submit" id="resetBtn">Set password</button>' +
      '</form>' +
      '<p class="auth-foot">After setting your password, sign in with your email.</p>' +
      '</div>';
  }

  function renderAuthScreen() {
    const screen = document.getElementById('authScreen');
    const hash = location.hash;
    if (hash.startsWith('#reset')) {
      const params = new URLSearchParams(hash.slice(7));
      const token = params.get('token');
      screen.innerHTML = resetView(token);
      bindReset(token);
    } else {
      screen.innerHTML = loginView();
      bindLogin();
    }
  }

  function bindLogin() {
    const form = document.getElementById('loginForm');
    const err = document.getElementById('loginError');
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const email = document.getElementById('loginEmail').value.trim();
      const password = document.getElementById('loginPassword').value;
      err.hidden = true;
      const btn = document.getElementById('loginBtn');
      btn.disabled = true; btn.textContent = 'Signing in…';
      try {
        const user = await api('/login', { method: 'POST', body: JSON.stringify({ email: email, password: password }) });
        showApp(user);
        if (typeof loadData === 'function') await loadData();
        if (location.hash.slice(1) === 'admin' && typeof state !== 'undefined') {
          state.view = 'admin';
          if (typeof render === 'function') render();
        }
      } catch (ex) {
        err.textContent = ex.message; err.hidden = false;
      } finally {
        btn.disabled = false; btn.textContent = 'Sign in';
      }
    });
  }

  function bindReset(token) {
    const form = document.getElementById('resetForm');
    const err = document.getElementById('resetError');
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const pw = document.getElementById('resetPassword').value;
      const confirm = document.getElementById('resetConfirm').value;
      err.hidden = true;
      if (pw.length < 8) { err.textContent = 'Password must be at least 8 characters.'; err.hidden = false; return; }
      if (pw !== confirm) { err.textContent = 'Passwords do not match.'; err.hidden = false; return; }
      const btn = document.getElementById('resetBtn');
      btn.disabled = true; btn.textContent = 'Saving…';
      try {
        await api('/reset', { method: 'POST', body: JSON.stringify({ token: token, password: pw }) });
        location.hash = '';
        renderAuthScreen();
        const loginErr = document.getElementById('loginError');
        if (loginErr) { loginErr.textContent = 'Password set. Sign in to continue.'; loginErr.hidden = false; loginErr.style.color = '#137a56'; }
      } catch (ex) {
        err.textContent = ex.message; err.hidden = false;
      } finally {
        btn.disabled = false; btn.textContent = 'Set password';
      }
    });
  }

  // ---- Admin panel ----
  function roleSelect(roles, id) {
    return '<select id="' + id + '">' + roles.map(function (r) { return '<option value="' + esc(r.key) + '">' + esc(r.label) + '</option>'; }).join('') + '</select>';
  }

  function sbuSelect(sbus, id) {
    return '<select id="' + id + '"><option value="">All SBUs (full access)</option>' + sbus.map(function (s) { return '<option value="' + esc(s.name) + '">' + esc(s.name) + '</option>'; }).join('') + '</select>';
  }

  function adminViewBody(roles, sbus) {
    return '<div id="adminError" class="negative" role="alert"></div>' +
      '<h3>Add a user</h3>' +
      '<form id="addUserForm" class="admin-form" novalidate>' +
      '<div class="field"><label for="newUserName">Name</label><input class="search" id="newUserName" placeholder="Full name" required></div>' +
      '<div class="field"><label for="newUserEmail">Email</label><input class="search" id="newUserEmail" type="email" placeholder="name@anwargroup.com" required></div>' +
      '<div class="field"><label for="newUserRole">Role</label>' + roleSelect(roles, 'newUserRole') + '</div>' +
      '<div class="field"><label for="newUserSbu">Data access (SBU)</label>' + sbuSelect(sbus, 'newUserSbu') + '</div>' +
      '<div class="field"><label for="newUserPassword">Password</label><input class="search" id="newUserPassword" type="text" placeholder="Leave blank to email a reset link" minlength="8"></div>' +
      '<div class="field"><button class="action primary" type="submit" id="addUserBtn">Create user</button></div>' +
      '</form>' +
      '<p class="source">Admins see all SBUs and the Admin menu. Other users see only their assigned SBU (or all SBUs if "All SBUs" is selected). If you leave the password blank, a reset link is emailed instead.</p>' +
      '<p class="source" id="newUserLink" hidden></p>' +
      '<h3>Active users</h3>' +
      '<div id="userTable"></div>' +
      '<div class="admin-sections">' +
      '<div class="admin-sub">' +
      '<h3>Add a new role</h3>' +
      '<form id="addRoleForm" class="admin-inline" novalidate>' +
      '<input class="search" id="newRoleLabel" placeholder="Role name, e.g. Finance Head" required>' +
      '<button class="action" type="submit" id="addRoleBtn">Add role</button>' +
      '</form>' +
      '</div>' +
      '<div class="admin-sub">' +
      '<h3>Add a new SBU</h3>' +
      '<form id="addSbuForm" class="admin-inline" novalidate>' +
      '<input class="search" id="newSbuName" placeholder="SBU name, e.g. Anwar Cement Sheet" required>' +
      '<input class="search" id="newSbuCode" placeholder="Code, e.g. ACSL">' +
      '<button class="action" type="submit" id="addSbuBtn">Add SBU</button>' +
      '</form>' +
      '</div>' +
      '</div>';
  }

  window.adminView = function () {
    return '<section class="panel wide"><div id="adminBody">Loading…</div></section>';
  };

  function showResetLink(link) {
    const el = document.getElementById('newUserLink');
    if (el) {
      el.hidden = false;
      el.innerHTML = 'Password reset link (also emailed): <a href="' + esc(link) + '" target="_blank">' + esc(link) + '</a>';
    }
  }

  function roleLabel(role) {
    const map = { admin: 'Administrator', group_executive: 'Group Executive' };
    return map[role] || role;
  }

  function renderUserTable() {
    const el = document.getElementById('userTable');
    if (!el) return;
    el.innerHTML = '<p class="muted">Loading users…</p>';
    api('/users').then(function (users) {
      el.innerHTML = '<div class="tablewrap"><table><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>SBU</th><th>Password</th><th></th></tr></thead><tbody>' +
        users.map(function (u) {
          return '<tr><td>' + esc(u.name) + '</td><td>' + esc(u.email) + '</td><td>' + esc(roleLabel(u.role)) + '</td><td>' + esc(u.sbu || 'All SBUs') + '</td>' +
            '<td>' + (u.password ? '<span class="password-cell" title="' + esc(u.password) + '">' + esc(u.password) + '</span>' : '<span class="negative">Not set</span>') + '</td>' +
            '<td><button class="action" data-edit="' + u.id + '">Edit</button> <button class="action" data-reset="' + u.id + '">Resend reset link</button> <button class="action" data-delete="' + u.id + '">Delete</button></td></tr>';
        }).join('') + '</tbody></table></div>';
      bindUserActions(users);
    }).catch(function (ex) {
      el.innerHTML = '<p class="negative">' + esc(ex.message) + '</p>';
    });
  }

  function openEditDialog(user) {
    document.getElementById('editUserName').value = user.name;
    document.getElementById('editUserEmail').value = user.email;
    document.getElementById('editUserPassword').value = '';
    document.getElementById('editUserError').textContent = '';
    // Populate role + SBU dropdowns from the API.
    Promise.all([
      api('/roles').catch(function () { return [{ key: 'admin', label: 'Administrator' }, { key: 'group_executive', label: 'Group Executive' }]; }),
      api('/sbus').catch(function () { return []; })
    ]).then(function (results) {
      const roles = results[0], sbus = results[1];
      document.getElementById('editUserRole').innerHTML = roles.map(function (r) {
        return '<option value="' + esc(r.key) + '"' + (r.key === user.role ? ' selected' : '') + '>' + esc(r.label) + '</option>';
      }).join('');
      document.getElementById('editUserSbu').innerHTML = '<option value="">All SBUs (full access)</option>' + sbus.map(function (s) {
        return '<option value="' + esc(s.name) + '"' + (s.name === user.sbu ? ' selected' : '') + '>' + esc(s.name) + '</option>';
      }).join('');
      document.getElementById('editUserDialog').dataset.userId = user.id;
      document.getElementById('editUserDialog').showModal();
    });
  }

  function bindUserActions(users) {
    document.querySelectorAll('[data-edit]').forEach(function (btn) {
      btn.onclick = function () {
        const id = btn.dataset.edit;
        const u = users.find(function (x) { return String(x.id) === String(id); });
        if (u) openEditDialog(u);
      };
    });
    document.querySelectorAll('[data-reset]').forEach(function (btn) {
      btn.onclick = async function () {
        const id = btn.dataset.reset;
        btn.disabled = true; btn.textContent = 'Sending…';
        try {
          const r = await api('/users/' + id + '/reset', { method: 'POST' });
          showResetLink(r.reset_link);
          btn.textContent = 'Sent ✓';
          setTimeout(function () { btn.textContent = 'Resend reset link'; }, 3000);
        } catch (ex) {
          document.getElementById('adminError').textContent = ex.message;
          btn.textContent = 'Resend reset link';
        } finally {
          btn.disabled = false;
        }
      };
    });
    document.querySelectorAll('[data-delete]').forEach(function (btn) {
      btn.onclick = async function () {
        const id = btn.dataset.delete;
        const u = users.find(function (x) { return String(x.id) === String(id); });
        if (!confirm('Delete user ' + (u ? u.email : '') + '? This cannot be undone.')) return;
        try {
          await api('/users/' + id, { method: 'DELETE' });
          renderUserTable();
        } catch (ex) {
          document.getElementById('adminError').textContent = ex.message;
        }
      };
    });
  }

  function bindAdmin() {
    const body = document.getElementById('adminBody');
    if (!body) return;
    Promise.all([
      api('/roles').catch(function () { return [{ key: 'admin', label: 'Administrator' }, { key: 'group_executive', label: 'Group Executive' }]; }),
      api('/sbus').catch(function () { return []; })
    ]).then(function (results) {
      const roles = results[0], sbus = results[1];
      body.innerHTML = adminViewBody(roles, sbus);
      bindAddUser();
      bindAddRole();
      bindAddSbu();
      bindEditUserDialog();
      renderUserTable();
    });
  }

  function bindEditUserDialog() {
    const dialog = document.getElementById('editUserDialog');
    const cancelBtn = document.getElementById('cancelEditBtn');
    const saveBtn = document.getElementById('saveUserBtn');
    if (!dialog || !cancelBtn || !saveBtn) return;
    cancelBtn.onclick = function () { dialog.close(); };
    saveBtn.onclick = async function () {
      const id = dialog.dataset.userId;
      const name = document.getElementById('editUserName').value.trim();
      const email = document.getElementById('editUserEmail').value.trim();
      const role = document.getElementById('editUserRole').value;
      const sbu = document.getElementById('editUserSbu').value;
      const password = document.getElementById('editUserPassword').value.trim();
      const err = document.getElementById('editUserError');
      err.textContent = '';
      if (!name) { err.textContent = 'Name is required.'; return; }
      if (password && password.length < 8) { err.textContent = 'Password must be at least 8 characters.'; return; }
      saveBtn.disabled = true; saveBtn.textContent = 'Saving…';
      try {
        await api('/users/' + id, { method: 'PUT', body: JSON.stringify({ name: name, email: email, role: role, sbu: sbu, password: password }) });
        dialog.close();
        renderUserTable();
      } catch (ex) {
        err.textContent = ex.message;
      } finally {
        saveBtn.disabled = false; saveBtn.textContent = 'Save changes';
      }
    };
  }

  function bindAddUser() {
    const form = document.getElementById('addUserForm');
    if (!form) return;
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      document.getElementById('adminError').textContent = '';
      document.getElementById('newUserLink').hidden = true;
      const name = document.getElementById('newUserName').value.trim();
      const email = document.getElementById('newUserEmail').value.trim();
      const role = document.getElementById('newUserRole').value;
      const sbu = document.getElementById('newUserSbu').value.trim();
      const password = document.getElementById('newUserPassword').value.trim();
      const btn = document.getElementById('addUserBtn');
      btn.disabled = true; btn.textContent = 'Creating…';
      try {
        const r = await api('/users', { method: 'POST', body: JSON.stringify({ name: name, email: email, role: role, sbu: sbu, password: password }) });
        form.reset();
        if (r.reset_link) showResetLink(r.reset_link);
      } catch (ex) {
        document.getElementById('adminError').textContent = ex.message;
      } finally {
        btn.disabled = false; btn.textContent = 'Create user';
      }
    });
  }

  function bindAddRole() {
    const form = document.getElementById('addRoleForm');
    if (!form) return;
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const label = document.getElementById('newRoleLabel').value.trim();
      const btn = document.getElementById('addRoleBtn');
      document.getElementById('adminError').textContent = '';
      btn.disabled = true; btn.textContent = 'Adding…';
      try {
        await api('/roles', { method: 'POST', body: JSON.stringify({ label: label }) });
        form.reset();
        bindAdmin(); // refresh role dropdown
      } catch (ex) {
        document.getElementById('adminError').textContent = ex.message;
      } finally {
        btn.disabled = false; btn.textContent = 'Add role';
      }
    });
  }

  function bindAddSbu() {
    const form = document.getElementById('addSbuForm');
    if (!form) return;
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const name = document.getElementById('newSbuName').value.trim();
      const code = document.getElementById('newSbuCode').value.trim();
      const btn = document.getElementById('addSbuBtn');
      document.getElementById('adminError').textContent = '';
      btn.disabled = true; btn.textContent = 'Adding…';
      try {
        await api('/sbus', { method: 'POST', body: JSON.stringify({ name: name, code: code }) });
        form.reset();
        bindAdmin(); // refresh SBU dropdown
      } catch (ex) {
        document.getElementById('adminError').textContent = ex.message;
      } finally {
        btn.disabled = false; btn.textContent = 'Add SBU';
      }
    });
  }

  // ---- Header dropdown ----
  function bindHeader() {
    const chip = document.getElementById('userChip');
    const dropdown = document.getElementById('userDropdown');
    chip.addEventListener('click', function (e) {
      e.stopPropagation();
      dropdown.hidden = !dropdown.hidden;
    });
    document.addEventListener('click', function () { dropdown.hidden = true; });
    dropdown.addEventListener('click', function (e) { e.stopPropagation(); });
    document.getElementById('signOutBtn').addEventListener('click', async function () {
      try { await api('/logout', { method: 'POST' }); } catch (e) {}
      location.hash = '';
      showLogin();
    });
    const sidebarSignOut = document.getElementById('sidebarSignOut');
    sidebarSignOut.addEventListener('click', async function () {
      try { await api('/logout', { method: 'POST' }); } catch (e) {}
      location.hash = '';
      showLogin();
    });
    document.getElementById('adminLink').addEventListener('click', function () {
      dropdown.hidden = true;
      if (typeof state !== 'undefined') { state.view = 'admin'; }
      location.hash = 'admin';
      if (typeof render === 'function') render();
    });
  }

  // ---- Integrate admin view into nav ----
  function registerAdminView() {
    if (typeof views !== 'undefined') {
      views.admin = 'Admin';
    }
  }

  // ---- Access control ----
  function isAdmin() {
    return !!(currentUser && currentUser.role === 'admin');
  }

  // Returns [[id, sbu], ...] the current user is allowed to see.
  function allowedSbuEntries() {
    if (typeof portfolio === 'undefined' || !portfolio || !portfolio.sbus) return [];
    const entries = Object.entries(portfolio.sbus);
    if (isAdmin()) return entries;
    const target = ((currentUser && currentUser.sbu) || '').trim().toLowerCase();
    if (!target) return entries; // no restriction assigned
    return entries.filter(function (pair) {
      const s = pair[1];
      return ((s.name || '').toLowerCase() === target) || ((s.code || '').toLowerCase() === target);
    });
  }

  function applyAccessControl() {
    if (!currentUser || typeof portfolio === 'undefined' || !portfolio.sbus) return;
    const admin = isAdmin();

    // 1. Non-admins must never see the Admin menu. Remove it entirely,
    //    not just hide it, so it cannot be revealed by any later re-render.
    document.querySelectorAll('#nav [data-view="admin"]').forEach(function (b) {
      if (admin) { b.style.display = ''; } else { b.remove(); }
    });
    // Header user-dropdown "Admin panel" link (separate element).
    const adminLink = document.getElementById('adminLink');
    if (adminLink) adminLink.hidden = !admin;

    // 2. Restrict the SBU selectors to the allowed SBUs.
    const allowed = allowedSbuEntries();
    const allowedIds = new Set(allowed.map(function (p) { return p[0]; }));

    const sel = document.getElementById('sbu');
    if (sel) {
      Array.prototype.slice.call(sel.options).forEach(function (o) {
        if (o.value && !allowedIds.has(o.value)) o.remove();
      });
    }
    document.querySelectorAll('[data-active-sbu]').forEach(function (b) {
      if (!allowedIds.has(b.dataset.activeSbu)) b.remove();
    });

    // 3. If the active SBU is not allowed, switch to the first allowed one.
    if (typeof activeSbu !== 'undefined' && !allowedIds.has(activeSbu)) {
      if (allowed.length) {
        activeSbu = allowed[0][0];
        if (typeof activate === 'function') activate(activeSbu);
      }
    }
  }

  function patchRender() {
    // After render(), re-render admin view content and header if needed.
    if (typeof bind !== 'function') return;
    const originalRender = (typeof render === 'function') ? render : null;
    if (!originalRender) return;
    window.render = function () {
      // Prevent non-admins from reaching the admin view.
      if (typeof state !== 'undefined' && state.view === 'admin' && !isAdmin()) {
        state.view = 'overview';
        location.hash = 'overview';
      }
      originalRender();
      applyAccessControl();
      const adminViewActive = isAdmin() && state && state.view === 'admin';
      // On the admin view, hide the finance-specific controls (active SBU strip,
      // year/month/unit toolbar) so only the Add-user form is shown.
      const controls = document.getElementById('sbuControls');
      const toolbar = document.getElementById('toolbar');
      const footer = document.querySelector('main footer');
      if (controls) controls.style.display = adminViewActive ? 'none' : '';
      if (toolbar) toolbar.style.display = adminViewActive ? 'none' : (state && state.view === 'upload' ? 'none' : '');
      if (footer) footer.style.display = adminViewActive ? 'none' : '';
      if (adminViewActive) {
        const content = document.getElementById('content');
        content.innerHTML = '<div class="layout">' + adminView() + '</div>';
        bindAdmin();
      }
    };
  }

  // ---- Boot ----
  async function boot() {
    registerAdminView();
    bindHeader();
    // A reset link always takes priority — show the set-password screen
    // even if a session already exists (e.g. admin opens a user's link).
    if (location.hash.startsWith('#reset')) {
      renderAuthScreen();
      showLogin();
      return;
    }
    // Gate: only reveal app once authenticated.
    try {
      const user = await api('/me');
      patchRender();
      showApp(user);
      if (typeof loadData === 'function') await loadData();
      if (location.hash.slice(1) === 'admin' && typeof state !== 'undefined') {
        state.view = 'admin';
        if (typeof render === 'function') render();
      }
    } catch (e) {
      patchRender();
      renderAuthScreen();
      showLogin();
    }
  }

  // Re-check auth when hash changes (for reset link / admin deep link).
  window.addEventListener('hashchange', function () {
    if (location.hash.startsWith('#reset')) {
      renderAuthScreen();
      showLogin();
    } else if (!currentUser) {
      renderAuthScreen();
    } else if (state && state.view === 'admin' && location.hash === '#admin') {
      if (typeof render === 'function') render();
    }
  });

  document.addEventListener('DOMContentLoaded', boot);
  if (document.readyState !== 'loading') boot();
})();
