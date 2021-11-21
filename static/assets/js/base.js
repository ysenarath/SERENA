document.addEventListener('keypress', (e) => {
    document.getElementById('userInput').focus();
});

up.compiler('.navbar-burger', (element) => {
    element.addEventListener('click', () => {
        // Get the target from the "data-target" attribute
        const target = element.dataset.target;
        const $target = document.getElementById(target);
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        element.classList.toggle('is-active');
        $target.classList.toggle('is-active');
    });
});

up.compiler('a#open-modal', (element) => {
    element.addEventListener('click', function (event) {
        event.preventDefault();
        let modal = document.querySelector('.modal');  // assuming you have only 1
        let html = document.querySelector('html');
        modal.classList.add('is-active');
        html.classList.add('is-clipped');
        modal.querySelector('.modal-background').addEventListener('click', function (e) {
            e.preventDefault();
            modal.classList.remove('is-active');
            html.classList.remove('is-clipped');
        });
        modal.querySelector('.modal-close').addEventListener('click', function (e) {
            e.preventDefault();
            modal.classList.remove('is-active');
            html.classList.remove('is-clipped');
        });
    });
});
