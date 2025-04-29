/* Script pour l'ajout d'un formeset */
document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("formset-container");
    const totalForms = document.getElementById("id_form-TOTAL_FORMS");
    const addButton = document.getElementById("add-formset");
    const errorBox = document.getElementById("form-error");
    const emptyTemplate = document.getElementById("empty-form-template");

    function reindexForms() {
      const forms = container.querySelectorAll(".formset-item");
      forms.forEach((form, index) => {
        form.querySelectorAll("input, select, textarea, label").forEach((el) => {
          if (el.name) el.name = el.name.replace(/form-\d+-/, `form-${index}-`);
          if (el.id) el.id = el.id.replace(/form-\d+-/, `form-${index}-`);
          if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/form-\d+-/, `form-${index}-`);
        });
      });
      totalForms.value = forms.length;
    }

    function addNewForm() {
      const clone = emptyTemplate.content.cloneNode(true);
      container.appendChild(clone);
      reindexForms();
      attachRemoveHandlers();
    }

    function attachRemoveHandlers() {
      container.querySelectorAll(".remove-form").forEach((button) => {
        button.onclick = function () {
          const item = button.closest(".formset-item");
          item.classList.add("animate__fadeOut");
          setTimeout(() => {
            item.remove();
            if (container.querySelectorAll(".formset-item").length === 0) {
              addNewForm();
            } else {
              reindexForms();
            }
          }, 300);
        };
      });
    }

    addButton.addEventListener("click", function () {
      errorBox.style.display = "none";
      const lastForm = container.querySelector(".formset-item:last-child");
      const inputs = lastForm.querySelectorAll("input, select");
      const isEmpty = Array.from(inputs).every(
        (input) => input.value.trim() === ""
      );
      if (isEmpty) {
        errorBox.innerText =
          "⚠️ Veuillez d'abord remplir la dernière ligne avant d'en ajouter une nouvelle.";
        errorBox.style.display = "block";
        return;
      }
      addNewForm();
    });

    document.querySelector("form").addEventListener("submit", function (e) {
      const forms = container.querySelectorAll(".formset-item");
      const filled = Array.from(forms).some((form) => {
        const formSelect = form.querySelector('select[name*="form"]');
        const dosageInput = form.querySelector('input[name*="dosage"]');
        const priceInput = form.querySelector('input[name*="price"]');
        return (
          formSelect?.value.trim() &&
          dosageInput?.value.trim() &&
          priceInput?.value.trim()
        );
      });

      if (!filled) {
        e.preventDefault();
        errorBox.innerText =
          "⚠️ Veuillez remplir au moins une ligne de forme, dosage et prix.";
        errorBox.style.display = "block";
      }
    });

    attachRemoveHandlers();
  });

    // Cacher automatiquement les alertes après 3 secondes
    setTimeout(function () {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 3000); // 3000 ms = 3 secondes

    // Disparaître avec animation douce après 3 secondes
    setTimeout(function () {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            alert.classList.remove('alert-slide');
            alert.classList.add('alert-disappear');

            // Supprime complètement l'alerte après l'animation
            setTimeout(function () {
                alert.remove();
            }, 500); // Durée de l'animation fadeOut
        });
    }, 3000); // Après 3 secondes

