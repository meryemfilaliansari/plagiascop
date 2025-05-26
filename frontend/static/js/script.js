document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Gestion de l'aperçu du texte
    const textInput = document.getElementById('text');
    const fileInput = document.getElementById('file');
    const textPreview = document.getElementById('textPreview');
    
    if (textInput && textPreview) {
        textInput.addEventListener('input', function() {
            updateTextPreview(this.value);
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                if (file.type === 'text/plain') {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        updateTextPreview(e.target.result);
                    };
                    reader.readAsText(file);
                } else if (file.type === 'application/pdf') {
                    // Pour PDF, nous affichons juste le nom du fichier
                    updateTextPreview(`Fichier PDF sélectionné: ${file.name}`);
                }
            }
        });
    }
    
    function updateTextPreview(text) {
        if (textPreview) {
            textPreview.textContent = text || 'Aucun texte saisi';
            if (text.length > 1000) {
                textPreview.textContent = text.substring(0, 1000) + '... [texte tronqué]';
            }
        }
    }
    
    // Animation des résultats
    const resultsCards = document.querySelectorAll('.animate-results');
    resultsCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Gestion de l'affichage des sections correspondantes
    document.querySelectorAll('.show-matches-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.classList.toggle('d-none');
                this.textContent = targetElement.classList.contains('d-none') ? 
                    'Afficher les correspondances' : 'Masquer les correspondances';
            }
        });
    });
});

// Fonction pour surligner le texte
function highlightText(sourceText, matchedSections) {
    let highlightedText = sourceText;
    
    matchedSections.forEach(section => {
        const escapedText = section.source_sentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        highlightedText = highlightedText.replace(
            new RegExp(escapedText, 'gi'),
            `<span class="highlight">${section.source_sentence}</span>`
        );
    });
    
    return highlightedText;
}