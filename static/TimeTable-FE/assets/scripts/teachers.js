document.addEventListener("DOMContentLoaded", () => {
    function loadComponent(id, file) {
        showLoader();
        fetch(file)
            .then((response) => response.text())
            .then((data) => {
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
        document.getElementById("current-year").textContent =
            new Date().getFullYear();
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

        navLinks.forEach((link) => {
            if (currentPath.endsWith(link.getAttribute("href"))) {
                link.classList.add("active");
            }
        });
    }

    loadComponent("navbar-admin", "../components/admin_navbar.html");
    loadComponent("footer", "../components/footer.html");
    setTimeout(highlightActiveLink, 1000);
    init();
});

const teachersTableBody = document.getElementById("teachersTableBody");
const teacherSearch = document.getElementById("teacherSearch");
const noTeachersMessage = document.getElementById("noTeachersMessage");
const teacherDetailsModal = document.getElementById("teacherDetailsModal");
const teacherDetailsContent = document.getElementById("teacherDetailsContent");
const teacherTypeSelect = document.getElementById("teacherTypeSelect");
const saveTypeBtn = document.getElementById("saveTypeBtn");
const cancelEditBtn = document.getElementById("cancelEditBtn");
const closeModal = document.querySelector(".close");

const baseUrl = BE_URL;
const token = localStorage.getItem("access_token");
let currentTeacher = null;
let allTeachers = [];

function init() {
    loadTeachers();
    setupEventListeners();
}

function loadTeachers() {
    teachersTableBody.innerHTML = '<tr><td colspan="7">Loading teachers...</td></tr>';

    showLoader();
    fetch(`${baseUrl}/getAllTeachers/`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            allTeachers = sortTeachers(data);
            renderTeachersTable(allTeachers);
            noTeachersMessage.style.display =
                allTeachers.length === 0 ? "block" : "none";
        })
        .catch((error) => {
            showError(error);
            teachersTableBody.innerHTML =
                '<tr><td colspan="7">Error loading teachers</td></tr>';
        })
        .finally(() => {
            hideLoader();
        });
}

function sortTeachers(teachers) {
    const admins = [];
    const departmentsMap = {};

    // Separate admins and group others by department
    teachers.forEach((teacher) => {
        if (teacher.teacher_type === "admin") {
            admins.push(teacher);
        } else {
            if (!departmentsMap[teacher.department]) {
                departmentsMap[teacher.department] = [];
            }
            departmentsMap[teacher.department].push(teacher);
        }
    });

    // Sort admins alphabetically by name
    admins.sort((a, b) => a.name.localeCompare(b.name));

    // Process each department
    const sortedDepartments = Object.keys(departmentsMap).sort(); // sort department names alphabetically
    const result = [...admins];

    sortedDepartments.forEach((dept) => {
        const deptTeachers = departmentsMap[dept];
        // Separate HOD and faculty
        const hod = deptTeachers.find((t) => t.teacher_type === "hod");
        const faculty = deptTeachers
            .filter((t) => t.teacher_type !== "hod")
            .sort((a, b) => a.name.localeCompare(b.name));
        if (hod) result.push(hod);
        result.push(...faculty);
    });

    return result;
}

function showError(error) {
    console.error("Error: ", error);
    alert(error.message || "An error occurred.");
}

function renderTeachersTable(teachers) {
    teachersTableBody.innerHTML = "";

    teachers.forEach((teacher, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${teacher.teacher_code || "N/A"}</td>
            <td>${teacher.name || "Admin"}</td>
            <td>${teacher.department || "N/A"}</td>
            <td>${teacher.designation || "N/A"}</td>
            <td>${teacher.teacher_type || "N/A"}</td>
            <td>
                <button class="edit-btn" data-id="${teacher.teacher_code
            }"><i class="fas fa-edit"></i></button>
                <button class="delete-btn" data-id="${teacher.teacher_code
            }"><i class="fas fa-trash-alt"></i></button>
            </td>
        `;
        teachersTableBody.appendChild(row);
    });

    document
        .querySelectorAll(".edit-btn")
        .forEach((btn) => btn.addEventListener("click", handleEditTeacher));
    document
        .querySelectorAll(".delete-btn")
        .forEach((btn) => btn.addEventListener("click", handleDeleteTeacher));
}

function filterTeachers() {
    const searchTerm = teacherSearch.value.toLowerCase();
    const filteredTeachers = allTeachers.filter((teacher) =>
        Object.values(teacher).some(
            (val) => val && val.toString().toLowerCase().includes(searchTerm)
        )
    );
    renderTeachersTable(filteredTeachers);
}

function handleEditTeacher(e) {
    const teacherCode = e.target.closest("button").getAttribute("data-id");
    // Simulating API call by fetching from the sample data
    const teacher = allTeachers.find((t) => t.teacher_code === teacherCode);
    if (teacher) {
        currentTeacher = teacher;
        showTeacherDetails(teacher);
    } else {
        showError({ message: "Teacher not found!" });
    }
}

function showTeacherDetails(teacher) {
    teacherDetailsContent.innerHTML = `
        <div><strong>Teacher Code:</strong> ${teacher.teacher_code || "N/A"
        }</div>
        <div><strong>Name:</strong> ${teacher.name || "N/A"}</div>
        <div><strong>Department:</strong> ${teacher.department || "N/A"}</div>
        <div><strong>Designation:</strong> ${teacher.designation || "N/A"}</div>
        <div><strong>Phone:</strong> ${teacher.phone || "N/A"}</div>
        <div><strong>Email:</strong> ${teacher.email || "N/A"}</div>
        <div><strong>Working Days:</strong> ${teacher.working_days || "N/A"
        }</div>
        <div><strong>Workload:</strong> ${teacher.weekly_workload ? teacher.weekly_workload + " hours" : "N/A"
        }</div>
        <div><strong>Type:</strong> ${teacher.teacher_type || "N/A"}</div>
    `;
    document.getElementById("teacherTypeSelect").value = teacher.teacher_type;
    teacherDetailsModal.style.display = "block";
}

function handleDeleteTeacher(e) {
    const teacherCode = e.target.closest("button").getAttribute("data-id");
    const teacher = allTeachers.find((t) => t.teacher_code === teacherCode);

    if (!teacher) {
        showError({ message: "Teacher not found!" });
        return;
    }

    if (confirm("Are you sure you want to delete this teacher?")) {
        showLoader();
        fetch(`${baseUrl}/deleteTeacher/${teacher.id}/`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to delete teacher");
                }
                alert("Teacher deleted successfully!");
                window.location.reload();
            })
            .catch((error) => {
                showError(error);
            })
            .finally(() => {
                hideLoader();
            });
    }
}

function saveTeacherType() {
    const selectedType = teacherTypeSelect.value;

    if (!currentTeacher) {
        showError({ message: "No teacher selected!" });
        return;
    }

    if (!selectedType) {
        showError({ message: "Please select a teacher type!" });
        return;
    }

    // Update the teacher object with new type
    const updatedTeacher = {
        ...currentTeacher,
        teacher_type: selectedType,
        designation: selectedType === "hod" ? "HOD" : currentTeacher.designation,
    };

    showLoader();
    fetch(`${baseUrl}/updateTeacher/${currentTeacher.id}/`, {
        method: "PUT",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedTeacher),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to update teacher type");
            }
            return response.json();
        })
        .then((updatedTeacher) => {
            alert("Teacher type updated successfully!");
            window.location.reload();
        })
        .catch((error) => {
            showError(error);
        })
        .finally(() => {
            hideLoader();
        });
}

// Add these event listeners in your setupEventListeners function
function setupEventListeners() {
    teacherSearch.addEventListener("input", filterTeachers);
    closeModal.addEventListener(
        "click",
        () => (teacherDetailsModal.style.display = "none")
    );
    window.addEventListener("click", (e) => {
        if (e.target === teacherDetailsModal)
            teacherDetailsModal.style.display = "none";
    });

    // Add these new event listeners
    saveTypeBtn.addEventListener("click", saveTeacherType);
    cancelEditBtn.addEventListener(
        "click",
        () => (teacherDetailsModal.style.display = "none")
    );
}