document.querySelector("button").onclick = function () {
  const scanButton = this; // Reference to the button element
  const countdownDuration = 30; // Countdown duration in seconds

  // Start the countdown
  startCountdown(scanButton, countdownDuration);

  // Call the eel function to start scanning
  eel.scan();
};

function startCountdown(button, duration) {
  let remainingTime = duration;
  button.disabled = true; // Disable the button during the countdown
  button.style.backgroundColor = "darkgray"; // Change button appearance

  const timer = setInterval(() => {
    button.textContent = `Syncing... ${remainingTime} seconds`; // Update button text
    remainingTime--;

    if (remainingTime < 0) {
      clearInterval(timer); // Stop the timer
      button.textContent = "Scan sensors"; // Reset button text
      button.disabled = false; // Re-enable the button
      button.style.backgroundColor = "green"; // Reset button appearance
    }
  }, 1000); // Update every second
}


function update_status() {
  eel.update_status()(function (data) {
    console.log("Raw Data Received from Python:", data); // Log raw data for debugging

    try {
      // Parse the combined data
      const parsedData = JSON.parse(data);
      const sensors = parsedData.sensors; // Sensor data (JSON string)
      const tasks = parsedData.tasks;    // Task data (JSON string)

      // Get the containers for sensors and tasks
      const sensorContainer = document.getElementById("sensorContainer");
      const taskContainer = document.getElementById("taskContainer");

      // Clear existing content in the task container
      taskContainer.innerHTML = "";

      // Parse and display sensor data
      const sensorData = JSON.parse(sensors);
      for (const [key, value] of Object.entries(sensorData)) {
        // Check if a box for this key already exists
        if (document.getElementById(`sensor-${key}`)) {
          console.log(`Sensor with key ${key} already exists. Skipping.`);
          continue; // Skip adding a duplicate box
        }

        const sensorDiv = document.createElement("div");
        sensorDiv.className = "sensor-box"; // Use class for styling
        sensorDiv.id = `sensor-${key}`; // Assign a unique ID based on the key
        sensorDiv.style.display = "flex";
        sensorDiv.style.justifyContent = "space-between";
        sensorDiv.style.alignItems = "center";
        sensorDiv.style.border = "1px solid #ccc";
        sensorDiv.style.borderRadius = "5px";
        sensorDiv.style.padding = "10px";
        sensorDiv.style.marginBottom = "10px";

        // Left section: Sensor name and update button
        const leftSection = document.createElement("div");
        leftSection.style.display = "flex";
        leftSection.style.flexDirection = "column";
        leftSection.style.alignItems = "flex-start";

        // Static label: "Sensor name"
        const label = document.createElement("strong");
        label.textContent = "Sensor name";
        label.style.marginBottom = "5px";

        // Create input box for the device name
        const nameInput = document.createElement("input");
        nameInput.type = "text";
        nameInput.value = value.name || "Unknown"; // Pre-fill with the current name or "Unknown"
        nameInput.style.width = "200px";
        nameInput.style.marginBottom = "5px";
        nameInput.style.padding = "5px";

        // Create "Update sensor name" button
        const updateNameButton = document.createElement("button");
        updateNameButton.textContent = "Update sensor name";
        updateNameButton.style.padding = "5px 10px";
        updateNameButton.style.fontSize = "16px";
        updateNameButton.style.cursor = "pointer";

        // Add click handler with popup for updating name
        updateNameButton.onclick = function () {
          const newName = nameInput.value.trim();
          if (newName) {
            eel.change_name(value.address, newName); // Call eel function with address and new name
            alert(`Your sensor name has been changed to: ${newName}`);
          } else {
            alert("Please enter a valid name.");
          }
        };

        leftSection.appendChild(label);
        leftSection.appendChild(nameInput);
        leftSection.appendChild(updateNameButton);

        // Right section: Other sensor information and Fetch data button
        const rightSection = document.createElement("div");
        rightSection.style.textAlign = "left";

        // Sensor information
        const sensorInfo = `
          <strong>Key:</strong> ${key}<br>
          <strong>Address:</strong> ${value.address}<br>
          <strong>Status:</strong> ${value.status || "Unavailable"}
        `;
        rightSection.innerHTML = sensorInfo;

        // Add "Fetch data" button for available sensors
        if (value.status === "Available") {
          const fetchButton = document.createElement("button");
          fetchButton.textContent = "Fetch data";
          fetchButton.style.padding = "5px 10px";
          fetchButton.style.fontSize = "16px";
          fetchButton.style.cursor = "pointer";
          fetchButton.style.marginTop = "10px";

          // Add click handler with popup for fetching data
          fetchButton.onclick = async function () {
            await eel.fetch_data(value.address, value.name); // Call eel function with address and name
            alert(`Started fetching data for: ${value.name || "Unknown"}`);
          };

          rightSection.appendChild(fetchButton);
        }

        // Append both sections to the sensor box
        sensorDiv.appendChild(leftSection);
        sensorDiv.appendChild(rightSection);

        sensorContainer.appendChild(sensorDiv);
      }

      // Parse and display task data
      const taskData = JSON.parse(tasks);
      for (const [key, value] of Object.entries(taskData)) {
        const taskDiv = document.createElement("div");
        taskDiv.className = "task-box"; // Use class for styling
        taskDiv.style.border = "1px solid #ccc";
        taskDiv.style.borderRadius = "5px";
        taskDiv.style.padding = "10px";
        taskDiv.style.marginBottom = "10px";

        // Construct HTML content for the task
        const taskInfo = `
          <strong>Task:</strong> ${key}<br>
          <strong>Type:</strong> ${value.task_type}<br>
          <strong>Status:</strong> ${value.status || "Unknown"}
        `;
        taskDiv.innerHTML = taskInfo;
        taskContainer.appendChild(taskDiv);
      }

      // Automatically scroll to the bottom of the status messages container
      taskContainer.scrollTop = taskContainer.scrollHeight;
    } catch (error) {
      console.error("Error parsing or displaying data:", error);
    }
  });
}


// Automatically start fetching sensor data when the page loads
window.onload = function () {
    // Start periodically fetching sensor data
    setInterval(update_status, 1000); // Fetch sensor data every second
  };