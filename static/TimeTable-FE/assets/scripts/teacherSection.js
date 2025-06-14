document.addEventListener("DOMContentLoaded", () => {
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

const baseUrl = BE_URL;
const courseDropdown = document.getElementById("course");
const branchDropdown = document.getElementById("branch");
const yearDropdown = document.getElementById("year");
const semesterDropdown = document.getElementById("semester");
const submitBtn = document.getElementById("submitBtn");
let department;

async function getTeachersData() {
    showLoader();
    try {
        const response = await fetch(`${baseUrl}/getSpecificTeacher/`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        });
        const data = await handleResponse(response);
        console.log(data);
        let department = data.department;

        if (!departments.length) {
            console.error("Departments data is missing.");
            return;
        }

        const selectedDepartment = departments.find(dep => dep.name === department);
        if (!selectedDepartment) {
            console.error("Selected department not found in departments.");
            return;
        }

        clearDropdown(courseDropdown);
        populateDropdown(courseDropdown, selectedDepartment.courses || [], "name", "name");
    } catch (error) {
        showError(error);
    } finally {
        hideLoader();
    }
}

function clearDropdown(dropdown) {
    dropdown.innerHTML = "";
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select an option";
    dropdown.appendChild(defaultOption);
}

function populateDropdown(dropdown, options, valueKey, textKey) {
    options.forEach((option) => {
        const opt = document.createElement("option");
        opt.value = option[valueKey];
        opt.textContent = option[textKey];
        dropdown.appendChild(opt);
    });
}

courseDropdown.addEventListener("change", function () {
    if (!department) {
        console.error("Department is undefined.");
        return;
    }

    const selectedDepartment = departments.find(dep => dep.name === department);
    if (!selectedDepartment) return;

    const selectedCourse = selectedDepartment.courses.find(course => course.name === courseDropdown.value);
    clearDropdown(branchDropdown);
    populateDropdown(branchDropdown, selectedCourse?.branches || [], "name", "name");
});

branchDropdown.addEventListener("change", function () {
    if (!department) {
        console.error("Department is undefined.");
        return;
    }

    const selectedDepartment = departments.find(dep => dep.name === department);
    const selectedCourse = selectedDepartment?.courses.find(course => course.name === courseDropdown.value);
    const selectedBranch = selectedCourse?.branches.find(branch => branch.name === branchDropdown.value);

    clearDropdown(yearDropdown);
    populateDropdown(yearDropdown, selectedBranch?.years || [], "year", "year");
});

yearDropdown.addEventListener("change", function () {
    if (!department) {
        console.error("Department is undefined.");
        return;
    }

    const selectedDepartment = departments.find(dep => dep.name === department);
    const selectedCourse = selectedDepartment?.courses.find(course => course.name === courseDropdown.value);
    const selectedBranch = selectedCourse?.branches.find(branch => branch.name === branchDropdown.value);
    const selectedYear = selectedBranch?.years.find(year => year.year == yearDropdown.value);

    clearDropdown(semesterDropdown);
    populateDropdown(semesterDropdown, selectedYear?.semesters || [], "sem", "sem");
});

async function handleResponse(response) {
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || data.message || `HTTP error! Status: ${response.status}`);
    }
    return data;
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