/**
 * Filter pre-rendered publication items (Jekyll dossier layout).
 */
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('publication-search');
  const clearBtn = document.getElementById('clear-search');
  const filterResults = document.getElementById('filter-results');
  const emptyState = document.getElementById('publications-empty');
  const items = Array.from(document.querySelectorAll('.dossier-pub-item'));
  const yearHeaders = Array.from(document.querySelectorAll('.dossier-pub-year'));

  if (!searchInput || items.length === 0) return;

  const total = items.length;

  function updateYearHeaders() {
    yearHeaders.forEach((header) => {
      const year = header.dataset.year;
      const visibleInYear = items.some(
        (item) => item.dataset.year === year && !item.hidden
      );
      header.hidden = !visibleInYear;
    });
  }

  function filterPublications(term) {
    const query = term.toLowerCase().trim();
    let visibleCount = 0;

    items.forEach((item) => {
      const haystack = item.dataset.search || '';
      const match = query === '' || haystack.includes(query);
      item.hidden = !match;
      if (match) visibleCount += 1;
    });

    updateYearHeaders();

    if (filterResults) {
      filterResults.textContent =
        query === ''
          ? `Showing all ${total} publications`
          : `Showing ${visibleCount} of ${total} publications`;
    }

    if (emptyState) {
      emptyState.hidden = visibleCount > 0;
    }

    if (clearBtn) {
      clearBtn.hidden = query === '';
    }
  }

  searchInput.addEventListener('input', (event) => {
    filterPublications(event.target.value);
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      searchInput.value = '';
      filterPublications('');
      searchInput.focus();
    });
  }

  searchInput.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      searchInput.value = '';
      filterPublications('');
    }
  });
});
