/* Script pour ma page my_pharmacy */

      document.getElementById("editBtn").addEventListener("click", function () {
        // Rendre les champs éditables
        var inputs = document.querySelectorAll("input, textarea");
        inputs.forEach(function (input) {
          input.removeAttribute("readonly");
          input.style.backgroundColor = "#fff"; // Optional: change background color when editable
        });

        // Afficher le bouton d'enregistrement et masquer le bouton de modification
        document.getElementById("submitBtn").style.display = "inline-block";
        document.getElementById("editBtn").style.display = "none";
      });

      document.addEventListener('DOMContentLoaded', function() {
        // Afficher les messages d'erreur et de succès avec animation
        var alertMessages = document.querySelectorAll('.alert');
        alertMessages.forEach(function(message) {
            message.classList.add('show');
        });
    });


    document.getElementById("edit-btn").addEventListener("click", function () {
        let inputs = document.querySelectorAll("input, textarea, select");
        inputs.forEach((input) => {
          input.disabled = false; // Active les champs
        });
      });
  
      
/* Script pour ma page my_pharmacy */