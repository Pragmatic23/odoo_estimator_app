document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('requirementForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get button elements after form submission is triggered
            const submitBtn = document.getElementById('submitBtn');
            const spinner = submitBtn.querySelector('.spinner-border');
            const buttonText = submitBtn.querySelector('.button-text');
            
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
            
            if (isValid) {
                try {
                    // Show loading state
                    spinner.classList.remove('d-none');
                    buttonText.textContent = 'Submitting...';
                    submitBtn.disabled = true;
                    
                    // Submit the form after a short delay to ensure UI updates
                    setTimeout(() => {
                        form.submit();
                    }, 100);
                } catch (error) {
                    console.error('Error updating button state:', error);
                    // Submit form anyway if UI update fails
                    form.submit();
                }
            } else {
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
