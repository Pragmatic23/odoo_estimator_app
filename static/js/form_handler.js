document.addEventListener('DOMContentLoaded', function() {
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
    
    // Handle login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        handleFormSubmission(loginForm);
    }
    
    // Handle admin reset credentials form submission
    const resetCredentialsForm = document.getElementById('resetCredentialsForm');
    if (resetCredentialsForm) {
        handleFormSubmission(resetCredentialsForm);
    }
});

function handleFormSubmission(form) {
    if (!form) return;

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
                if (spinner) spinner.classList.remove('d-none');
                if (buttonText) buttonText.textContent = 'Processing...';
                if (submitBtn) submitBtn.disabled = true;
                
                // Submit the form
                form.submit();
            } catch (error) {
                console.error('Error submitting form:', error);
                // Re-enable the button if there's an error
                if (spinner) spinner.classList.add('d-none');
                if (buttonText) buttonText.textContent = form.id === 'loginForm' ? 'Login' : 'Submit';
                if (submitBtn) submitBtn.disabled = false;
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
