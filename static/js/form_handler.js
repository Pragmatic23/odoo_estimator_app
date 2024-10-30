document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('requirementForm');
    const submitBtn = document.getElementById('submitBtn');
    
    if (form && submitBtn) {
        const spinner = submitBtn.querySelector('.spinner-border');
        const buttonText = submitBtn.querySelector('.button-text');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic client-side validation
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (isValid && spinner && buttonText) {
                // Show loading state
                spinner.classList.remove('d-none');
                buttonText.textContent = 'Submitting...';
                submitBtn.disabled = true;
                
                // Submit the form
                form.submit();
            } else if (!isValid) {
                alert('Please fill in all required fields correctly');
            }
        });
        
        // Remove invalid class on input
        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    }
});
