document.addEventListener('DOMContentLoaded', function() {
    const analyzeForm = document.getElementById('analyzeForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Clear previous errors
            errorMessage.classList.add('d-none');
            errorMessage.textContent = '';
            
            // Show loading spinner
            loadingSpinner.classList.remove('d-none');
            analyzeBtn.disabled = true;
            
            // Create form data
            const formData = new FormData(analyzeForm);
            
            // Send request to analyze endpoint
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                loadingSpinner.classList.add('d-none');
                analyzeBtn.disabled = false;
                
                if (data.error) {
                    // Show error message
                    errorMessage.textContent = data.error;
                    errorMessage.classList.remove('d-none');
                } else {
                    // Redirect to results page
                    window.location.href = '/results';
                }
            })
            .catch(error => {
                // Hide loading spinner
                loadingSpinner.classList.add('d-none');
                analyzeBtn.disabled = false;
                
                // Show error message
                errorMessage.textContent = 'An error occurred. Please try again.';
                errorMessage.classList.remove('d-none');
                console.error('Error:', error);
            });
        });
    }
});