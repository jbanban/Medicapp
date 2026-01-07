const app = document.getElementById("calendar");

let currentDate = new Date();
let selectedDate = null;
let showScheduler = false;
let schedulerView = "week";

let duration = 60;
let appointmentTitle = "";

const availability = {
  sunday: { available: false },
  monday: { start: "09:00", end: "17:00", available: true },
  tuesday: { start: "09:00", end: "17:00", available: true },
  wednesday: { start: "09:00", end: "17:00", available: true },
  thursday: { start: "09:00", end: "17:00", available: true },
  friday: { start: "09:00", end: "17:00", available: true },
  saturday: { available: false }
};

const DAYS = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
const monthNames = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December"
];

function getDaysInMonth(date) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const lastDate = new Date(year, month + 1, 0).getDate();
  return { firstDay, lastDate };
}

function renderCalendarDays() {
  const { firstDay, lastDate } = getDaysInMonth(currentDate);
  const today = new Date();

  let html = "";

  for (let i = 0; i < firstDay; i++) {
    html += `<div class="h-32 border border-gray-200 bg-gray-50"></div>`;
  }

  for (let d = 1; d <= lastDate; d++) {
    const isToday =
      d === today.getDate() &&
      currentDate.getMonth() === today.getMonth() &&
      currentDate.getFullYear() === today.getFullYear();

    html += `
      <div onclick="openScheduler(${d})"
           class="h-32 border border-gray-200 p-2 cursor-pointer hover:bg-blue-50">
        <span class="${isToday ? "bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center" : ""}">
          ${d}
        </span>
      </div>
    `;
  }

  return html;
}

function openScheduler(day) {
  selectedDate = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth(),
    day
  );
  showScheduler = true;
  schedulerView = "week";
  render();
}

function render() {
  app.innerHTML = `
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 px-6 py-4 flex justify-between">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <div class="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white">
            <i data-lucide="calendar"></i>
          </div>
          <span class="text-xl font-medium text-gray-700">Calendar</span>
        </div>

        <button onclick="goToday()"
          class="px-5 py-2 border border-gray-300 rounded-full text-sm hover:bg-gray-50">
          Today
        </button>

        <div class="flex">
          <button onclick="prevMonth()" class="p-2 hover:bg-gray-100 rounded-full">
            <i data-lucide="chevron-left"></i>
          </button>
          <button onclick="nextMonth()" class="p-2 hover:bg-gray-100 rounded-full">
            <i data-lucide="chevron-right"></i>
          </button>
        </div>

        <h1 class="text-xl text-gray-700">
          ${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}
        </h1>
      </div>

      <div class="flex gap-2">
        <button class="p-2 hover:bg-gray-100 rounded-full"><i data-lucide="search"></i></button>
        <button class="p-2 hover:bg-gray-100 rounded-full"><i data-lucide="help-circle"></i></button>
        <button class="p-2 hover:bg-gray-100 rounded-full"><i data-lucide="settings"></i></button>
      </div>
    </header>

    <!-- Calendar -->
    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="grid grid-cols-7 border-b border-gray-200">
          ${DAYS.map(d => `
            <div class="text-center text-xs font-medium text-gray-600 p-2 border-r">
              ${d}
            </div>`).join("")}
        </div>

        <div class="grid grid-cols-7">
          ${renderCalendarDays()}
        </div>
      </div>
    </main>

    <!-- Scheduler Modal -->
    ${showScheduler ? renderSchedulerModal() : ""}
  `;

  lucide.createIcons();
}

function renderSchedulerModal() {
  return `
    <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white w-full max-w-6xl h-[90vh] rounded-lg flex overflow-hidden">

        <!-- Sidebar -->
        <div class="w-[440px] border-r flex flex-col">
          <div class="flex justify-between items-center px-6 py-4 border-b">
            <div class="flex gap-2">
              <button onclick="schedulerView='config';render()"
                class="px-3 py-1.5 rounded text-sm ${schedulerView==="config"?"bg-blue-100 text-blue-700":"hover:bg-gray-100"}">
                Configure
              </button>
              <button onclick="schedulerView='week';render()"
                class="px-3 py-1.5 rounded text-sm ${schedulerView==="week"?"bg-blue-100 text-blue-700":"hover:bg-gray-100"}">
                Week View
              </button>
            </div>

            <button onclick="closeScheduler()" class="p-2 hover:bg-gray-100 rounded">
              <i data-lucide="x"></i>
            </button>
          </div>

          <div class="flex-1 p-6 text-center text-gray-500">
            <i data-lucide="calendar" class="w-12 h-12 mx-auto mb-3"></i>
            <p class="text-sm">
              Selected: ${selectedDate.toDateString()}
            </p>
            <p class="text-xs mt-2">
              Click on available time slots to book
            </p>
          </div>

          <div class="px-6 py-4 border-t flex justify-between">
            <button onclick="closeScheduler()"
              class="px-6 py-2 border rounded hover:bg-gray-50">
              Close
            </button>
            <button class="px-8 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Save
            </button>
          </div>
        </div>

        <!-- Week View Placeholder -->
        <div class="flex-1 flex items-center justify-center text-gray-400">
          Week View (same layout logic as React version)
        </div>
      </div>
    </div>
  `;
}

function closeScheduler() {
  showScheduler = false;
  render();
}

function prevMonth() {
  currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1);
  render();
}

function nextMonth() {
  currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1);
  render();
}

function goToday() {
  currentDate = new Date();
  render();
}

render();
