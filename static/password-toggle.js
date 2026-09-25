document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("password");
    const showPassword = document.getElementById("show-password");

    if (!passwordInput || !showPassword) {
        return;
    }

    showPassword.addEventListener("change", () => {
        passwordInput.type = showPassword.checked
            ? "text"
            : "password";
    });
});
