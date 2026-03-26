function sendOTP() {

    let email = document.querySelector('[name="email"]').value;

    if (email === "") {
        alert("Enter email first");
        return;
    }

    // show OTP box
    document.getElementById("otpBox").style.display = "block";

    // move to step 2
    document.getElementById("step1").style.display = "none";
    document.getElementById("step2").style.display = "block";

    document.getElementById("stepIndicator2").classList.remove("bg-secondary");
    document.getElementById("stepIndicator2").classList.add("bg-primary");

    // copy email
    document.getElementById("emailStep2").value = email;

    // submit form manually
    let form = document.querySelector("form");

    let hidden = document.createElement("input");
    hidden.type = "hidden";
    hidden.name = "send_otp";
    hidden.value = "1";

    form.appendChild(hidden);

    form.submit();
}