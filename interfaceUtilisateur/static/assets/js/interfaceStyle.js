document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const resultBox = document.getElementById('search-results');
    const searchToggle = document.getElementById('searchToggle');
    const topbarSearch = document.getElementById('topbarSearch');
    const searchClose = document.getElementById('searchClose');

    // Afficher/Masquer la barre de recherche
    if (searchToggle && topbarSearch) {
        searchToggle.addEventListener('click', function (e) {
            e.preventDefault();
            topbarSearch.style.display = 'block';
        });
    }

    if (searchClose && topbarSearch) {
        searchClose.addEventListener('click', function () {
            topbarSearch.style.display = 'none';
        });
    }

    // Logique de recherche (inchangée)
    if (!searchInput || !resultBox) return;

    searchInput.addEventListener('keydown', function (event) {
        const query = this.value.trim();

        if (event.key === "Enter" && query.length > 1) {
            event.preventDefault();

            // Appel pour enregistrer l'historique
            fetch(`/produit/search/?q=${encodeURIComponent(query)}&save_history=true`, { method: 'GET' })
                .then(response => {
                    if (!response.ok) {
                        console.error('Erreur lors de l\'enregistrement de l\'historique');
                    }
                })
                .catch(error => {
                    console.error('Erreur réseau lors de l\'enregistrement de l\'historique:', error);
                });

            // Appel pour afficher les résultats
            resultBox.innerHTML = `
                <div class="text-center my-3" id="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    <p class="mt-2">Recherche en cours...</p>
                </div>
            `;

            fetch(`/produit/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultBox.innerHTML = '';

                    if (data.results.length === 0) {
                        resultBox.innerHTML = `
                            <div class="alert alert-warning text-center" role="alert">
                                <i class="bi bi-emoji-frown"></i> Aucun résultat trouvé.
                            </div>
                        `;
                        return;
                    }

                    data.results.forEach(item => {
                        const rowDiv = document.createElement('div');
                        rowDiv.classList.add('row', 'align-items-center', 'p-2', 'mb-2', 'border', 'rounded');
                        rowDiv.innerHTML = `
                            <div class="col-md-3"><strong class="product-name" style="color: skyblue;">${item.nom_produit}</strong></div>
                            <div class="col-md-3"><i class="bi bi-hospital"></i> ${item.nom_pharmacie}</div>
                            <div class="col-md-3"><i class="bi bi-geo-alt-fill"></i> ${item.adresse_pharmacie}</div>
                            <div class="col-md-2 text-success fw-bold">${item.prix} FNG</div>
                            <div class="col-md-1 text-end">
                                <a href="${item.detail_url}" class="btn btn-sm btn-outline-primary">Détails</a>
                            </div>
                        `;
                        resultBox.appendChild(rowDiv);
                    });
                })
                .catch(error => {
                    resultBox.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            Erreur de recherche : ${error.message}
                        </div>
                    `;
                });
        }
    });

    searchInput.addEventListener('keyup', function (event) {
        const query = this.value.trim();

        if (query.length > 1 && event.key !== "Enter") {
            resultBox.innerHTML = `
                <div class="text-center my-3" id="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    <p class="mt-2">Recherche en cours...</p>
                </div>
            `;

            fetch(`/produit/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultBox.innerHTML = '';

                    if (data.results.length === 0) {
                        resultBox.innerHTML = `
                            <div class="alert alert-warning text-center" role="alert">
                                <i class="bi bi-emoji-frown"></i> Aucun résultat trouvé.
                            </div>
                        `;
                        return;
                    }

                    data.results.forEach(item => {
                        const rowDiv = document.createElement('div');
                        rowDiv.classList.add('row', 'align-items-center', 'p-2', 'mb-2', 'border', 'rounded');
                        rowDiv.innerHTML = `
                            <div class="col-md-3"><strong class="product-name" style="color: skyblue;">${item.nom_produit}</strong></div>
                            <div class="col-md-3"><i class="bi bi-hospital"></i> ${item.nom_pharmacie}</div>
                            <div class="col-md-3"><i class="bi bi-geo-alt-fill"></i> ${item.adresse_pharmacie}</div>
                            <div class="col-md-2 text-success fw-bold">${item.prix} FNG</div>
                            <div class="col-md-1 text-end">
                                <a href="${item.detail_url}" class="btn btn-sm btn-outline-primary">Détails</a>
                            </div>
                        `;
                        resultBox.appendChild(rowDiv);
                    });
                })
                .catch(error => {
                    resultBox.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            Erreur de recherche : ${error.message}
                        </div>
                    `;
                });
        } else if (query.length <= 1) {
            resultBox.innerHTML = '';
        }
    });
});