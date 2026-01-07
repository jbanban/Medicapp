const calendar = document.getElementById("calendar-days");
const daySlots = document.getElementById("day-slots");
const selectedDateEl = document.getElementById("selected-date");

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth();

function loadCalendar() {
  const firstDay = new Date(year, month, 1).getDay();
  const lastDate = new Date(year, month + 1, 0).getDate();

  calendar.innerHTML = "";

  for (let i = 0; i < firstDay; i++) {
    calendar.innerHTML += `<div class="h-20 border"></div>`;
  }

  for (let d = 1; d <= lastDate; d++) {
    const dateStr = `${year}-${month + 1}-${d}`;
    calendar.innerHTML += `
      <div onclick="loadDay('${dateStr}')"
           class="h-20 border p-2 cursor-pointer hover:bg-blue-50">
        ${d}
      </div>
    `;
  }
}

async function loadDay(date) {
    selectedDateEl.innerText = date;
    daySlots.innerHTML = "";

    const res = await fetch(`/api/day/${date}`);
    const slots = await res.json();

    const slotMap = {};
    slots.forEach(s => slotMap[s.time] = s.status);

    for (let h = 9; h <= 17; h++) {
        const time = `${h}:00`;
        const status = slotMap[time];

        let bg = "hover:bg-blue-50";
        let label = "";
        let action = "";

        if (!status) {
        bg = "bg-gray-50";
        action = `
            <button onclick="openSlot('${date}','${time}')"
            class="px-4 py-1 bg-blue-600 text-white rounded text-sm">
            Open
            </button>`;
        }

        if (status === "pending") {
        bg = "bg-yellow-100";
        label = `<span class="text-yellow-700 text-sm">Pending</span>`;
        }

        if (status === "booked") {
        bg = "bg-red-100";
        label = `<span class="text-red-600 text-sm">Booked</span>`;
        }

        daySlots.innerHTML += `
        <div class="flex justify-between items-center border p-3 rounded ${bg}">
            <span>${time}</span>
            ${label || action}
        </div>
        `;
    }
}

async function openSlot(date, time) {
    await fetch("/api/open_slot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, time })
    });

        loadDay(date);
}

async function book(date, time) {
    await fetch("/api/book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, time })
    });

    loadDay(date);
}

loadCalendar();
