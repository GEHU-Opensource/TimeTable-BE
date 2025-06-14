document.addEventListener("DOMContentLoaded", function () {
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

    const uploadForm = document.getElementById("uploadForm");
    const csvInput = document.getElementById("csvFiles");
    const responseDiv = document.getElementById("response");
    const baseUrl = BE_URL;

    uploadForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        if (csvInput.files.length <= 1) {
            showMessage("Please select at least two CSV files.", "error");
            return;
        }
        if (csvInput.files.length === 0) {
            showMessage("Please select at least one CSV file.", "error");
            return;
        }

        const formData = new FormData();
        for (const file of csvInput.files) {
            formData.append("csv_files", file);
        }

        showLoader();
        try {
            showMessage("Processing... Please wait.", "info");

            const response = await fetch(`${baseUrl}/detectConflicts/`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            responseDiv.style.display = "block";
            responseDiv.innerHTML = "";

            if (response.ok) {
                if (data.conflicts && data.conflicts.length > 0) {
                    displayConflicts(data.conflicts);
                } else if (data.message) {
                    showMessage(data.message, "success");
                }
            } else {
                showMessage(
                    data.error || "An error occurred while processing.",
                    "error"
                );
            }
        } catch (error) {
            showMessage("Network error. Please try again.", "error");
        } finally {
            hideLoader();
        }
    });

    function showMessage(message, type) {
        responseDiv.innerHTML = `<p class="${type}">${message}</p>`;
        responseDiv.style.display = "block";
    }

    function displayConflicts(conflicts) {
        responseDiv.innerHTML = "<h3>Conflicts Found</h3>";
        conflicts.forEach((conflict, index) => {
            const conflictEntry = document.createElement("div");
            conflictEntry.classList.add("conflict-entry");

            conflictEntry.innerHTML = `
      <p><strong>Timetable 1:</strong> ${conflict.timetable_1}</p>
      <p><strong>Timetable 2:</strong> ${conflict.timetable_2}</p>
      <pre><strong>Conflict Details:</strong> ${JSON.stringify(
                conflict.conflict_details,
                null,
                2
            )}</pre>
      <hr>
    `;
            responseDiv.appendChild(conflictEntry);
        });
        responseDiv.style.display = "block";
    }
});
