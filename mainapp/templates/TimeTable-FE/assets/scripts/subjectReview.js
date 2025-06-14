document.addEventListener("DOMContentLoaded", function () {
    showTab("pending");

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
const searchBar = document.querySelector(".searchBar");
let requests = {};
let approved = {};
const token = localStorage.getItem("access_token");

const searchSubject = document.getElementById("pendingSubjectSearch");
searchSubject.addEventListener("input", function () {
    searchPendingSubjects(this.value.toLowerCase());
});

// Tab Functions
function showTab(tabId) {
    toggleActiveClass(tabId);
    if (tabId === "pending") {
        getPendingRequests();
    } else {
        getApprovedSubjects();
        checkScrollbar();
    }
}

function checkScrollbar() {
    const footer = document.querySelector("footer");
    if (document.body.scrollHeight <= window.innerHeight) {
        footer.classList.add("fixed");
    } else {
        footer.classList.remove("fixed");
    }
}


function toggleActiveClass(tabId) {
    document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active"));
    document.querySelectorAll(".tab-btn").forEach(button => button.classList.remove("active"));
    document.getElementById(tabId).classList.add("active");
    document.querySelector(`button[onclick="showTab('${tabId}')"]`).classList.add("active");
}

// Pending Requests Functions
function getPendingRequests() {
    showLoader();
    fetch(`${baseUrl}/getPendingRequests/`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
    })
        .then(handleResponse)
        .then(data => {
            if (Object.keys(data.pending_requests).length === 0) {
                document.querySelector(".request-container").innerHTML = `<p class="emptyRequests">No subject is pending for approval.</p>`;
                return;
            }
            searchBar.style.display = "flex";
            requests = { ...data };
            loadPendingSubjects(requests);
        })
        .catch(showError)
        .finally(() => {
            hideLoader();
        });
}

function loadPendingSubjects(requests) {
    const requestContainer = document.querySelector(".request-container");
    requestContainer.innerHTML = "";
    requests.subjects.forEach(({ subject_name, subject_code }) => {
        populateSubjectCard(subject_name, subject_code, requests);
    });
    createApproveButton(requests);
}

function searchPendingSubjects(searchValue) {
    const filteredSubjects = requests.subjects.filter(({ subject_name, subject_code }) =>
        subject_name.toLowerCase().includes(searchValue) || subject_code.toLowerCase().includes(searchValue)
    );

    const requestContainer = document.querySelector(".request-container");
    requestContainer.innerHTML = "";
    const approveBtn = document.getElementById("approveBtn");

    if (filteredSubjects.length === 0) {
        requestContainer.innerHTML = `<p class="emptyRequests">No subjects found.</p>`;
        approveBtn.style.display = "none";
    } else {
        filteredSubjects.forEach(({ subject_name, subject_code }) => {
            populateSubjectCard(subject_name, subject_code, requests);
        });
        approveBtn.style.display = "inline-block";
    }
    checkScrollbar();
}

// Subject Card Functions
function populateSubjectCard(subject_name, subject_code, requests) {
    const subjectDiv = createSubjectCard(subject_name, subject_code, requests);
    document.querySelector(".request-container").appendChild(subjectDiv);
}

function createSubjectCard(subject_name, subject_code, requests) {
    const subjectDiv = document.createElement("div");
    subjectDiv.classList.add("subject-container");

    const teachersLabel = requests.pending_requests[subject_code] || [];
    const assignedTeachers = teachersLabel.map(obj => {
        const teacherCode = Object.keys(obj)[0];
        const teacherName = obj[teacherCode];
        return `${teacherName} (${teacherCode})`;
    }).filter(Boolean);

    subjectDiv.innerHTML = `
        <label class="subject">${subject_name}<br>(${subject_code})</label>
        <div class="teacher-selection">
            <input type="text" class="teacher-search" placeholder="Search and select teachers">
            <div class="dropdown-content"></div>
        </div>
        <label>Selected Teachers</label>
        <div class="selected-teachers"></div>
    `;

    const searchInput = subjectDiv.querySelector(".teacher-search");
    const dropdown = subjectDiv.querySelector(".dropdown-content");
    const selectedTeachersDiv = subjectDiv.querySelector(".selected-teachers");

    setupTeacherDropdown(assignedTeachers, requests, dropdown, selectedTeachersDiv, searchInput);
    return subjectDiv;
}

function setupTeacherDropdown(assignedTeachers, requests, dropdown, selectedTeachersDiv, searchInput) {
    populateDropdown(assignedTeachers, requests, dropdown);
    populateSelectedTeachers(assignedTeachers, selectedTeachersDiv);
    attachDropdownListeners(searchInput, dropdown, selectedTeachersDiv);
}

function populateDropdown(assignedTeachers, requests, dropdown) {
    const allTeachers = requests.teachers.map(t => t.teacher_name + " (" + t.teacher_code + ")");
    assignedTeachers.forEach(teacher => dropdown.appendChild(createTeacherCheckbox(teacher, true)));
    allTeachers.filter(t => !assignedTeachers.includes(t)).forEach(teacher_code => dropdown.appendChild(createTeacherCheckbox(teacher_code, false)));
}

function createTeacherCheckbox(teacher, checked) {
    const label = document.createElement("label");
    label.innerHTML = `
        <input type="checkbox" value="${teacher}" ${checked ? "checked" : ""}>
        ${teacher}
    `;
    return label;
}

function populateSelectedTeachers(assignedTeachers, selectedTeachersDiv) {
    assignedTeachers.forEach(teacher => {
        const teacherTag = document.createElement("span");
        teacherTag.textContent = teacher;
        teacherTag.classList.add("selected-teacher");
        selectedTeachersDiv.appendChild(teacherTag);
    });
}

function attachDropdownListeners(searchInput, dropdown, selectedTeachersDiv) {
    searchInput.addEventListener("click", () => {
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });

    dropdown.addEventListener("change", (event) => {
        updateSelectedTeachers(event.target, selectedTeachersDiv);
    });

    searchInput.addEventListener("input", function () {
        filterDropdownOptions(this.value.toLowerCase(), dropdown);
    });

    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.style.display = "none";
        }
    });
}

