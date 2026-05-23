async function register() {

    const username = document.getElementById(
        "register-username"
    ).value;

    const email = document.getElementById(
        "register-email"
    ).value;

    const password = document.getElementById(
        "register-password"
    ).value;

    const resultDiv = document.getElementById(
        "register-result"
    );

    try {

        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const data = await response.json();

        resultDiv.innerText = data.message;

    } catch (error) {

        resultDiv.innerText = "请求失败";

    }
}

async function login() {

    const email = document.getElementById(
        "login-email"
    ).value;

    const password = document.getElementById(
        "login-password"
    ).value;

    const resultDiv = document.getElementById(
        "login-result"
    );

    try {

        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                password
            })
        });

        const data = await response.json();

        if (data.success) {

            localStorage.setItem(
                "token",
                data.token
            );

            resultDiv.innerText = "登录成功";

        } else {

            resultDiv.innerText = data.message;

        }

    } catch (error) {

        resultDiv.innerText = "请求失败";

    }
}