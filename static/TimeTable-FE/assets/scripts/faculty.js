const departmentDropdown = document.getElementById("department");
const form = document.getElementById("facultyForm");
const searchInput = document.getElementById("searchSubjects");
const dropdownContent = document.querySelector(".dropdown-content");
const selectedSubjectsContainer = document.querySelector(".selected-subjects");
const subjectList = document.getElementById("subjectList");
const baseUrl = BE_URL;

document.addEventListener("DOMContentLoaded", () => {
    loadDepartments();
    loadSubjects();
    setupSearchInput();
    setupFormSubmission();
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
    loadComponent("footer", "../components/footer.html");
    setTimeout(highlightActiveLink, 1000);
});

function loadDepartments() {
    if (typeof departments !== "undefined") {
        departments.forEach((department) => {
            const option = document.createElement("option");
            option.value = department.name;
            option.textContent = department.name;
            departmentDropdown.appendChild(option);
        });
    } else {
        console.error("Departments data is not defined.");
    }
}

function loadSubjects() {
    dropdownContent.innerHTML = "";

    showLoader();
    fetch(`${baseUrl}/getAllSubjects/`, { method: "GET" })
        .then(handleResponse)
        .then((subjects) => {
            subjects.forEach((subject) => {
                const label = document.createElement("label");
                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.value = subject.subject_name;
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(` ${subject.subject_name} (${subject.subject_code})`));
                dropdownContent.appendChild(label);

                checkbox.addEventListener("change", updateSelectedSubjects);
            });
        })
        .catch(showError)
        .finally(() => {
            hideLoader();
        });
}

function handleResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
}

function showError(error) {
    console.error("Error: ", error);
    alert(error);
}

function updateSelectedSubjects() {
    const selectedSubjects = getSelectedSubjects();
    subjectList.innerHTML = "";
    if (selectedSubjects.length > 0) {
        selectedSubjects.forEach((subject) => {
            const subjectElement = document.createElement("span");
            subjectElement.textContent = subject;
            subjectList.appendChild(subjectElement);
        });
        selectedSubjectsContainer.style.display = "block";
    } else {
        selectedSubjectsContainer.style.display = "none";
    }
}

function getSelectedSubjects() {
    const selectedSubjects = [];
    const checkboxes = dropdownContent.querySelectorAll("input[type='checkbox']");
    checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
            selectedSubjects.push(checkbox.value);
        }
    });
    return selectedSubjects;
}

function setupSearchInput() {
    searchInput.addEventListener("input", function () {
        const searchValue = this.value.toLowerCase();
        const labels = dropdownContent.querySelectorAll("label");
        let hasVisibleOption = false;

        labels.forEach((label) => {
            const text = label.textContent.toLowerCase();
            label.style.display = text.includes(searchValue) ? "flex" : "none";
            if (text.includes(searchValue)) hasVisibleOption = true;
        });

        dropdownContent.style.display = hasVisibleOption ? "block" : "none";
    });

    searchInput.addEventListener("focus", function () {
        dropdownContent.style.display = "block";
    });

    document.addEventListener("click", function (event) {
        if (
            !searchInput.contains(event.target) &&
            !dropdownContent.contains(event.target)
        ) {
            dropdownContent.style.display = "none";
        }
    });
}

function setupFormSubmission() {
    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const selectedSubjects = getSelectedSubjects();
        if (selectedSubjects.length === 0) {
            alert("Please select at least one preferred subject.");
            return;
        }

        const formData = gatherFormData(selectedSubjects);

        submitFormData(formData);
    });
}

function gatherFormData(selectedSubjects) {
    const elements = form.elements;
    const data = {
        name: titleCase(elements["name"].value),
        phone: elements["phone"].value,
        email: elements["email"].value,
        department: elements["department"].value,
        designation: elements["designation"].value,
        working_days: elements["working_days"].value,
        preferred_subjects: selectedSubjects,
    };
    return data;
}

function titleCase(s) {
    return s.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

function submitFormData(data) {
    // Show loading indicator
    document.getElementById("loading-spinner").style.display = "block";

    showLoader();
    fetch(`${baseUrl}/addTeacher/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
        .then((response) => {
            if (!response.ok) {
                return response.json().then((errorData) => {
                    throw new Error(
                        errorData.error || `HTTP error! Status: ${response.status}`
                    );
                });
            }
            return response.json();
        })
        .then((responseData) => {
            // Hide the loading spinner
            document.getElementById("loading-spinner").style.display = "none";
            if (responseData.message) {
                alert(responseData.message);
            }
            form.reset();
            selectedSubjectsContainer.style.display = "none";
        })
        .catch((error) => {
            document.getElementById("loading-spinner").style.display = "none";
            if (error.message.includes("User with this email already exists.")) {
                alert("This teacher's email already exists. Please try again.");
            } else {
                alert("Failed to submit data. Please try again.");
            }
            console.error("Error posting data:", error);
        })
        .finally(() => {
            hideLoader();
        });
}