function updateSelectedTeachers(checkbox, selectedTeachersDiv) {
    if (checkbox.checked) {
        const teacherTag = document.createElement("span");
        teacherTag.textContent = checkbox.value;
        teacherTag.classList.add("selected-teacher");
        selectedTeachersDiv.appendChild(teacherTag);
    } else {
        Array.from(selectedTeachersDiv.children).forEach(span => {
            if (span.textContent === checkbox.value) {
                span.remove();
            }
        });
    }
}

function filterDropdownOptions(searchValue, dropdown) {
    const labels = dropdown.querySelectorAll("label");
    let hasVisibleOption = false;

    labels.forEach((label) => {
        const text = label.textContent.toLowerCase();
        label.style.display = text.includes(searchValue) ? "flex" : "none";
        if (text.includes(searchValue)) hasVisibleOption = true;
    });

    dropdown.style.display = hasVisibleOption ? "block" : "none";
}

// Approval Functions
function createApproveButton(requests) {
    const submitSection = document.createElement("div");
    submitSection.classList.add("submitBtn");
    submitSection.innerHTML = `<button type="submit" id="approveBtn">Approve</button>`;
    document.getElementById("approveButton").innerHTML = "";
    document.getElementById("approveButton").appendChild(submitSection);
    document.getElementById("approveBtn").addEventListener("click", () => {
        handleApprovalClick(requests);
    });
}

function handleApprovalClick(requests) {
    const selectedTeachersMap = getSelectedTeachersMap(requests);
    if (!isValidTeachersSelection(selectedTeachersMap)) {
        alert(`Please select at least one Teacher for each Subject!`);
        return;
    }
    submitApproval(selectedTeachersMap);
}

function getSelectedTeachersMap(requests) {
    const selectedTeachersMap = {};
    document.querySelectorAll(".subject-container").forEach(subjectDiv => {
        const subjectCode = subjectDiv.querySelector(".subject").textContent.match(/\((.*?)\)/)[1];
        const selectedTeachers = [];

        subjectDiv.querySelectorAll(".selected-teachers .selected-teacher").forEach(span => {
            const teacherNameAndCode = span.textContent;
            let teacherCode = null;
            if (teacherNameAndCode.includes("(")) {
                teacherCode = teacherNameAndCode.substring(
                    teacherNameAndCode.indexOf('(') + 1,
                    teacherNameAndCode.indexOf(')')
                );
            } else {
                teacherCode = teacherNameAndCode;
            }
            const teacherData = requests.teachers.find(t => t.teacher_code === teacherCode);

            if (teacherData) selectedTeachers.push(teacherData.teacher_code)
            else selectedTeachers.push(teacherCode);
        });

        selectedTeachersMap[subjectCode] = selectedTeachers;
    });

    return selectedTeachersMap;
}

function isValidTeachersSelection(selectedTeachersMap) {
    return Object.values(selectedTeachersMap).every(teachers => teachers.length > 0);
}

function submitApproval(selectedTeachersMap) {
    showLoader();
    fetch(`${baseUrl}/approveSubjectRequests/`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(selectedTeachersMap),
    })
        .then(handleResponse)
        .then(() => {
            alert("Subjects approved successfully!");
            document.location.reload();
        })
        .catch(error => {
            console.error("Error approving subjects:", error);
            alert("Failed to approve subjects.");
        })
        .finally(() => {
            hideLoader();
        });
}

