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

    const existingClassTableBody = document.querySelector("#existingClassTable tbody");
    const newClassTableBody = document.querySelector("#classTable tbody");
    const addClassBtn = document.getElementById("addClassBtn");
    const submitClassBtn = document.getElementById("submitClassBtn");
    const baseUrl = BE_URL;
    const token = localStorage.getItem("access_token");
    fetchRooms();

    addClassBtn.addEventListener("click", () => {
        addNewClassRow("", "", "");
    });

    submitClassBtn.addEventListener("click", handleSubmitClasses);
    function fetchRooms() {
        const searchContainer = document.querySelector(".search-container");
        const noRoomsMessage = document.getElementById("noRoomsMessage");
        const existingClassTable = document.getElementById("existingClassTable");

        // Clear existing rows
        existingClassTableBody.innerHTML = "";

        // Hide elements initially
        searchContainer.style.display = "none";
        existingClassTable.style.display = "none";
        noRoomsMessage.style.display = "none";

        showLoader();
        fetch(`${baseUrl}/getRooms/`, {
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
            .then((rooms) => {
                if (Array.isArray(rooms)) {
                    if (rooms.length > 0) {
                        rooms.forEach((room) =>
                            addExistingRow(
                                room.id,
                                room.room_code,
                                room.capacity,
                                room.room_type
                            )
                        );
                        searchContainer.style.display = "block";
                        existingClassTable.style.display = "";
                    } else {
                        noRoomsMessage.style.display = "block";
                    }
                } else {
                    noRoomsMessage.style.display = "block";
                }
            })
            .catch((error) => {
                console.error("Error fetching rooms:", error);
                noRoomsMessage.style.display = "block";
                alert("Failed to fetch rooms. Please try again.");
            })
            .finally(() => {
                hideLoader();
            });
    }

    function handleSubmitClasses() {
        const rows = newClassTableBody.querySelectorAll("tr");
        const roomData = [];

        rows.forEach((row) => {
            const data = {
                room_code: row.querySelector(".class-code").value.trim(),
                capacity: row.querySelector(".class-capacity").value.trim(),
                room_type: row.querySelector(".class-type").value.trim(),
            };

            if (validateRoomData(data)) {
                roomData.push(data);
            }
        });

        if (roomData.length > 0) {
            showLoader();
            fetch(`${baseUrl}/addRoom/`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(roomData),
            })
                .then((response) => {
                    if (!response.ok) {
                        return response.json().then((errorData) => {
                            throw errorData;
                        });
                    }
                    return response.json();
                })
                .then((response) => {
                    let successMessage = "Rooms added successfully!";
                    let errorMessage = "";

                    if (response.errors && response.errors.length > 0) {
                        errorMessage =
                            "Failed to add the following rooms due to existing room codes:\n";
                        response.errors.forEach((error) => {
                            errorMessage += `Room code: ${error.room_data.room_code} - ${error.error}\n`;
                        });
                    }

                    if (response.added_rooms && response.added_rooms.length > 0) {
                        successMessage += `\nSuccessfully added the following rooms:\n`;
                        response.added_rooms.forEach((room) => {
                            successMessage += `Room code: ${room.room_code}, Capacity: ${room.capacity}, Type: ${room.room_type}\n`;
                        });
                    }

                    if (errorMessage) {
                        alert(errorMessage);
                    } else {
                        alert(successMessage);
                    }

                    window.location.reload();
                })
                .catch((error) => {
                    console.error("Error adding rooms:", error);
                    if (error && error.errors) {
                        alert(`Error: ${error.errors.map((err) => err.error).join(", ")}`);
                    } else if (error && error.message) {
                        alert(`Error: ${error.message}`);
                    } else {
                        alert("Failed to add rooms. Please try again.");
                    }
                })
                .finally(() => {
                    hideLoader();
                });
        } else {
            alert("Please fill in all required fields before submitting!");
        }
    }

    function validateRoomData(data) {
        if (!data.room_code || !data.capacity || !data.room_type) {
            alert("All fields (room code, capacity, and room type) are required.");
            return false;
        }
        if (isNaN(data.capacity) || parseInt(data.capacity) <= 0) {
            alert("Capacity must be a valid positive number.");
            return false;
        }
        return true;
    }

    function addExistingRow(id, code, capacity, type) {
        const row = document.createElement("tr");
        row.dataset.rowId = id;

        row.innerHTML = `
        <td><input type="text" value="${code}" disabled></td>
        <td><input type="number" min="0" value="${capacity}" disabled></td>
        <td>
          <select disabled>
            ${generateRoomTypeOptions(type)}
          </select>
        </td>
        <td>
          <button class="edit-btn" title="Edit"><i class="fas fa-edit"></i></button>
          <button class="delete-btn" title="Delete"><i class="fas fa-trash-alt"></i></button>
        </td>
        `;

        const editBtn = row.querySelector(".edit-btn");
        const deleteBtn = row.querySelector(".delete-btn");
        const inputs = row.querySelectorAll("input, select");

        editBtn.addEventListener("click", () => handleEditRow(editBtn, inputs, id));
        deleteBtn.addEventListener("click", () => handleDeleteRow(row, id));

        existingClassTableBody.appendChild(row);
    }

    function handleEditRow(editBtn, inputs, rowId) {
        const icon = editBtn.querySelector("i");
        if (icon.classList.contains("fa-edit")) {
            inputs.forEach((input) => (input.disabled = false));
            icon.classList.remove("fa-edit");
            icon.classList.add("fa-save");
            editBtn.title = "Save";
        } else {
            const data = {
                room_code: inputs[0].value.trim(),
                capacity: inputs[1].value.trim(),
                room_type: inputs[2].value.trim(),
            };

            if (!validateRoomData(data)) {
                inputs.forEach((input) => (input.disabled = false));
                return;
            }

            showLoader();
            fetch(`${baseUrl}/updateRoom/${rowId}/`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`,
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
                .then((updatedData) => {
                    alert("Room updated successfully!");
                    icon.classList.remove("fa-save");
                    icon.classList.add("fa-edit");
                    editBtn.title = "Edit";
                    inputs.forEach((input) => (input.disabled = true));
                })
                .catch((error) => {
                    console.error("Error updating room:", error);
                    alert(error.message || "Failed to update room details.");
                })
                .finally(() => {
                    hideLoader();
                });
        }
    }

    function handleDeleteRow(row, rowId) {
        if (confirm("Are you sure you want to delete this room?")) {
            showLoader();
            fetch(`${baseUrl}/deleteRoom/${rowId}/`, {
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
                .then(() => {
                    row.remove();
                    alert("Room deleted successfully!");

                    // Check if this was the last room
                    const remainingRows = existingClassTableBody.querySelectorAll("tr");
                    if (remainingRows.length === 0) {
                        window.location.reload();
                    }
                })
                .catch((error) => {
                    console.error("Error deleting room:", error);
                    alert("Failed to delete room. Please try again.");
                })
                .finally(() => {
                    hideLoader();
                });
        }
    }

    function addNewClassRow(code, capacity, type) {
        const row = document.createElement("tr");

        row.innerHTML = `
        <td><input type="text" class="class-code" value="${code}" placeholder="Enter Room Code"></td>
        <td><input type="number" min="0" class="class-capacity" value="${capacity}" placeholder="Enter Room Capacity"></td>
        <td>
          <select class="class-type">
            ${generateRoomTypeOptions(type)}
          </select>
        </td>
        <td>
          <button class="delete-btn" title="Delete"><i class="fas fa-trash-alt"></i></button>
        </td>
        `;

        const deleteBtn = row.querySelector(".delete-btn");
        deleteBtn.addEventListener("click", () => {
            if (confirm("Are you sure you want to delete this entry?")) {
                row.remove();
            }
        });

        newClassTableBody.appendChild(row);
    }

    function generateRoomTypeOptions(selectedType) {
        const roomTypes = ["Lecture Theatre", "Class Room", "Lab", "Seminar Hall"];
        return roomTypes
            .map(
                (type) =>
                    `<option value="${type}" ${type === selectedType ? "selected" : ""
                    }>${type}</option>`
            )
            .join("");
    }

    // Add search functionality
    const classSearch = document.getElementById("classSearch");
    classSearch.addEventListener("input", (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = existingClassTableBody.querySelectorAll("tr");

        rows.forEach((row) => {
            const code = row
                .querySelector("td:first-child input")
                .value.toLowerCase();
            const capacity = row
                .querySelector("td:nth-child(2) input")
                .value.toLowerCase();
            const type = row
                .querySelector("td:nth-child(3) select")
                .value.toLowerCase();

            if (
                code.includes(searchTerm) ||
                capacity.includes(searchTerm) ||
                type.includes(searchTerm)
            ) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });
});
