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
    loadComponent("navbar-admin", "../components/admin_navbar.html");
    loadComponent("footer", "../components/footer.html");
    setTimeout(highlightActiveLink, 1000);

    const departmentDropdown = document.getElementById("department");
    const courseDropdown = document.getElementById("course");
    const branchDropdown = document.getElementById("branch");
    const yearDropdown = document.getElementById("year");
    const semesterDropdown = document.getElementById("semester");
    const sectionInput = document.getElementById("sections");
    const allocateButton = document.getElementById("allocate");
    const downloadButton = document.getElementById("download-btn");
    const timetable = document.getElementById("show");
    const fileInput = document.getElementById('tt');
    const fileChosen = document.getElementById('file-chosen');
    const baseUrl = BE_URL;
    const token = localStorage.getItem("access_token");
    let mongoId = null;

    fileInput.addEventListener('change', () => {
        fileChosen.textContent = fileInput.files[0]?.name || "No file chosen";
    });

    if (typeof departments !== 'undefined') {
        departments.forEach(department => {
            const option = document.createElement('option');
            option.value = department.name;
            option.textContent = department.name;
            departmentDropdown.appendChild(option);
        });
    }
    else {
        console.error("Departments data is not defined.");
    }

    function clearDropdown(dropdown) {
        dropdown.innerHTML = '';
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select an option';
        dropdown.appendChild(defaultOption);
    }

    function populateDropdown(dropdown, options, valueKey, textKey) {
        options.forEach(option => {
            const opt = document.createElement("option");
            opt.value = option[valueKey];
            opt.textContent = option[textKey];
            dropdown.appendChild(opt);
        });
    }

    departmentDropdown.addEventListener("change", function () {
        const selectedDepartment = departmentDropdown.value;
        clearDropdown(courseDropdown);
        populateDropdown(courseDropdown, departments.find(dep => dep.name === selectedDepartment)?.courses || [], "name", "name");
    });

    courseDropdown.addEventListener("change", function () {
        const selectedDepartment = departments.find(department => department.name === departmentDropdown.value);
        const selectedCourse = selectedDepartment?.courses.find(course => course.name === courseDropdown.value);
        clearDropdown(branchDropdown);
        populateDropdown(branchDropdown, selectedCourse?.branches || [], "name", "name");
    });

    branchDropdown.addEventListener("change", function () {
        const selectedDepartment = departments.find(department => department.name === departmentDropdown.value);
        const selectedCourse = selectedDepartment?.courses.find(course => course.name === courseDropdown.value);
        const selectedBranch = selectedCourse?.branches.find(branch => branch.name === branchDropdown.value);
        clearDropdown(yearDropdown);
        populateDropdown(yearDropdown, selectedBranch?.years || [], "year", "year");
    });

    yearDropdown.addEventListener("change", function () {
        const selectedDepartment = departments.find(department => department.name === departmentDropdown.value);
        const selectedCourse = selectedDepartment?.courses.find(course => course.name === courseDropdown.value);
        const selectedBranch = selectedCourse?.branches.find(branch => branch.name === branchDropdown.value);
        const selectedYear = selectedBranch?.years.find(year => year.year === yearDropdown.value);
        clearDropdown(semesterDropdown);
        populateDropdown(semesterDropdown, selectedYear?.semesters || [], "sem", "sem");
    });

    allocateButton.addEventListener("click", function () {
        const data = {
            department: departmentDropdown.value,
            course: courseDropdown.value,
            branch: branchDropdown.value,
            year: yearDropdown.value,
            semester: semesterDropdown.value,
            total_sections: sectionInput.value,
            file: fileInput.files[0],
        };

        if (!data.department || !data.course || !data.branch || !data.year || !data.semester || !data.total_sections) {
            alert("Please fill all the required fields!");
            return;
        }

        if (!fileInput.files.length) {
            alert("Please select a file before submitting.");
            return;
        }

        const formData = new FormData();
        formData.append("department", data.department);
        formData.append("course", data.course);
        formData.append("branch", data.branch);
        formData.append("year", data.year);
        formData.append("semester", data.semester);
        formData.append("total_sections", data.total_sections);
        formData.append("file", data.file);

        showLoader();
        fetch(`${baseUrl}/addStudentAPI/`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
            },
            body: formData
        })
            .then(handleResponse)
            .then(response => {
                const queryParams = new URLSearchParams({
                    department: departmentDropdown.value,
                    course: courseDropdown.value,
                    branch: branchDropdown.value,
                    year: yearDropdown.value
                }).toString();

                return fetch(`${baseUrl}/listSections/?${queryParams}`, {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
            })
            .then(handleResponse)
            .then(response => {
                mongoId = response.mongo_id;
                if (!mongoId) {
                    throw new Error("No mongoId received from server");
                }
                return fetch(`${baseUrl}/downloadSections/${mongoId}/`, {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Failed to download sections");
                }
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'sections.xlsx';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1];
                    }
                }

                return response.blob().then(blob => ({ blob, filename }));
            })
            .then(({ blob, filename }) => {
                // Display the Excel file
                const url = URL.createObjectURL(blob);
                return fetch(url)
                    .then(res => res.arrayBuffer())
                    .then(buffer => {
                        const workbook = XLSX.read(buffer, { type: 'array' });
                        displaySheet(workbook, workbook.SheetNames[0]);
                        timetable.style.display = "block";

                        // Store the blob for later download
                        lastDownloadBlob = { blob, filename };
                    });
            })
            .catch(showError)
            .finally(() => {
                hideLoader();
            });
    });

    downloadButton.addEventListener('click', () => {
        if (!lastDownloadBlob) {
            alert("No sections allocated yet. Please allocate sections first.");
            return;
        }

        const { blob, filename } = lastDownloadBlob;
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    });

    // Add this at the top with your other variable declarations
    let lastDownloadBlob = null;

    function displaySheet(workbook, sheetName) {
        const sheet = workbook.Sheets[sheetName];
        const html = XLSX.utils.sheet_to_html(sheet);
        const outputDiv = document.getElementById("output");
        outputDiv.innerHTML = html;
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
});