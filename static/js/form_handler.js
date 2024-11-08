document.addEventListener('DOMContentLoaded', function() {
    // Handle all form submissions
    const forms = {
        requirementForm: document.getElementById('requirementForm'),
        registrationForm: document.getElementById('registrationForm'),
        loginForm: document.getElementById('loginForm'),
        resetCredentialsForm: document.getElementById('resetCredentialsForm')
    };
    
    Object.values(forms).forEach(form => {
        if (form) {
            handleFormSubmission(form);
        }
    });
});

function handleFormSubmission(form) {
    if (!form) return;

    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;
    
    const spinner = submitBtn.querySelector('.spinner-border');
    const buttonText = submitBtn.querySelector('.button-text');
    
    form.addEventListener('submit', function(e) {
        // Only prevent default if we need to do custom handling
        if (form.id === 'requirementForm') {
            e.preventDefault();
        }
        
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
            if (spinner) spinner.classList.remove('d-none');
            if (buttonText) buttonText.textContent = 'Processing...';
            if (submitBtn) submitBtn.disabled = true;
            
            // Allow normal form submission for login and registration
            if (form.id !== 'requirementForm') {
                return true;
            }
            
            // Custom handling for requirement form
            try {
                form.submit();
            } catch (error) {
                console.error('Error submitting form:', error);
                if (spinner) spinner.classList.add('d-none');
                if (buttonText) buttonText.textContent = 'Submit';
                if (submitBtn) submitBtn.disabled = false;
            }
        } else {
            if (form.id === 'requirementForm') {
                e.preventDefault();
            }
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
