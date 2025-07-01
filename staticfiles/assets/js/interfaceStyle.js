// Script de filtrage des recherche
document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const spinner = document.getElementById('loading-spinner');
  const filterLinks = document.querySelectorAll('.filter-option');

  let filters = {
    price: null,
    type: null,
    localite: null,
    stock: null,
    q: ''
  };

  function fetchFilteredProducts() {
    spinner.classList.remove('d-none');

    const params = new URLSearchParams(filters);
    fetch(`/produits/recherche/?${params.toString()}`)
      .then(response => response.text())
      .then(data => {
        searchResults.innerHTML = data;
        spinner.classList.add('d-none');
      })
      .catch(error => {
        console.error(error);
        spinner.classList.add('d-none');
      });
  }

  // Recherche live
  searchInput.addEventListener('input', () => {
    filters.q = searchInput.value.trim();
    fetchFilteredProducts();
  });

  // Application des filtres
  filterLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const filter = this.dataset.filter;
      const value = this.dataset.value;

      // Toggle du filtre (click 2 fois = retire le filtre)
      if (filters[filter] === value) {
        filters[filter] = null;
      } else {
        filters[filter] = value;
      }

      fetchFilteredProducts();
    });
  });
});
