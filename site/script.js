// site/script.js

const listEl = document.getElementById('list');
const filterEl = document.getElementById('filter');
const badgeEl = document.getElementById('badge');
const paginationEl = document.getElementById('pagination');

let grants = [];
let currentPage = 1;
const pageSize = 12;

// Fetch data
fetch('/data/grants.json')
  .then(r => r.json())
  .then(json => {
    grants = json;
    badgeEl.textContent = `Data refreshed: ${grants[0]?.retrieved_at}`;
    render();
  });

// ---- Load scraper_status.json and update badge ----
fetch('/data/scraper_status.json')
  .then(r => r.json())
  .then(status => {
    const failing = status.filter(s => s.error || s.n_grants === 0);
    const badge   = document.getElementById('status-badge');

    // Badge text & color
    if (failing.length === 0) {
      badge.textContent = 'All sources healthy';
      badge.classList.replace('bg-secondary', 'bg-success');
    } else {
      badge.textContent = `${failing.length} source(s) failing`;
      badge.classList.replace('bg-secondary', 'bg-danger');
    }

    // Build popover content
    const html = failing.length === 0
      ? '<p class="mb-0">Every scraper ran successfully on the last crawl.</p>'
      : '<ul class="mb-0">' + failing.map(f =>
          `<li><strong>${f.name}</strong> – ${f.error ? f.error : 'returned 0 grants'}</li>`
        ).join('') + '</ul>';

    // Initialise Bootstrap popover
    bootstrap.Popover.getOrCreateInstance(badge, {
      content: html,
      html: true,
      placement: 'bottom'
    });
  })
  .catch(err => console.error('Status fetch failed', err));

// Re-render on search
filterEl.addEventListener('input', () => {
  currentPage = 1;
  render();
});

function render() {
  const q = filterEl.value.toLowerCase();
  const filtered = grants.filter(g =>
    !q ||
    g.name.toLowerCase().includes(q) ||
    g.funder.toLowerCase().includes(q) ||
    g.region.toLowerCase().includes(q) ||
    g.tags.some(tag => tag.toLowerCase().includes(q))
  );

  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  currentPage = Math.min(currentPage, totalPages);

  // Render grants for current page
  listEl.innerHTML = '';
  const start = (currentPage - 1) * pageSize;
  const end = start + pageSize;
  filtered.slice(start, end).forEach(g => {
    const col = document.createElement('div');
    col.className = 'col';
    col.innerHTML = `
      <a href="${g.url}" target="_blank" class="card h-100 text-decoration-none">
        <div class="card-body">
          <h5 class="card-title">${g.name}</h5>
          <h6 class="card-subtitle mb-2 text-muted">${g.amount_min}–${g.amount_max} ${g.currency} • ${g.region}</h6>
          <p class="card-text">${g.description || ''}</p>
        </div>
      </a>`;
    listEl.appendChild(col);
  });

  // Render pagination
  paginationEl.innerHTML = '';
  for (let i = 1; i <= totalPages; i++) {
    const li = document.createElement('li');
    li.className = 'page-item' + (i === currentPage ? ' active' : '');
    const a = document.createElement('a');
    a.className = 'page-link';
    a.href = '#';
    a.textContent = i;
    a.addEventListener('click', (e) => {
      e.preventDefault();
      currentPage = i;
      render();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    li.appendChild(a);
    paginationEl.appendChild(li);
  }
}