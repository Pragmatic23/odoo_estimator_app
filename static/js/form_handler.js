document.addEventListener('DOMContentLoaded', function() {
    // Handle login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const spinner = submitBtn?.querySelector('.spinner-border');
            const buttonText = submitBtn?.querySelector('.button-text');
            
            // Show loading state
            if (spinner) spinner.classList.remove('d-none');
            if (buttonText) buttonText.textContent = 'Processing...';
            if (submitBtn) submitBtn.disabled = true;
            
            // Submit form
            this.submit();
        });
    }
    
    // Handle requirement form submission
    const requirementForm = document.getElementById('requirementForm');
    if (requirementForm) {
        handleFormSubmission(requirementForm);
    }
    
    // Handle registration form submission
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        handleFormSubmission(registrationForm);
    }
    
    // Handle admin reset credentials form submission
    const resetCredentialsForm = document.getElementById('resetCredentialsForm');
    if (resetCredentialsForm) {
        handleFormSubmission(resetCredentialsForm);
    }
});

function handleFormSubmission(form) {
    if (!form || form.id === 'loginForm') return; // Skip login form as it's handled separately

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
        
        // Password matching validation for reset credentials form
        if (form.id === 'resetCredentialsForm') {
            const newPassword = form.querySelector('#new_password');
            const confirmPassword = form.querySelector('#confirm_password');
            if (newPassword && confirmPassword && newPassword.value !== confirmPassword.value) {
                isValid = false;
                confirmPassword.classList.add('is-invalid');
                alert('New passwords do not match');
                return;
            }
        }
        
        if (isValid) {
            try {
                // Show loading state if elements exist
                if (spinner) spinner.classList.remove('d-none');
                if (buttonText) buttonText.textContent = 'Processing...';
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
            
            // Clear password match validation on input
            if (form.id === 'resetCredentialsForm' && 
                (this.id === 'new_password' || this.id === 'confirm_password')) {
                const confirmPassword = form.querySelector('#confirm_password');
                if (confirmPassword) {
                    confirmPassword.classList.remove('is-invalid');
                }
            }
        });
    });
}
