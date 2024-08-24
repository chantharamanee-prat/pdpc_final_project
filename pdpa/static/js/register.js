function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const checkbox = document.querySelector(`input[onclick="togglePassword('${fieldId}')"]`);

    if (checkbox.checked) {
        passwordField.type = 'text';
    } else {
        passwordField.type = 'password';
    }
}

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Form validation
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const webUrl = document.getElementById('web-url').value;
    const webUsername = document.getElementById('web-username').value;
    const webPassword = document.getElementById('web-password').value;

    if (username && password && webUrl && webUsername && webPassword) {
        alert('Registration successful!');
        // Additional logic for form submission can be added here
    } else {
        alert('Please fill out all fields.');
    }
});
