// Wait for DOM to load before running JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Welcome Button
    const welcomeButton = document.getElementById('welcomeButton');
    if (welcomeButton) {
        welcomeButton.addEventListener('click', () => {
            alert('Welcome to the Silent Library!');
        });
    }

    // Set Active Link in Navbar
    const links = document.querySelectorAll('.navbar a');
    links.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add('active');
        }
    });

    // Add more interactivity here as needed
});
