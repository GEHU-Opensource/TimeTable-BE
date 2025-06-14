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
    setTimeout(highlightActiveLink, 10000);

    const departmentDropdown = document.getElementById("department");
    const courseDropdown = document.getElementById("course");
    const branchDropdown = document.getElementById("branch");
    const yearDropdown = document.getElementById("year");
    const semesterDropdown = document.getElementById("semester");
    const updateButton = document.getElementById("updateTT");
    const fileInput = document.getElementById("tt");
    const fileChosen = document.getElementById("file-chosen");

    // Display selected file names
    fileInput.addEventListener("change", () => {
        const files = Array.from(fileInput.files).map(file => file.name).join(", ");
        fileChosen.textContent = files || "No file chosen";
    });

    // Populate department dropdown
    if (typeof departments !== "undefined") {
        departments.forEach(department => {
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
        populateDropdown(
            courseDropdown,
            departments.find(dep => dep.name === selectedDepartment)?.courses || [],
            "name",
            "name"
        );
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

    updateButton.addEventListener("click", function () {
        if (!departmentDropdown.value || !courseDropdown.value || !yearDropdown.value || !semesterDropdown.value) {
            alert("Fill in all the details!");
            return;
        }

        if (!fileInput.files.length) {
            alert("Please select at least one file before submitting.");
            return;
        }

        const formData = new FormData();
        formData.append("department", departmentDropdown.value);
        formData.append("course", courseDropdown.value);
        formData.append("branch", branchDropdown.value);
        formData.append("year", yearDropdown.value);
        formData.append("semester", semesterDropdown.value);

        // Append multiple files
        Array.from(fileInput.files).forEach(file => {
            formData.append("csv_files[]", file);
            console.log(file);
        });

        console.log("Form Data:", formData);
        alert("Updated successfully!");

        /*
        fetch("api", {
            method: "POST",
            body: formData, // Using FormData to send files
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Success:", data);
            alert("Timetable updated successfully!");
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to update timetable. Please try again.");
        });
        */
    });
});