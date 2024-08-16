document.querySelectorAll('.show-more').forEach(button => {
    button.addEventListener('click', function(event) {
        const detailSection = button.nextElementSibling;
        if (button.textContent === 'Show More') {
            button.textContent = 'Show Less';
            detailSection.style.display = 'block';
        } else {
            button.textContent = 'Show More';
            detailSection.style.display = 'none';
        }
    });
});

document.querySelectorAll('.work-in-progress a').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const detailSection = link.parentElement.nextElementSibling;
        if (link.textContent === 'Show Details') {
            link.textContent = 'Hide Details';
            detailSection.style.display = 'block';
        } else {
            link.textContent = 'Show Details';
            detailSection.style.display = 'none';
        }
    });
});
