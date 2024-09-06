function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const checkbox = document.querySelector(`input[onclick="togglePassword('${fieldId}')"]`);

    if (checkbox.checked) {
        passwordField.type = 'text';
    } else {
        passwordField.type = 'password';
    }
}


document.getElementById("username").addEventListener("focus", () => {
    document.getElementById("usernameValidator").innerHTML = ""

});
