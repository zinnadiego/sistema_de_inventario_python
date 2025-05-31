// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effect to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.transition = 'transform 0.3s ease';
        });
    });

    // Add tooltips to icons
    const icons = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    icons.forEach(icon => {
        new bootstrap.Tooltip(icon);
    });

    // Add animation to numbers in stats cards
    const numbers = document.querySelectorAll('.display-6');
    numbers.forEach(number => {
        const finalValue = parseInt(number.textContent);
        let currentValue = 0;
        const duration = 1000; // 1 second
        const increment = finalValue / (duration / 16); // 60 FPS

        const animate = () => {
            currentValue = Math.min(currentValue + increment, finalValue);
            number.textContent = Math.floor(currentValue);
            
            if (currentValue < finalValue) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    });

    // Add fade-in effect to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
    });
}); 