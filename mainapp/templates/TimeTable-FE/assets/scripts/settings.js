document.addEventListener("DOMContentLoaded", () => {
    const baseUrl = BE_URL;
    let originalData = {};
    const token = localStorage.getItem("access_token");

    function loadComponent(id, file) {
        showLoader();
        fetch(file)
            .then(response => response.text())
            .then(data => {
                document.getElementById(id).innerHTML = data;
                attachNavbarEventListeners();
            })
            .finally(() => {
                hideLoader();
            });
    }

    function attachNavbarEventListeners() {
        const logoutBtn = document.getElementById("logoutBtn");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", () => {
                localStorage.clear();
                window.location.href = "../index.html";
            });
        }
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

    document.getElementById("show-password").addEventListener("click", function () {
        var passwordFields = document.querySelectorAll(".password");
        passwordFields.forEach(function (field) {
            if (field.type === "password") {
                field.type = "text";
            }
            else {
                field.type = "password";
            }
        });
    });

    document.getElementById("update-form").addEventListener("submit", (event) => {
        event.preventDefault();
        const oldPasswordInput = document.getElementById("oldPass");
        const newPasswordInput = document.getElementById("newPass");
        const confirmPasswordInput = document.getElementById("confirmPass");
        const data = {
            old_password: oldPasswordInput.value.trim(),
            new_password: newPasswordInput.value.trim(),
            confirm_password: confirmPasswordInput.value.trim(),
        }
        
        showLoader();
        fetch(`${baseUrl}/updatePassword/`, {
            method: "PUT",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then(handleResponse)
            .then((response) => {
                alert(response.message);
                document.location.reload();
            })
            .catch(showError)
            .finally(() => {
                hideLoader();
            });
    });

    function handleResponse(response) {
        return response.json().then((data) => {
            if (!response.ok) {
                throw new Error(data.error || data.message || `HTTP error! Status: ${response.status}`);
            }
            return data;
        });
    }

    function showError(error) {
        console.error("Error: ", error);
        const errorMessage = error.message || "An error occurred.";

        if (errorMessage.includes("401")) {
            alert("Session expired. Redirecting to login...");
            window.location.href = "../index.html";
        } else {
            alert(errorMessage);
        }
    }

    function getTeachersData() {
        showLoader();
        fetch(`${baseUrl}/getSpecificTeacher/`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        })
            .then(handleResponse)
            .then(data => {
                originalData = { ...data };
                if (originalData.teacher_type === "hod") {
                    loadComponent("navbar-hod", "../components/hod_navbar.html");
                }
                else {
                    loadComponent("navbar-faculty", "../components/faculty_navbar.html");
                }
                loadComponent("footer", "../components/footer.html");
                setTimeout(highlightActiveLink, 1000);
            })
            .catch(showError)
            .finally(() => {
                hideLoader();
            });
    }

    getTeachersData();
});