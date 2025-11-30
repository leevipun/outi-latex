(function () {
    let lastScrollY = window.scrollY;
    const navbar = document.querySelector('.navbar');

    if (!navbar) return;

    window.addEventListener(
        'scroll',
        function () {
            const currentY = window.scrollY;
            const delta = currentY - lastScrollY;

            // If scrolling down past 80px hide navbar
            if (currentY > 80 && delta > 0) {
                navbar.classList.add('navbar--hidden');
            } else {
                // Scrolling up or near top -> show navbar
                navbar.classList.remove('navbar--hidden');
            }

            lastScrollY = currentY;
        },
        { passive: true }
    );
})();
