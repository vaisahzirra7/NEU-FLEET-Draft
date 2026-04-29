/* VanaraFleetsOps — Main JS */
document.addEventListener('DOMContentLoaded', () => {

  // ── Sidebar mobile toggle ──────────────────────────────
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('overlay');
  const toggleBtn = document.getElementById('sidebarToggle');

  function openSidebar() {
    sidebar?.classList.add('open');
    overlay?.classList.add('show');
  }
  function closeSidebar() {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('show');
  }

  toggleBtn?.addEventListener('click', openSidebar);
  overlay?.addEventListener('click', closeSidebar);

  // ── Active nav item ────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item[href]').forEach(link => {
    if (currentPath.startsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });

  // ── Auto-dismiss alerts ────────────────────────────────
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // ── Confirm delete buttons ─────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => {
      const msg = btn.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ── Form: auto-calculate total value (coupon form) ─────
  const litresInput = document.getElementById('id_litres');
  const costInput   = document.getElementById('id_cost_per_litre');
  const totalEl     = document.getElementById('total-value-display');

  function updateTotal() {
    if (!litresInput || !costInput || !totalEl) return;
    const l = parseFloat(litresInput.value) || 0;
    const c = parseFloat(costInput.value)   || 0;
    const t = l * c;
    totalEl.textContent = t > 0 ? '₦ ' + t.toLocaleString('en-NG', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : '—';
  }

  litresInput?.addEventListener('input', updateTotal);
  costInput?.addEventListener('input', updateTotal);
  updateTotal();

  // ── Coupon lookup: auto-fill on verification code input ─
  const couponLookupInput = document.getElementById('coupon-lookup');
  const couponLookupBtn   = document.getElementById('coupon-lookup-btn');

  couponLookupBtn?.addEventListener('click', async () => {
    const code = couponLookupInput?.value.trim();
    if (!code) return;

    couponLookupBtn.textContent = 'Looking up...';
    couponLookupBtn.disabled = true;

    try {
      const res = await fetch(`/coupons/lookup/?q=${encodeURIComponent(code)}`);
      const data = await res.json();

      if (data.error) {
        showInlineError('coupon-lookup-error', data.error);
      } else {
        // Populate hidden fields and display
        document.getElementById('id_coupon').value = data.id;
        document.getElementById('coupon-info-plate').textContent  = data.plate;
        document.getElementById('coupon-info-driver').textContent = data.driver;
        document.getElementById('coupon-info-litres').textContent = data.litres + ' L';
        document.getElementById('coupon-info-value').textContent  = '₦ ' + data.total_value;
        document.getElementById('coupon-info-box').style.display  = 'block';
        document.getElementById('coupon-lookup-error').textContent = '';
      }
    } catch {
      showInlineError('coupon-lookup-error', 'Network error. Please try again.');
    }

    couponLookupBtn.textContent = 'Look Up';
    couponLookupBtn.disabled = false;
  });

  function showInlineError(elId, msg) {
    const el = document.getElementById(elId);
    if (el) el.textContent = msg;
  }
});
