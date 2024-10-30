document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('requirementForm');
    
    if (form) {
        // Prevent form submission if validation fails
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
            
            // Additional custom validation
            const projectScope = document.getElementById('project_scope');
            const functionalReqs = document.getElementById('functional_requirements');
            const modulesInvolved = document.getElementById('modules_involved');
            
            if (projectScope.value.trim().length < 10) {
                projectScope.setCustomValidity('Project scope must be at least 10 characters long.');
                event.preventDefault();
            } else {
                projectScope.setCustomValidity('');
            }
            
            if (functionalReqs.value.trim().length < 20) {
                functionalReqs.setCustomValidity('Functional requirements must be at least 20 characters long.');
                event.preventDefault();
            } else {
                functionalReqs.setCustomValidity('');
            }
            
            const modulesList = modulesInvolved.value.trim().split(',').map(m => m.trim()).filter(m => m);
            if (modulesList.length === 0) {
                modulesInvolved.setCustomValidity('Please specify at least one module.');
                event.preventDefault();
            } else {
                modulesInvolved.setCustomValidity('');
            }
        });
        
        // Clear custom validity on input
        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('input', function() {
                this.setCustomValidity('');
            });
        });
    }
});
