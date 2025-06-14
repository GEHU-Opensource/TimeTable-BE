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

    const baseUrl = BE_URL;
    const token = localStorage.getItem("access_token");
    const departmentDropdown = document.getElementById("department");
    const courseDropdown = document.getElementById("course");
    const branchDropdown = document.getElementById("branch");
    const yearDropdown = document.getElementById("year");
    const semesterDropdown = document.getElementById("semester");
    const professorWeeklyLoad = document.getElementById("professorLoad");
    const adjunctWeeklyLoad = document.getElementById("adjunctLoad");
    const hodWeeklyLoad = document.getElementById("hodLoad");
    const assistantProfessorWeeklyLoad = document.getElementById(
        "assistant_professorLoad"
    );
    const lecturerWeeklyLoad = document.getElementById("lecturerLoad");
    const labAssistantWeeklyLoad = document.getElementById("lab_assistantLoad");
    const generateButton = document.getElementById("generateTT");
    const downloadButton = document.getElementById("download-btn");
    const timetable = document.getElementById("show");
    const addTimeSlotButton = document.getElementById("add-time-slot");

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

    addTimeSlotButton.addEventListener("click", function () {
        const tbody = document.getElementById("time-slot-body");

        const row = document.createElement("tr");
        row.classList.add("sortable");

        row.innerHTML = `
            <td><input type="time" class="time-slot-input start-time"></td>
            <td><input type="time" class="time-slot-input end-time"></td>
            <td><button class="delete-btn"><i class="fa fa-trash" aria-hidden="true"></i></button></td>
        `;

        tbody.appendChild(row);
        makeRowsSortable();
    });

    document
        .getElementById("time-slot-body")
        .addEventListener("click", function (event) {
            if (event.target.closest(".delete-btn")) {
                const row = event.target.closest("tr");
                const startTime = row.querySelector(".start-time").value;
                const endTime = row.querySelector(".end-time").value;
                if (!startTime && !endTime) {
                    row.remove();
                } else {
                    if (
                        confirm(
                            "This row contains data. Are you sure you want to delete it?"
                        )
                    ) {
                        row.remove();
                    }
                }
            }
        });

    function makeRowsSortable() {
        let draggedRow = null;
        const tbody = document.getElementById("time-slot-body");

        tbody.querySelectorAll("tr").forEach((row) => {
            row.draggable = true;

            row.addEventListener("dragstart", function () {
                draggedRow = this;
                setTimeout(() => (this.style.opacity = "0.5"), 0);
            });

            row.addEventListener("dragend", function () {
                setTimeout(() => (this.style.opacity = "1"), 0);
                draggedRow = null;
            });

            row.addEventListener("dragover", function (e) {
                e.preventDefault();
                const rows = Array.from(tbody.children);
                const indexDragged = rows.indexOf(draggedRow);
                const indexOver = rows.indexOf(this);

                if (indexDragged > indexOver) {
                    tbody.insertBefore(draggedRow, this);
                } else {
                    tbody.insertBefore(draggedRow, this.nextSibling);
                }
            });
        });
    }

    generateButton.addEventListener("click", function () {
        const data = {
            department: "CSE",
            course: courseDropdown.value,
            semester: semesterDropdown.value,
            weekly_workload: {
                professor: professorWeeklyLoad.value,
                adjunct: adjunctWeeklyLoad.value,
                hod: hodWeeklyLoad.value,
                assistant_professor: assistantProfessorWeeklyLoad.value,
                lecturer: lecturerWeeklyLoad.value,
                lab_assistant: labAssistantWeeklyLoad.value,
            },
            time_slots: {},
        };

        // Capture time slots to pass to displayTimetable
        const timeSlotsArray = [];
        document.querySelectorAll("#time-slot-body tr").forEach((row, index) => {
            const startTime = row.querySelector(".start-time").value;
            const endTime = row.querySelector(".end-time").value;

            if (startTime && endTime) {
                const format12HourWithoutAMPM = (time) => {
                    let [hour, minute] = time.split(":");
                    hour = parseInt(hour);
                    let formattedHour = hour % 12 || 12;
                    return `${formattedHour}:${minute}`;
                };

                const slot = `${format12HourWithoutAMPM(
                    startTime
                )} - ${format12HourWithoutAMPM(endTime)}`;
                data.time_slots[String(index + 1)] = slot;
                timeSlotsArray.push(slot);
            }
        });

        if (!data.department || !data.course) {
            alert("Fill in all the details");
            return;
        }
        if (
            data.weekly_workload.professor === "0" ||
            data.weekly_workload.adjunct === "0" ||
            data.weekly_workload.hod === "0" ||
            data.weekly_workload.assistant_professor === "0" ||
            data.weekly_workload.lecturer === "0" ||
            data.weekly_workload.lab_assistant === "0" ||
            data.weekly_workload.professor === "" ||
            data.weekly_workload.adjunct === "" ||
            data.weekly_workload.hod === "" ||
            data.weekly_workload.assistant_professor === "" ||
            data.weekly_workload.lecturer === "" ||
            data.weekly_workload.lab_assistant === ""
        ) {
            alert("Enter the Weekly Load!");
            return;
        }

        if (Object.keys(data.time_slots).length === 0) {
            alert("Add at least one time slot!");
            return;
        }

        showLoader();
        fetch(`${baseUrl}/timetable/generate/`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((responseData) => {
                alert("Timetable generated successfully!");
                displayTimetable(
                    responseData,
                    data.department,
                    data.course,
                    data.semester,
                    timeSlotsArray
                );
            })
            .catch((error) => {
                console.error("Error generating timetable:", error);
                alert("Failed to generate the timetable: " + error.message);
            })
            .finally(() => {
                hideLoader();
            });
    });
});

