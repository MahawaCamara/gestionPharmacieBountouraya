// Script pour la page login

//Script pour effacer les messages de succès apres 5 seconde 
        setTimeout(() => {
          const messages = document.getElementById("messages");
          if (messages) {
            messages.style.display = "none";
          }
        }, 5000); // disparaît après 5 secondes
   