// Approved Subjects Functions
function getApprovedSubjects() {
    showLoader();
    fetch(`${baseUrl}/getApprovedSubjects/`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
    })
        .then(handleResponse)
        .then(data => {
            renderApprovedSubjects(data);
            approved = { ...data };
        })
        .catch(showError)
        .finally(() => {
            hideLoader();
        });
}

function renderApprovedSubjects(approvedData) {
    const approvedContainer = document.querySelector("#approved .approved-container");
    approvedContainer.innerHTML = "";

    if (!approvedData.length) {
        approvedContainer.innerHTML = `<p class="emptyApproved">No subject is approved.</p>`;
        return;
    }

    const table = document.createElement("table");
    table.classList.add("approved-table");

    const tableHeader = `
        <thead>
            <tr>
                <th>
                    Subject Name<br>
                    <input type="text" class="subjectTable" id="subjectSearch" placeholder="Search Subject Name">
                </th>
                <th>
                    Subject Code<br>
                    <input type="text" class="subjectTable" id="codeSearch" placeholder="Search Subject Code">
                </th>
                <th>
                    Faculty<br>
                    <input type="text" class="subjectTable" id="facultySearch" placeholder="Search Faculty">
                </th>
            </tr>
        </thead>
    `;

    const tableBody = document.createElement("tbody");

    let lastSubject = null;
    approvedData.forEach(({ subject_name, subject_code, teachers }) => {
        const teachersName = getTeachersNames(teachers);
        const subjectDiv = createApprovedSubjectCard(subject_name, subject_code, teachersName, lastSubject);
        lastSubject = subjectDiv ? { subject_name, subject_code } : lastSubject;
        tableBody.appendChild(subjectDiv);
    });

    table.innerHTML = tableHeader;
    table.appendChild(tableBody);
    approvedContainer.appendChild(table);

    addSearchFilters();
}

function getTeachersNames(teachersArray) {
    return teachersArray.map(teacherObj => {
        const teacherCode = Object.keys(teacherObj)[0];
        const teacherName = teacherObj[teacherCode];
        return `${teacherName} (${teacherCode})`;
    });
}

function createApprovedSubjectCard(subject_name, subject_code, teachers, lastSubject) {
    const subjectDiv = document.createElement("tr");

    if (lastSubject && lastSubject.subject_name === subject_name && lastSubject.subject_code === subject_code) {
        subjectDiv.innerHTML = `
            <td></td>
            <td></td>
            <td>
                ${teachers.length > 0
                ? `<ul class="faculty-list">
                        ${teachers.map(teacher => `<li class="faculty-name">${teacher}</li>`).join('')}
                      </ul>`
                : "<span class='faculty-name'>No faculty assigned</span>"}
            </td>
        `;
    } else {
        subjectDiv.innerHTML = `
            <td>${subject_name}</td>
            <td>${subject_code}</td>
            <td>
                ${teachers.length > 0
                ? `<ul class="faculty-list">
                        ${teachers.map(teacher => `<li class="faculty-name">${teacher}</li>`).join('')}
                      </ul>`
                : "<span class='faculty-name'>No faculty assigned</span>"}
            </td>
        `;
    }

    return subjectDiv;
}

function addSearchFilters() {
    const subjectSearch = document.getElementById("subjectSearch");
    const codeSearch = document.getElementById("codeSearch");
    const facultySearch = document.getElementById("facultySearch");

    subjectSearch.addEventListener("input", filterTable);
    codeSearch.addEventListener("input", filterTable);
    facultySearch.addEventListener("input", filterTable);
}

function filterTable() {
    const subjectValue = document.getElementById("subjectSearch").value.toLowerCase();
    const codeValue = document.getElementById("codeSearch").value.toLowerCase();
    const facultyValue = document.getElementById("facultySearch").value.toLowerCase();

    const rows = document.querySelectorAll(".approved-table tbody tr");

    rows.forEach(row => {
        const subjectName = row.children[0].textContent.toLowerCase();
        const subjectCode = row.children[1].textContent.toLowerCase();
        const facultyNames = row.children[2].textContent.toLowerCase();

        const subjectMatch = subjectName.includes(subjectValue);
        const codeMatch = subjectCode.includes(codeValue);
        const facultyMatch = facultyNames.includes(facultyValue);

        if (subjectMatch && codeMatch && facultyMatch) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

function handleResponse(response) {
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    return response.json();
}

function showError(error) {
    console.error("Error: ", error);

    if (error.message.includes("401")) {
        alert("Session expired. Redirecting to login...");
        window.location.href = "../index.html";
    } else {
        alert(error.message || "An error occurred.");
    }
}