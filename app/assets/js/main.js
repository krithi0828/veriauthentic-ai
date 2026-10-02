/* Client-Side Interactivity, Theme Switcher, Cmd+K Modal, & Chart Initializers */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initAuthCodeFormatter();
  initGlobalSearch();
  initBarcodeScanner();
  initPriceDeviationLive();
});

/* ------------------------------------------------------------------
   1. THEME SWITCHER (Light, Dark, System with localStorage)
   ------------------------------------------------------------------ */
function initTheme() {
  const savedTheme = localStorage.getItem('veri_theme') || 'dark';
  applyTheme(savedTheme);

  const themeToggleButtons = document.querySelectorAll('[data-action="toggle-theme"]');
  themeToggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('veri_theme', next);
    });
  });
}

function applyTheme(theme) {
  if (theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  } else {
    document.documentElement.setAttribute('data-theme', theme);
  }
}

/* ------------------------------------------------------------------
   2. AUTH CODE AUTO-FORMATTER (AUTH-XXXX-XXXX Mask & Uppercase)
   ------------------------------------------------------------------ */
function initAuthCodeFormatter() {
  const codeInputs = document.querySelectorAll('.js-auth-code-input');
  codeInputs.forEach(input => {
    input.addEventListener('input', (e) => {
      let val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
      if (val.startsWith('AUTH')) {
        val = val.substring(4);
      }
      
      let formatted = 'AUTH';
      if (val.length > 0) {
        formatted += '-' + val.substring(0, 4);
      }
      if (val.length > 4) {
        formatted += '-' + val.substring(4, 8);
      }
      e.target.value = formatted;
    });

    input.addEventListener('paste', (e) => {
      e.preventDefault();
      const pasted = (e.clipboardData || window.clipboardData).getData('text');
      let clean = pasted.toUpperCase().replace(/[^A-Z0-9]/g, '');
      if (clean.includes('AUTH')) {
        clean = clean.replace('AUTH', '');
      }
      let formatted = 'AUTH';
      if (clean.length > 0) formatted += '-' + clean.substring(0, 4);
      if (clean.length > 4) formatted += '-' + clean.substring(4, 8);
      e.target.value = formatted;
    });
  });
}

/* ------------------------------------------------------------------
   3. BARCODE DETECTOR BROWSER API INTEGRATION
   ------------------------------------------------------------------ */
function initBarcodeScanner() {
  const scanButtons = document.querySelectorAll('.js-barcode-scan-btn');
  if ('BarcodeDetector' in window) {
    scanButtons.forEach(btn => btn.style.display = 'inline-flex');
  } else {
    scanButtons.forEach(btn => btn.style.display = 'none');
  }
}

/* ------------------------------------------------------------------
   4. LIVE PRICE DEVIATION CALCULATOR
   ------------------------------------------------------------------ */
function initPriceDeviationLive() {
  const refInput = document.querySelector('.js-ref-price');
  const listInput = document.querySelector('.js-list-price');
  const previewBox = document.querySelector('.js-price-dev-preview');

  if (refInput && listInput && previewBox) {
    const update = () => {
      const ref = parseFloat(refInput.value) || 0;
      const list = parseFloat(listInput.value) || 0;
      if (ref > 0) {
        const dev = ((ref - list) / ref) * 100.0;
        let signal = 'Normal';
        let color = '#10b981';
        if (dev >= 40.0) { signal = 'Highly Suspicious (>40%)'; color = '#ef4444'; }
        else if (dev >= 15.0) { signal = 'Suspicious (15-40%)'; color = '#f59e0b'; }
        
        previewBox.innerHTML = `Price Deviation: <b>${dev.toFixed(1)}%</b> off MSRP (${signal})`;
        previewBox.style.color = color;
      }
    };
    refInput.addEventListener('input', update);
    listInput.addEventListener('input', update);
  }
}

/* ------------------------------------------------------------------
   5. GLOBAL SEARCH PALETTE (Cmd+K / Ctrl+K)
   ------------------------------------------------------------------ */
function initGlobalSearch() {
  const modal = document.getElementById('search-modal');
  if (!modal) return;

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      modal.style.display = modal.style.display === 'flex' ? 'none' : 'flex';
      const input = modal.querySelector('input');
      if (input) input.focus();
    } else if (e.key === 'Escape' && modal.style.display === 'flex') {
      modal.style.display = 'none';
    }
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.style.display = 'none';
  });
}
