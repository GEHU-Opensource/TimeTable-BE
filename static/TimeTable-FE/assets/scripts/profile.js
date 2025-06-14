document.addEventListener("DOMContentLoaded", () => {
    const departmentDropdown = document.getElementById("department");
    const profileForm = document.getElementById("profileForm");
    const subjectList = document.getElementById("subjectList");
    const editButton = document.getElementById("editBtn");
    const submitBtn = document.getElementById("submitBtn");
    const profileHead = document.getElementById("profileHeading");
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

                if (originalData.assigned_subjects.length === 0) {
                    document.querySelector(".inRequest").style.display = "block";
                }
                else {
                    document.querySelector(".inRequest").style.display = "none";
                }
                populateProfileForm(data);
                loadDepartments(data.department);
                updateSelectedSubjects();
                const teacherCode = data.teacher_code;
                profileHead.textContent = `Profile ( ${teacherCode} )`;
            })
            .catch(showError)
            .finally(() => {
                hideLoader();
            });
    }

    function populateProfileForm(data) {
        profileForm.elements["name"].value = data.name || "";
        profileForm.elements["phone"].value = data.phone || "";
        profileForm.elements["email"].value = data.email || "";
        profileForm.elements["designation"].value = data.designation || "";
        profileForm.elements["working_days"].value = data.working_days || "";
    }

    function toggleEditMode(enable) {
        const inputs = profileForm.querySelectorAll("input, select");
        inputs.forEach(input => {
            if (!["email", "name"].includes(input.id)) {
                input.disabled = !enable;
            }
        });
        submitBtn.disabled = !enable;
        editButton.querySelector("i").classList.toggle("fa-pencil", !enable);
        editButton.querySelector("i").classList.toggle("fa-times", enable);
    }

    editButton.addEventListener("click", () => {
        const isEditing = !profileForm.elements["department"].disabled;

        if (isEditing) {
            if (confirm("You have unsaved changes. Discard them?")) {
                populateProfileForm(originalData);
                loadDepartments(originalData.department);
                toggleEditMode(false);
            } else {
                toggleEditMode(false);
            }
        } else {
            toggleEditMode(true);
        }
    });

    profileForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const assignedSubjects = originalData.assigned_subjects;
        const updatedData = {
            id: originalData.id,
            teacher_code: originalData.teacher_code,
            teacher_type: originalData.teacher_type,
            name: profileForm.elements["name"].value,
            phone: profileForm.elements["phone"].value,
            email: profileForm.elements["email"].value,
            department: profileForm.elements["department"].value,
            designation: profileForm.elements["designation"].value,
            working_days: profileForm.elements["working_days"].value,
            assigned_subjects: assignedSubjects,
        };
        if (confirm("Are you sure to Submit these details?"))
            submitData(updatedData);
    });

    function submitData(updatedData) {
        showLoader();
        fetch(`${baseUrl}/updateTeacher/${originalData.id}/`, {
            method: "PUT",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(updatedData),
        })
            .then(handleResponse)
            .then(() => {
                alert("Profile updated successfully!");
                originalData = { ...updatedData };
                document.location.reload();
            })
            .catch(showError)
            .finally(() => {
                hideLoader();
            });
    }

    function loadDepartments(selectedDepartment) {
        departmentDropdown.innerHTML = "";
        if (Array.isArray(departments)) {
            departments.forEach(department => {
                const option = document.createElement("option");
                option.value = department.name;
                option.textContent = department.name;
                if (department.name === selectedDepartment) option.selected = true;
                departmentDropdown.appendChild(option);
            });
        }
    }

    function updateSelectedSubjects() {
        const assignedSubjects = originalData.assigned_subjects;
        subjectList.innerHTML = "";

        assignedSubjects.forEach((subjectObj) => {
            // Create container for each subject
            const subject_code = subjectObj.subject_code;
            const subject_name = subjectObj.subject_name;

            const subjectContainer = document.createElement("div");
            subjectContainer.classList.add("subject-card");

            // Create div for subject code
            const codeDiv = document.createElement("div");
            codeDiv.classList.add("subject-code");
            codeDiv.textContent = subject_code;

            // Create div for subject name
            const nameDiv = document.createElement("div");
            nameDiv.classList.add("subject-name");
            nameDiv.textContent = subject_name;

            // Append both divs to container
            subjectContainer.appendChild(codeDiv);
            subjectContainer.appendChild(nameDiv);

            // Append container to subject list
            subjectList.appendChild(subjectContainer);
        });
    }

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

    getTeachersData();
});