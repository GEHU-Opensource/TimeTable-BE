import { showLoader, hideLoader, authFetch, BE_URL, departments } from './data.js';

document.addEventListener("DOMContentLoaded", () => {
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

    function init() {
        loadComponent("navbar-admin", "/TimeTable-FE/assets/components/admin_navbar.html");
        loadComponent("footer", "/TimeTable-FE/assets/components/footer.html");
        setTimeout(highlightActiveLink, 1000);
    }
    init();

    const token = localStorage.getItem("access_token");
    const departmentDropdown = document.getElementById("department");
    const courseDropdown = document.getElementById("course");
    const branchDropdown = document.getElementById("branch");
    const yearDropdown = document.getElementById("year");
    const semesterDropdown = document.getElementById("semester");
    const getSubjectsButton = document.getElementById("getSubjects");
    const existingSubjectTableBody = document.querySelector(
        "#subjectListTable tbody"
    );
    const newSubjectTableBody = document.querySelector("#newSubjectTable tbody");
    const baseUrl = BE_URL;
    const addSubjectBtn = document.getElementById("addSubjectBtn");
    const submitBtn = document.getElementById("submitBtn");

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

    departmentDropdown.addEventListener("change", function () {
        const selectedDepartment = departmentDropdown.value;
        clearDropdown(courseDropdown);
        populateDropdown(
            courseDropdown,
            departments.find((dep) => dep.name === selectedDepartment)?.courses || [],
            "name",
            "name"
        );
    });

    courseDropdown.addEventListener("change", function () {
        const selectedDepartment = departments.find(
            (department) => department.name === departmentDropdown.value
        );
        const selectedCourse = selectedDepartment?.courses.find(
            (course) => course.name === courseDropdown.value
        );
        clearDropdown(branchDropdown);
        populateDropdown(
            branchDropdown,
            selectedCourse?.branches || [],
            "name",
            "name"
        );
    });

    branchDropdown.addEventListener("change", function () {
        const selectedDepartment = departments.find(
            (department) => department.name === departmentDropdown.value
        );
        const selectedCourse = selectedDepartment?.courses.find(
            (course) => course.name === courseDropdown.value
        );
        const selectedBranch = selectedCourse?.branches.find(
            (branch) => branch.name === branchDropdown.value
        );
        clearDropdown(yearDropdown);
        populateDropdown(yearDropdown, selectedBranch?.years || [], "year", "year");
    });

    yearDropdown.addEventListener("change", function () {
        const selectedDepartment = departments.find(
            (department) => department.name === departmentDropdown.value
        );
        const selectedCourse = selectedDepartment?.courses.find(
            (course) => course.name === courseDropdown.value
        );
        const selectedBranch = selectedCourse?.branches.find(
            (branch) => branch.name === branchDropdown.value
        );
        const selectedYear = selectedBranch?.years.find(
            (year) => year.year === yearDropdown.value
        );
        clearDropdown(semesterDropdown);
        populateDropdown(
            semesterDropdown,
            selectedYear?.semesters || [],
            "sem",
            "sem"
        );
    });

    function displayExistingSubjects(subjects) {
        existingSubjectTableBody.innerHTML = "";
        subjects.forEach((subject) => {
            const row = document.createElement("tr");
            row.dataset.subjectId = subject.id;
            row.innerHTML = `
                    <td><input type="text" class="subject-code" value="${subject.subject_code}" disabled /></td>
                    <td><input type="text" class="subject-name" value="${subject.subject_name}" disabled /></td>
                    <td>
                        <select class="subject-credit" disabled>
                            <option value="0" ${subject.credits === 0 ? "selected" : ""}>0</option>
                            <option value="1" ${subject.credits === 1 ? "selected" : ""}>1</option>
                            <option value="2" ${subject.credits === 2 ? "selected" : ""}>2</option>
                            <option value="3" ${subject.credits === 3 ? "selected" : ""}>3</option>
                            <option value="4" ${subject.credits === 4 ? "selected" : ""}>4</option>
                        </select>
                    </td>
                    <td>
                        <select class="subject-weekly" disabled>
                            <option value="1" ${subject.weekly_quota_limit === 1 ? "selected" : ""}>1</option>
                            <option value="2" ${subject.weekly_quota_limit === 2 ? "selected" : ""}>2</option>
                            <option value="3" ${subject.weekly_quota_limit === 3 ? "selected" : ""}>3</option>
                            <option value="4" ${subject.weekly_quota_limit === 4 ? "selected" : ""}>4</option>
                        </select>
                    </td>
                    <td>
                        <select class="subject-special" disabled>
                            <option value="No" ${subject.is_special_subject === "No" ? "selected" : ""}>No</option>
                            <option value="Yes" ${subject.is_special_subject === "Yes" ? "selected" : ""}>Yes</option>
                        </select>
                    </td>
                    <td>
                        <select class="is-Lab" disabled>
                            <option value="No" ${subject.is_lab === "No" ? "selected" : ""}>No</option>
                            <option value="Yes" ${subject.is_lab === "Yes" ? "selected" : ""}>Yes</option>
                        </select>
                    </td>
                    <td>
                        <button class="edit-btn" title="Edit"><i class="fas fa-edit"></i></button>
                        <button class="delete-btn" title="Delete"><i class="fas fa-trash-alt"></i></button>
                    </td>
                `;
            const editButton = row.querySelector(".edit-btn");
            const deleteButton = row.querySelector(".delete-btn");
            const inputs = row.querySelectorAll("input, select");

            editButton.addEventListener("click", () => {
                const icon = editButton.querySelector("i");
                if (icon.classList.contains("fa-edit")) {
                    inputs.forEach((input) => (input.disabled = false));
                    icon.classList.remove("fa-edit");
                    icon.classList.add("fa-save");
                    editButton.title = "Save";
                } else {
                    const selectedDepartment = departmentDropdown.value;
                    const selectedCourse = courseDropdown.value;
                    const selectedBranch = branchDropdown.value;
                    const selectedSemester = semesterDropdown.value;
                    const data = {
                        department: selectedDepartment,
                        course: selectedCourse,
                        branch: selectedBranch,
                        semester: selectedSemester,
                        subjects: [],
                    };
                    if (
                        inputs[0].value.trim() !== "" &&
                        inputs[1].value.trim() !== ""
                    ) {
                        const subjectCodeInput = row.querySelector(".subject-code");
                        const subjectNameInput = row.querySelector(".subject-name");
                        const subjectCreditInput = row.querySelector(".subject-credit");
                        const subjectWeeklyInput = row.querySelector(".subject-weekly");
                        const specialSubjectInput = row.querySelector(".subject-special");
                        const isLabInput = row.querySelector(".is-Lab");
                        const subjectCode = subjectCodeInput.value.trim();
                        const subjectName = subjectNameInput.value.trim();
                        const subjectCredit = subjectCreditInput.value.trim();
                        const subjectWeekly = subjectWeeklyInput.value.trim();
                        const specialSubject = specialSubjectInput.value.trim();
                        const isLab = isLabInput.value.trim();
                        const editedsubject = {
                            subject_name: subjectName,
                            subject_code: subjectCode,
                            credits: subjectCredit,
                            weekly_quota_limit: subjectWeekly,
                            is_special_subject: specialSubject,
                            is_lab: isLab,
                        };
                        data.subjects.push(editedsubject);

                        showLoader();
                        fetch(`${baseUrl}/updateSubject/${row.dataset.subjectId}/`, {
                            method: "PUT",
                            headers: {
                                Authorization: `Bearer ${token}`,
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify(editedsubject),
                        })
                            .then((response) => {
                                if (!response.ok) {
                                    return response.json().then((data) => {
                                        throw new Error(
                                            data.error || "Failed to save data. Please try again."
                                        );
                                    });
                                }
                                return response.json();
                            })
                            .then((responseData) => {
                                alert("Subject updation successful!");
                                icon.classList.remove("fa-save");
                                icon.classList.add("fa-edit");
                                editButton.title = "Edit";
                                inputs.forEach((input) => (input.disabled = true));
                            })
                            .catch((error) => {
                                console.error("Error submitting data:", error);
                                alert(error.message);
                            })
                            .finally(() => {
                                hideLoader();
                            });
                    } else {
                        alert("Please fill all the Subject Details!");
                        inputs.forEach((input) => (input.disabled = false));
                        return;
                    }
                }
            });

            deleteButton.addEventListener("click", () => {
                let result = confirm("Are you sure to Delete?");
                if (result) {
                    row.remove();

                    showLoader();
                    fetch(`${baseUrl}/deleteSubject/${row.dataset.subjectId}/`, {
                        method: "DELETE",
                        headers: {
                            Authorization: `Bearer ${token}`,
                            "Content-Type": "application/json",
                        },
                    })
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .catch((error) => {
                            console.error("Error deleting subject:", error);
                            alert("Failed to delete subject. Please try again.");
                        })
                        .finally(() => {
                            hideLoader();
                        });
                } else {
                    return;
                }
            });
            existingSubjectTableBody.appendChild(row);
        });
    }

    getSubjectsButton.addEventListener("click", function () {
        const selectedDepartment = departmentDropdown.value;
        const selectedCourse = courseDropdown.value;
        const selectedBranch = branchDropdown.value;
        const selectedSemester = semesterDropdown.value;
        const params = new URLSearchParams({
            department: selectedDepartment,
            course: selectedCourse,
            branch: selectedBranch,
            semester: selectedSemester,
        });
        if (
            !selectedDepartment ||
            !selectedCourse ||
            !selectedBranch ||
            !selectedSemester
        ) {
            alert("Please fill in all the fields.");
            return;
        }

        showLoader();
        fetch(`${baseUrl}/getFilteredSubjects/filter?${params.toString()}`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((fetchedSubjects) => {
                displayExistingSubjects(fetchedSubjects);
            })
            .catch((error) => {
                console.error("Error: ", error);
                alert(error);
            })
            .finally(() => {
                hideLoader();
            });

        const subjectDatas = document.getElementById("subjectData");
        newSubjectTableBody.textContent = "";
        subjectDatas.style.display = "block";
    });

    addSubjectBtn.addEventListener("click", function () {
        const newRow = document.createElement("tr");
        newRow.innerHTML = `
                <td><input type="text" class="subject-code" placeholder="Enter Subject Code" /></td>
                <td><input type="text" class="subject-name" placeholder="Enter Subject Name" /></td>
                <td>
                    <select class="subject-credit">
                        <option value="0">0</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                    </select>
                </td>
                <td>
                    <select class="subject-weekly">
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                    </select>
                </td>
                <td>
                    <select class="subject-special">
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                    </select>
                </td>
                <td>
                    <select class="is-Lab">
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                    </select>
                </td>
                <td><button class="delete-btn" title="Delete"><i class="fas fa-trash-alt"></i></button></td>
            `;
        const deleteButton = newRow.querySelector(".delete-btn");
        deleteButton.addEventListener("click", () => {
            let result = confirm("Are you sure to Delete?");
            if (result) {
                newRow.remove();
            } else {
                return;
            }
        });
        newSubjectTableBody.appendChild(newRow);
    });

    submitBtn.addEventListener("click", function () {
        const selectedDepartment = departmentDropdown.value;
        const selectedCourse = courseDropdown.value;
        const selectedBranch = branchDropdown.value;
        const selectedYear = yearDropdown.value;
        const selectedSemester = semesterDropdown.value;
        const data = [];
        const subjectRows = document.querySelectorAll("#newSubjectTable tr");
        let allFieldsFilled = true;

        subjectRows.forEach((row) => {
            const subjectCodeInput = row.querySelector(".subject-code");
            const subjectNameInput = row.querySelector(".subject-name");
            const subjectCreditInput = row.querySelector(".subject-credit");
            const subjectWeeklyInput = row.querySelector(".subject-weekly");
            const specialSubjectInput = row.querySelector(".subject-special");
            const isLabInput = row.querySelector(".is-Lab");

            if (subjectCodeInput && subjectNameInput) {
                const subjectCode = subjectCodeInput.value.trim();
                const subjectName = subjectNameInput.value.trim();
                const subjectCredit = subjectCreditInput.value.trim();
                const subjectWeekly = subjectWeeklyInput.value.trim();
                const specialSubject = specialSubjectInput.value.trim();
                const isLab = isLabInput.value.trim();

                if (subjectCode && subjectName && subjectCredit) {
                    const subject = {
                        department: selectedDepartment,
                        course: selectedCourse,
                        branch: selectedBranch,
                        year: selectedYear,
                        semester: selectedSemester,
                        subject_name: subjectName,
                        subject_code: subjectCode,
                        credits: subjectCredit,
                        weekly_quota_limit: subjectWeekly,
                        is_special_subject: specialSubject,
                        is_lab: isLab,
                    };
                    data.push(subject);
                } else {
                    allFieldsFilled = false;
                }
            }
        });

        if (!allFieldsFilled) {
            alert("Please fill in all subject details.");
            return;
        }

        if (data.length > 0) {
            showLoader();
            fetch(`${baseUrl}/addSubject/`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
                .then((response) => {
                    if (!response.ok) {
                        return response.json().then((data) => {
                            const errorMessage = data.errors
                                ? data.errors
                                    .map(
                                        (error) =>
                                            `${error.subject_data.subject_code}: ${error.error}`
                                    )
                                    .join("\n")
                                : data.error || "Failed to add subjects. Please try again.";

                            throw new Error(errorMessage);
                        });
                    }
                    return response.json();
                })
                .then((serverResponse) => {
                    if (serverResponse.message) {
                        alert(serverResponse.message);
                    }
                    if (serverResponse.errors && serverResponse.errors.length > 0) {
                        let errorMessages = "";
                        serverResponse.errors.forEach((error) => {
                            const subjectError = `${error.subject_data.subject_code}: ${error.error}`;
                            errorMessages += subjectError + "\n";
                        });
                        alert(`Error(s) while adding subjects:\n${errorMessages}`);
                    }

                    getSubjectsButton.click();
                })
                .catch((error) => {
                    console.error("Error adding subjects:", error);
                    alert(error.message || "Failed to add subjects. Please try again.");
                })
                .finally(() => {
                    hideLoader();
                });
        } else {
            alert("No subjects to submit.");
        }
    });
});