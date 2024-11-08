document.addEventListener('DOMContentLoaded', function() {
    // Get all forms that need handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form) {
            handleFormSubmission(form);
        }
    });
});

function handleFormSubmission(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;
    
    const spinner = submitBtn.querySelector('.spinner-border');
    const buttonText = submitBtn.querySelector('.button-text');
    
    form.addEventListener('submit', function(e) {
        // Basic validation
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                
                // Create or update feedback message
                let feedback = field.nextElementSibling;
                if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    field.parentNode.insertBefore(feedback, field.nextSibling);
                }
                feedback.textContent = 'This field is required';
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        // Password validation for reset credentials form
        if (form.id === 'resetCredentialsForm') {
            const newPassword = form.querySelector('#new_password');
            const confirmPassword = form.querySelector('#confirm_password');
            
            if (newPassword && confirmPassword) {
                // Check password length
                if (newPassword.value.length < 6) {
                    isValid = false;
                    newPassword.classList.add('is-invalid');
                    let feedback = newPassword.nextElementSibling;
                    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                        feedback = document.createElement('div');
                        feedback.className = 'invalid-feedback';
                        newPassword.parentNode.insertBefore(feedback, newPassword.nextSibling);
                    }
                    feedback.textContent = 'Password must be at least 6 characters long';
                }
                
                // Check if passwords match
                if (newPassword.value !== confirmPassword.value) {
                    isValid = false;
                    confirmPassword.classList.add('is-invalid');
                    let feedback = confirmPassword.nextElementSibling;
                    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                        feedback = document.createElement('div');
                        feedback.className = 'invalid-feedback';
                        confirmPassword.parentNode.insertBefore(feedback, confirmPassword.nextSibling);
                    }
                    feedback.textContent = 'Passwords do not match';
                }
            }
        }
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
        
        // Show loading state
        if (spinner) spinner.classList.remove('d-none');
        if (buttonText) buttonText.textContent = 'Processing...';
        if (submitBtn) submitBtn.disabled = true;
        
        return true;
    });
    
    // Remove invalid class on input
    form.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            const feedback = this.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.remove();
            }
            
            // Clear password match validation on input
            if (form.id === 'resetCredentialsForm' && 
                (this.id === 'new_password' || this.id === 'confirm_password')) {
                const confirmPassword = form.querySelector('#confirm_password');
                if (confirmPassword) {
                    confirmPassword.classList.remove('is-invalid');
                    const confirmFeedback = confirmPassword.nextElementSibling;
                    if (confirmFeedback && confirmFeedback.classList.contains('invalid-feedback')) {
                        confirmFeedback.remove();
                    }
                }
            }
        });
    });
}
