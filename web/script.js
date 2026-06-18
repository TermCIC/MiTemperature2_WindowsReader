document.getElementById("scanButton").onclick = function () {
  startCountdown(this, 30);
  eel.scan();
};

function startCountdown(button, duration) {
  let t = duration;
  button.disabled = true;
  const tick = setInterval(() => {
    button.textContent = `Scanning... ${t}s`;
    t--;
    if (t < 0) {
      clearInterval(tick);
      button.textContent = "Scan for sensors";
      button.disabled = false;
    }
  }, 1000);
}

function formatTimestamp(epochStr) {
  const d = new Date(parseInt(epochStr, 10) * 1000);
  return d.toLocaleString();
}

function taskStatusClass(status) {
  if (!status) return "";
  const s = status.toLowerCase();
  if (s === "finished") return "finished";
  if (s.includes("fail") || s.includes("error")) return "failed";
  return "running";
}

function latestReading(records) {
  if (!records || Object.keys(records).length === 0) return null;
  const latestKey = Object.keys(records).sort((a, b) => b - a)[0];
  return records[latestKey];
}

function buildReadingsHTML(reading) {
  if (!reading) return '<span class="chip-empty">No readings yet</span>';
  const battery = Math.min(100, Math.max(0, reading.Battery || 0));
  return `
    <span class="chip">${reading.Temperature} °C</span>
    <span class="chip">${reading.Humidity}% RH</span>
    <span class="chip">Battery ${battery.toFixed(0)}%</span>
  `;
}

function buildFetchButton(address, name) {
  const btn = document.createElement("button");
  btn.className = "btn-fetch";
  btn.textContent = "Fetch data";
  btn.onclick = async function () {
    const card = document.getElementById(`sensor-${address}`);
    const feedback = card ? card.querySelector(".card-feedback") : null;
    btn.disabled = true;
    btn.textContent = "Fetching...";
    if (feedback) feedback.textContent = "Connecting to sensor...";
    await eel.fetch_data(address, name);
    if (feedback) feedback.textContent = "Fetch started — see Activity Log for progress.";
    setTimeout(() => {
      btn.disabled = false;
      btn.textContent = "Fetch data";
    }, 3000);
  };
  return btn;
}

function createSensorCard(address, value) {
  const card = document.createElement("div");
  card.className = "sensor-card";
  card.id = `sensor-${address}`;

  const isAvailable = value.status === "Available";
  const latest = latestReading(value.records);

  card.innerHTML = `
    <div class="card-top">
      <div>
        <div class="name-row">
          <input class="name-input" type="text" value="${value.name || "Unknown"}" />
          <button class="btn-name">Save</button>
        </div>
        <div class="sensor-address">${value.address}</div>
      </div>
      <span class="status-badge ${isAvailable ? "badge-available" : "badge-unavailable"}">
        ${value.status || "Unavailable"}
      </span>
    </div>
    <div class="readings-row">${buildReadingsHTML(latest)}</div>
    <div class="fetch-area"></div>
    <div class="card-feedback"></div>
  `;

  const nameInput = card.querySelector(".name-input");
  const saveBtn = card.querySelector(".btn-name");
  const feedback = card.querySelector(".card-feedback");

  saveBtn.onclick = () => {
    const newName = nameInput.value.trim();
    if (newName) {
      eel.change_name(value.address, newName);
      feedback.textContent = `Name saved as "${newName}"`;
      setTimeout(() => { feedback.textContent = ""; }, 3000);
    } else {
      feedback.textContent = "Please enter a valid name.";
    }
  };

  if (isAvailable) {
    card.querySelector(".fetch-area").appendChild(buildFetchButton(address, value.name));
  }

  return card;
}

function updateSensorCard(address, value) {
  const card = document.getElementById(`sensor-${address}`);
  const isAvailable = value.status === "Available";
  const latest = latestReading(value.records);

  if (!card) {
    document.getElementById("sensorContainer").appendChild(createSensorCard(address, value));
    return;
  }

  // Update status badge
  const badge = card.querySelector(".status-badge");
  badge.textContent = value.status || "Unavailable";
  badge.className = "status-badge " + (isAvailable ? "badge-available" : "badge-unavailable");

  // Update readings
  card.querySelector(".readings-row").innerHTML = buildReadingsHTML(latest);

  // Add or remove fetch button based on availability
  const fetchArea = card.querySelector(".fetch-area");
  const existingBtn = fetchArea.querySelector(".btn-fetch");
  if (isAvailable && !existingBtn) {
    fetchArea.appendChild(buildFetchButton(address, value.name));
  } else if (!isAvailable && existingBtn) {
    existingBtn.remove();
  }
}

function update_status() {
  eel.update_status()(function (data) {
    try {
      const parsed = JSON.parse(data);
      const sensors = parsed.sensors;
      const tasks = parsed.tasks;

      for (const [address, value] of Object.entries(sensors)) {
        updateSensorCard(address, value);
      }

      // Rebuild task log: most recent first, capped at 50
      const taskContainer = document.getElementById("taskContainer");
      taskContainer.innerHTML = "";
      const sorted = Object.entries(tasks).sort((a, b) => b[0] - a[0]).slice(0, 50);
      for (const [key, value] of sorted) {
        const entry = document.createElement("div");
        entry.className = `task-entry ${taskStatusClass(value.status)}`;
        entry.innerHTML = `
          <div class="task-time">${formatTimestamp(key)}</div>
          <div class="task-type">${value.task_type}</div>
          <div class="task-status">${value.status || "Unknown"}</div>
        `;
        taskContainer.appendChild(entry);
      }
    } catch (e) {
      console.error("update_status error:", e);
    }
  });
}

window.onload = () => {
  eel.get_version()(v => {
    document.getElementById("appVersion").textContent = `v${v}`;
  });
  setInterval(update_status, 1000);
};
