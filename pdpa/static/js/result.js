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
