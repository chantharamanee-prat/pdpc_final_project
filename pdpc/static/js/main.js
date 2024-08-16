document.querySelector('.select-all').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('.category-card');
    checkboxes.forEach(box => box.classList.add('selected'));
});
