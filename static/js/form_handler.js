document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('requirementForm');
    
    if (form) {
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
            
            // Validate timeline format
            const timelineField = document.getElementById('preferred_timeline');
            const timelineValue = timelineField.value.trim().toLowerCase();
            const timelinePattern = /^\d+\s*(?:month|months|mo)$/;
            
            if (!timelinePattern.test(timelineValue)) {
                isValid = false;
                timelineField.classList.add('is-invalid');
                alert('Timeline must be specified in months (e.g., "3 months")');
            }
            
            if (isValid) {
                form.submit();
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
