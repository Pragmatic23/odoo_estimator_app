document.addEventListener('DOMContentLoaded', function() {
    // Handle requirement form submission
    const requirementForm = document.getElementById('requirementForm');
    if (requirementForm) {
        handleFormSubmission(requirementForm);
    }
    
    // Handle admin reset credentials form submission
    const resetForm = document.getElementById('resetCredentialsForm');
    if (resetForm) {
        handleFormSubmission(resetForm);
    }
});

function handleFormSubmission(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;
    
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
        
        if (isValid) {
            try {
                // Show loading state if elements exist
                if (spinner) spinner.classList.remove('d-none');
                if (buttonText) buttonText.textContent = 'Submitting...';
                if (submitBtn) submitBtn.disabled = true;
                
                // Submit the form after a short delay to ensure UI updates
                setTimeout(() => {
                    form.submit();
                }, 100);
            } catch (error) {
                console.error('Error updating button state:', error);
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