function displayTimetable(data, department, course, semester, timeSlotsArray) {
    const container = document.getElementById("show");
    container.innerHTML = "";
    container.style.display = "block";

    // Create the container div
    const timetableContainer = document.createElement("div");
    timetableContainer.className = "container";

    // Header section
    const header = document.createElement("div");
    header.className = "header";
    const headerLeft = document.createElement("div");
    headerLeft.className = "header-left";
    const title = document.createElement("h1");
    title.textContent = "Generated TimeTable";
    headerLeft.appendChild(title);

    // Sections dropdown (dynamically fetched from API response)
    const sectionSelect = document.createElement("select");
    const sections = Object.keys(
        data.timetable?.[Object.keys(data.timetable)[0]] || {}
    ).sort();
    sections.forEach((section) => {
        const option = document.createElement("option");
        option.value = section;
        option.textContent = `${department}-${course}-${semester} Section ${section}`;
        sectionSelect.appendChild(option);
    });
    headerLeft.appendChild(sectionSelect);

    const downloadBtn = document.createElement("button");
    downloadBtn.textContent = "Download";
    downloadBtn.onclick = () =>
        (window.location.href = data.sections?.download_link || "#");
    headerLeft.appendChild(downloadBtn);

    header.appendChild(headerLeft);
    timetableContainer.appendChild(header);

    // Title and subtitle
    const titleDiv = document.createElement("div");
    titleDiv.className = "title";
    titleDiv.textContent = `TIME TABLE: ${course} ${department} ${semester} (2024-25 ${semester%2===0 ? 'EVEN' : 'ODD'} SEMESTER)`;
    timetableContainer.appendChild(titleDiv);

    // Create table
    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const dayHeader = document.createElement("th");
    dayHeader.textContent = "DAY \\ TIME";
    dayHeader.className = "day-col";
    headerRow.appendChild(dayHeader);

    // Function to parse time in HH:MM format to minutes for comparison
    const parseTimeToMinutes = (time) => {
        const [hours, minutes] = time.split(":").map(Number);
        return hours * 60 + minutes;
    };

    // Function to format minutes back to HH:MM
    const formatMinutesToTime = (totalMinutes) => {
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        return `${hours.toString().padStart(2, "0")}:${minutes
            .toString()
            .padStart(2, "0")}`;
    };

    // Get days from response and sort them
    const dayOrder = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ];
    const days = Object.keys(data.timetable || {})
        .filter((day) => dayOrder.includes(day))
        .sort((a, b) => dayOrder.indexOf(a) - dayOrder.indexOf(b));

    // Extract time slots in their original order from the response
    const orderedTimeSlots = [];
    const timeSlotIndices = new Set();

    // First, collect time slots from the first section of the first day
    const firstSection = sections[0]; // e.g., Section A
    const firstDay = days[0]; // Monday
    const firstDaySlots = data.timetable?.[firstDay]?.[firstSection] || [];

    firstDaySlots.forEach((slot) => {
        if (slot.time_slot && !timeSlotIndices.has(slot.time_slot)) {
            orderedTimeSlots.push(slot.time_slot);
            timeSlotIndices.add(slot.time_slot);
        }
    });

    // Then, collect additional unique time slots from other days/sections
    days.forEach((day) => {
        sections.forEach((section) => {
            (data.timetable?.[day]?.[section] || []).forEach((slot) => {
                if (slot.time_slot && !timeSlotIndices.has(slot.time_slot)) {
                    orderedTimeSlots.push(slot.time_slot);
                    timeSlotIndices.add(slot.time_slot);
                }
            });
        });
    });

    // If no time slots found, fall back to timeSlotsArray
    let timeSlots =
        orderedTimeSlots.length > 0
            ? orderedTimeSlots
            : timeSlotsArray && Array.isArray(timeSlotsArray)
                ? [...timeSlotsArray]
                : [];

    // If still no time slots, log an error and return
    if (timeSlots.length === 0) {
        console.error("No time slots available to display the timetable.");
        const errorDiv = document.createElement("div");
        errorDiv.textContent =
            "Error: No time slots available to display the timetable.";
        timetableContainer.appendChild(errorDiv);
        container.appendChild(timetableContainer);
        return;
    }

    // Create final time slots with BREAK and LUNCH inserted without altering original order
    // Final time slots with BREAK/LUNCH inserted (based on display order, not sorted order)
    const finalTimeSlots = [];
    let gapCount = 0;

    for (let i = 0; i < timeSlots.length; i++) {
        const currentSlot = timeSlots[i];
        finalTimeSlots.push(currentSlot);

        if (i < timeSlots.length - 1) {
            const [_, currentEnd] = currentSlot.split(" - ").map((t) => t.trim());
            const [nextStart] = timeSlots[i + 1].split(" - ").map((t) => t.trim());

            const currentEndMinutes = parseTimeToMinutes(currentEnd);
            const nextStartMinutes = parseTimeToMinutes(nextStart);

            if (nextStartMinutes > currentEndMinutes) {
                const gapSlot = `${formatMinutesToTime(
                    currentEndMinutes
                )} - ${formatMinutesToTime(nextStartMinutes)}`;
                const gapLabel =
                    gapCount === 0 ? "BREAK" : gapCount === 1 ? "LUNCH" : "BREAK";
                gapCount++;

                finalTimeSlots.push(`${gapSlot} ${gapLabel}`);
            }
        }
    }

    // Add time slots to header
    finalTimeSlots.forEach((slot) => {
        const th = document.createElement("th");
        if (slot.includes("BREAK") || slot.includes("LUNCH")) {
            th.textContent = slot.includes("BREAK") ? "BREAK" : "LUNCH";
            th.className = slot.includes("BREAK") ? "break" : "lunch";
        } else {
            th.textContent = slot;
        }
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Function to render table body for a specific section
    function renderTableBody(selectedSection) {
        const tbody = document.createElement("tbody");
        days.forEach((day, dayIndex) => {
            const row = document.createElement("tr");
            const dayCell = document.createElement("td");
            dayCell.textContent = day.toUpperCase();
            dayCell.className = "day-col";
            row.appendChild(dayCell);

            let slotIndex = 0;
            while (slotIndex < finalTimeSlots.length) {
                const slot = finalTimeSlots[slotIndex];
                const cell = document.createElement("td");

                if (slot.includes("BREAK")) {
                    cell.textContent = "BREAK";
                    cell.className = "break";
                    if (dayIndex === 0) {
                        cell.setAttribute("rowspan", days.length);
                    } else {
                        slotIndex++;
                        continue;
                    }
                } else if (slot.includes("LUNCH")) {
                    cell.textContent = "LUNCH";
                    cell.className = "lunch";
                    if (dayIndex === 0) {
                        cell.setAttribute("rowspan", days.length);
                    } else {
                        slotIndex++;
                        continue;
                    }
                } else {
                    // Normal time slot - find the classes for this day and section
                    const classes = (data.timetable?.[day]?.[selectedSection] || [])
                        .filter((c) => c.time_slot === slot)
                        .sort(
                            (a, b) =>
                                (a.group === "all" ? 0 : a.group) -
                                (b.group === "all" ? 0 : b.group)
                        );

                    if (classes.length > 0) {
                        // Check if classes can be combined
                        const groupedClasses = [];
                        const processedGroups = new Set();
                        for (const cls of classes) {
                            if (cls.group !== "all" && !processedGroups.has(cls.group)) {
                                const sameSubjectClasses = classes.filter(
                                    (c) =>
                                        c.subject_id === cls.subject_id &&
                                        c.teacher_id === cls.teacher_id &&
                                        c.time_slot === cls.time_slot
                                );
                                if (sameSubjectClasses.length > 1) {
                                    groupedClasses.push({
                                        subject_id: cls.subject_id,
                                        teacher_id: cls.teacher_id,
                                        classrooms: sameSubjectClasses.map((c) => ({
                                            group: c.group,
                                            classroom_id: c.classroom_id,
                                        })),
                                        group: "combined",
                                    });
                                    sameSubjectClasses.forEach((c) =>
                                        processedGroups.add(c.group)
                                    );
                                } else {
                                    groupedClasses.push(cls);
                                    processedGroups.add(cls.group);
                                }
                            } else if (cls.group === "all") {
                                groupedClasses.push(cls);
                            }
                        }

                        const currentClass = groupedClasses[0];
                        let displayText;
                        if (currentClass.group === "combined") {
                            const classroomText = currentClass.classrooms
                                .sort((a, b) => a.group - b.group)
                                .map((c) => `${c.classroom_id}(G${c.group})`)
                                .join("/");
                            displayText = `${currentClass.subject_id}<br>${classroomText}<br><div class="teacher">${currentClass.teacher_id}</div>`;
                        } else {
                            displayText = `${currentClass.subject_id}<br>${currentClass.classroom_id}`;
                            if (currentClass.group !== "all") {
                                displayText += ` (G${currentClass.group})`;
                            }
                            displayText += `<br><div class="teacher">${currentClass.teacher_id}</div>`;
                        }

                        // Check for consecutive slots with the same subject details
                        let colspan = 1;
                        for (let i = slotIndex + 1; i < finalTimeSlots.length; i++) {
                            const nextSlot = finalTimeSlots[i];
                            if (nextSlot.includes("BREAK") || nextSlot.includes("LUNCH"))
                                break;

                            const nextClasses = (
                                data.timetable?.[day]?.[selectedSection] || []
                            )
                                .filter((c) => c.time_slot === nextSlot)
                                .sort(
                                    (a, b) =>
                                        (a.group === "all" ? 0 : a.group) -
                                        (b.group === "all" ? 0 : b.group)
                                );

                            const nextGroupedClasses = [];
                            const nextProcessedGroups = new Set();
                            for (const cls of nextClasses) {
                                if (
                                    cls.group !== "all" &&
                                    !nextProcessedGroups.has(cls.group)
                                ) {
                                    const sameSubjectClasses = nextClasses.filter(
                                        (c) =>
                                            c.subject_id === cls.subject_id &&
                                            c.teacher_id === cls.teacher_id &&
                                            c.time_slot === cls.time_slot
                                    );
                                    if (sameSubjectClasses.length > 1) {
                                        nextGroupedClasses.push({
                                            subject_id: cls.subject_id,
                                            teacher_id: cls.teacher_id,
                                            classrooms: sameSubjectClasses.map((c) => ({
                                                group: c.group,
                                                classroom_id: c.classroom_id,
                                            })),
                                            group: "combined",
                                        });
                                        sameSubjectClasses.forEach((c) =>
                                            nextProcessedGroups.add(c.group)
                                        );
                                    } else {
                                        nextGroupedClasses.push(cls);
                                        nextProcessedGroups.add(cls.group);
                                    }
                                } else if (cls.group === "all") {
                                    nextGroupedClasses.push(cls);
                                }
                            }

                            if (
                                nextGroupedClasses.length > 0 &&
                                ((currentClass.group === "combined" &&
                                    nextGroupedClasses[0].group === "combined" &&
                                    currentClass.subject_id ===
                                    nextGroupedClasses[0].subject_id &&
                                    currentClass.teacher_id ===
                                    nextGroupedClasses[0].teacher_id &&
                                    JSON.stringify(
                                        currentClass.classrooms.sort((a, b) => a.group - b.group)
                                    ) ===
                                    JSON.stringify(
                                        nextGroupedClasses[0].classrooms.sort(
                                            (a, b) => a.group - b.group
                                        )
                                    )) ||
                                    (currentClass.group !== "combined" &&
                                        nextGroupedClasses[0].group !== "combined" &&
                                        currentClass.teacher_id ===
                                        nextGroupedClasses[0].teacher_id &&
                                        currentClass.subject_id ===
                                        nextGroupedClasses[0].subject_id &&
                                        currentClass.classroom_id ===
                                        nextGroupedClasses[0].classroom_id &&
                                        currentClass.group === nextGroupedClasses[0].group))
                            ) {
                                colspan++;
                                slotIndex++;
                            } else {
                                break;
                            }
                        }
                        if (colspan > 1) {
                            cell.setAttribute("colspan", colspan);
                        }
                        cell.innerHTML = displayText;
                    } else {
                        cell.className = "empty";
                    }
                }

                row.appendChild(cell);
                slotIndex++;
            }

            tbody.appendChild(row);
        });
        return tbody;
    }

    // Initial render with the first section
    table.appendChild(renderTableBody(sections[0]));

    // Update table body when section changes
    sectionSelect.addEventListener("change", function () {
        const selectedSection = this.value;
        const oldTbody = table.querySelector("tbody");
        oldTbody.remove();
        table.appendChild(renderTableBody(selectedSection));
    });

    timetableContainer.appendChild(table);
    container.appendChild(timetableContainer);
}
