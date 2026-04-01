const container = document.querySelector(".container");
const registerBtn = document.querySelector(".register-btn");
const loginBtn = document.querySelector(".login-btn");

const registerForm = document.querySelector(".register form");

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
});

loginBtn.addEventListener("click", () => {
    container.classList.remove("active");
});

if (registerForm) {
    registerForm.addEventListener("submit", function (e) {

        let passwordInput = registerForm.querySelector("#registerPassword");
        let confirmInput = registerForm.querySelector("#registerConfirmPassword");

        let password = passwordInput.value;
        let confirmPassword = confirmInput.value;

        let passwordError = document.getElementById("passwordError");
        let confirmError = document.getElementById("confirmError");

        if (passwordError) passwordError.innerText = "";
        if (confirmError) confirmError.innerText = "";

        passwordInput.classList.remove("error");
        confirmInput.classList.remove("error");

        let isValid = true;

        if (password.length < 6) {
            if (passwordError) passwordError.innerText = "Password must be at least 6 characters";
            passwordInput.classList.add("error");
            isValid = false;
        }

        if (password !== confirmPassword) {
            if (confirmError) confirmError.innerText = "Passwords do not match";
            confirmInput.classList.add("error");
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        }
    });
}