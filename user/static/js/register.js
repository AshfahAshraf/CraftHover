const container = document.querySelector(".container");
const registerBtn = document.querySelector(".register-btn");
const loginBtn = document.querySelector(".login-btn");

registerBtn.addEventListener('click', () => {
    container.classList.add('active');

})

loginBtn.addEventListener("click", () => {
    container.classList.remove("active")
})

function validateForm() {
    let email = document.getElementById("email_or_phone");
    let password = document.getElementById("password");
    let confirmPassword = document.getElementById("confirmPassword");
    let valid = true;

    //reset previous errors
    document.getElementById("userError").innerText = "";
    document.getElementById("passwordError").innerText = "";
    document.getElementById("confirmError").innerText = "";


    email.classList.remove("error");
    password.classList.remove("error");
    confirmPassword.classList.remove("error")


    //emai or phone validation

    if (email.value.trim() === "") {
        document.getElementById("userError").innerText = "Email or Phone is required"
        email.classList.add("error")
        valid = false;
    }


    //password validation

    if (password.value.trim() === "") {
        document.getElementById("passwordError").innerText = "Password is required"
        password.classList.add("error")
        valid = false;
    }

    //confrim password validatioin

    if (confirmPassword.value.trim() === "") {
        document.getElementById("confirmError").innerText = "confirm password is required"
        confirmPassword.classList.add("error")
        valid = false
    }
    else if (password.value !== confirmPassword.value) {
        document.getElementById("confirmError").innerText = "password do not match";
        valid = false
    }

    return valid;  //if false ,form will not submit
}


