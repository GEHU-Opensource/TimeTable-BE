const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const errorMessage = document.getElementById("error-message");
const expirationTime = Date.now() + 2 * 60 * 60 * 1000;
const apiUrl = BE_URL;

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value.trim();
    if (!email || !password) {
        alert("Please enter both email and password.");
        return;
    }

    showLoader();
    try {
        const response = await fetch(`${apiUrl}/login/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
            localStorage.setItem("sessionExpiresAt", expirationTime);
            if (data.teacher.teacher_type === "faculty") {
                window.location.href = "/faculty/timetable.html";
            } else if (data.teacher.teacher_type === "hod") {
                window.location.href = "/hod/timetable.html";
            } else {
                window.location.href = "/admin/subject.html";
            }
        } else {
            alert(data.detail || "Invalid credentials. Please try again.");
            errorMessage.textContent = data.detail || "Invalid credentials.";
        }
    } catch (error) {
        console.error("Error:", error);
        alert(
            "An error occurred while processing your request. Please try again later."
        );
        errorMessage.innerHTML = "An error occurred. Please try again later.";
    }
    finally {
        hideLoader();
    }
});

function togglePassword() {
    var showPass = document.getElementById("password");
    if (showPass.type === "password") {
        showPass.type = "text";
    }
    else {
        showPass.type = "password";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    localStorage.clear();
    function loadComponent(id, file) {
        showLoader();
        fetch(file)
            .then(response => response.text())
            .then(data => {
                document.getElementById(id).innerHTML = data;
            })
            .finally(() => {
                hideLoader();
            });
    }

    function highlightActiveLink() {
        document.getElementById("current-year").textContent = new Date().getFullYear();
        const footer = document.querySelector("footer");
        function checkScrollbar() {
            if (document.body.scrollHeight <= window.innerHeight) {
                footer.classList.add("fixed");
            } else {
                footer.classList.remove("fixed");
            }
        }
        checkScrollbar();
        window.addEventListener("resize", checkScrollbar);
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll("nav ul li a");
        navLinks.forEach(link => {
            if (currentPath.endsWith(link.getAttribute("href"))) {
                link.classList.add("active");
            }
        });
    }

    loadComponent("footer", "../components/footer.html");
    setTimeout(highlightActiveLink, 1000);
});