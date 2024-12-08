// Wait for the DOM to fully load before executing the code
document.addEventListener("DOMContentLoaded", function() {

    // Toggle mobile navigation menu visibility
    const menuButton = document.getElementById('menu-button');
    const navMenu = document.getElementById('nav-menu');

    if (menuButton && navMenu) {
        menuButton.addEventListener('click', function() {
            navMenu.classList.toggle('visible');
        });
    }

    // Form validation for contact form (or any form)
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            let isValid = true;
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const message = document.getElementById('message');

            // Basic form validation
            if (name.value === '') {
                alert('Name is required.');
                isValid = false;
            }
            if (email.value === '') {
                alert('Email is required.');
                isValid = false;
            }
            if (message.value === '') {
                alert('Message is required.');
                isValid = false;
            }

            if (!isValid) {
                event.preventDefault(); // Prevent form submission if validation fails
            }
        });
    }

    // Handle button click (Example: alert when a button is clicked)
    const alertButton = document.getElementById('alert-button');
    if (alertButton) {
        alertButton.addEventListener('click', function() {
            alert('Button clicked!');
        });
    }

    // Scroll to top of the page button
    const scrollToTopButton = document.getElementById('scroll-to-top');
    if (scrollToTopButton) {
        scrollToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth' // Smooth scroll to top
            });
        });
    }

});

// Toggle menu for mobile view (Example)
const style = document.createElement('style');
style.innerHTML = `
    #nav-menu.visible {
        display: block;
    }
`;
document.head.appendChild(style);
