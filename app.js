document.addEventListener("DOMContentLoaded", () => {
    /* -----------------------------------------------------------
       1. THEME TOGGLE (Dark / Light Mode Support)
    ----------------------------------------------------------- */
    const themeToggles = document.querySelectorAll(".theme-toggle");
    
    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("eduTheme", theme);
        
        // Toggle SVG sun/moon icons
        document.querySelectorAll(".sun-icon").forEach(icon => {
            icon.classList.toggle("hidden", theme === "dark");
        });
        document.querySelectorAll(".moon-icon").forEach(icon => {
            icon.classList.toggle("hidden", theme === "light");
        });
    }

    // Initialize saved or preferred theme
    const savedTheme = localStorage.getItem("eduTheme") || 
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    setTheme(savedTheme);

    themeToggles.forEach(btn => {
        btn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme");
            setTheme(current === "dark" ? "light" : "dark");
        });
    });

    /* -----------------------------------------------------------
       2. LOGIN PAGE & AUTHENTICATION TABS
    ----------------------------------------------------------- */
    const authTabs = document.querySelectorAll(".auth-tab");
    const authForms = document.querySelectorAll(".auth-form");

    if (authTabs.length > 0) {
        authTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                authTabs.forEach(t => t.classList.remove("active"));
                authForms.forEach(f => f.classList.add("hidden"));

                tab.classList.add("active");
                const targetId = tab.getAttribute("data-target");
                document.getElementById(targetId).classList.remove("hidden");
            });
        });

        authForms.forEach(form => {
            form.addEventListener("submit", (e) => {
                e.preventDefault();
                // Redirect straight to dashboard page upon form submission
                window.location.href = "/dashboard";
            });
        });
    }

    /* -----------------------------------------------------------
       3. DASHBOARD TAB SWITCHING
    ----------------------------------------------------------- */
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                tabBtns.forEach(b => b.classList.remove("active"));
                tabPanes.forEach(p => p.classList.add("hidden"));

                btn.classList.add("active");
                const targetId = btn.getAttribute("data-tab");
                const activePane = document.getElementById(targetId);
                activePane.classList.remove("hidden");
                activePane.classList.add("fade-in");
            });
        });
    }

    /* -----------------------------------------------------------
       4. K-12 MATH QUESTION GENERATOR (API Integration)
    ----------------------------------------------------------- */
    const generateMathBtn = document.getElementById("generate-math-btn");
    const mathResults = document.getElementById("math-results");

    if (generateMathBtn) {
        generateMathBtn.addEventListener("click", async () => {
            const grade = document.getElementById("grade-select").value;
            const count = document.getElementById("q-count").value;

            mathResults.innerHTML = "<p style='color:var(--text-muted);'>Generating practice problems...</p>";

            try {
                const response = await fetch("/api/generate-math", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ grade, count })
                });
                const data = await response.json();

                if (data.status === "success") {
                    mathResults.innerHTML = "";
                    data.questions.forEach((q, index) => {
                        const div = document.createElement("div");
                        div.className = "q-item fade-in";
                        div.innerHTML = `
                            <div><strong>Q${index + 1}:</strong> ${q.question}</div>
                            <button class="btn btn-outline btn-small" onclick="alert('Solution: ${q.answer}')">View Solution</button>
                        `;
                        mathResults.appendChild(div);
                    });
                }
            } catch (error) {
                mathResults.innerHTML = "<p style='color:#ef4444;'>Failed to communicate with Flask backend.</p>";
                console.error(error);
            }
        });
    }

    /* -----------------------------------------------------------
       5. TEXT QUESTION IMPORTER (API Integration)
    ----------------------------------------------------------- */
    const importBtn = document.getElementById("import-btn");
    const importResults = document.getElementById("import-results");

    if (importBtn) {
        importBtn.addEventListener("click", async () => {
            const text = document.getElementById("import-textarea").value;
            if (!text.trim()) return alert("Please input or paste worksheet text first.");

            importResults.innerHTML = "<p style='color:var(--text-muted);'>Parsing questions...</p>";

            try {
                const response = await fetch("/api/import-questions", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text })
                });
                const data = await response.json();

                if (data.status === "success") {
                    importResults.innerHTML = "";
                    data.imported.forEach((item, index) => {
                        const div = document.createElement("div");
                        div.className = "q-item fade-in";
                        div.innerHTML = `
                            <div><strong>Import ${index + 1}:</strong> ${item.question}</div>
                            <span style="color: #10b981; font-weight: 600; font-size:0.85rem;">✔ ${item.status}</span>
                        `;
                        importResults.appendChild(div);
                    });
                }
            } catch (error) {
                importResults.innerHTML = "<p style='color:#ef4444;'>Error parsing text payload.</p>";
                console.error(error);
            }
        });
    }

    /* -----------------------------------------------------------
       6. DAILY TASKS (LocalStorage Management)
    ----------------------------------------------------------- */
    const taskInput = document.getElementById("new-task-input");
    const addTaskBtn = document.getElementById("add-task-btn");
    const taskList = document.getElementById("task-list");

    if (taskList) {
        let tasks = JSON.parse(localStorage.getItem("eduTasks")) || [
            { text: "Grade K-2 Math Worksheets", completed: false },
            { text: "Review Lesson Plan for Algebra", completed: true }
        ];

        function renderTasks() {
            taskList.innerHTML = "";
            tasks.forEach((task, index) => {
                const li = document.createElement("li");
                li.className = `task-item fade-in ${task.completed ? "completed" : ""}`;
                li.innerHTML = `
                    <span onclick="toggleTask(${index})" style="cursor:pointer; flex:1; display:flex; align-items:center; gap:10px;">
                        <input type="checkbox" ${task.completed ? "checked" : ""} readOnly style="width:16px; height:16px; cursor:pointer;">
                        ${task.text}
                    </span>
                    <button class="btn btn-outline btn-small" onclick="deleteTask(${index})">Remove</button>
                `;
                taskList.appendChild(li);
            });
            localStorage.setItem("eduTasks", JSON.stringify(tasks));
        }

        if (addTaskBtn) {
            addTaskBtn.addEventListener("click", () => {
                if (taskInput.value.trim()) {
                    tasks.push({ text: taskInput.value.trim(), completed: false });
                    taskInput.value = "";
                    renderTasks();
                }
            });
        }

        window.toggleTask = (index) => {
            tasks[index].completed = !tasks[index].completed;
            renderTasks();
        };

        window.deleteTask = (index) => {
            tasks.splice(index, 1);
            renderTasks();
        };

        renderTasks();
    }

    /* -----------------------------------------------------------
       7. STUDY & FOCUS TIMER (Pomodoro Engine)
    ----------------------------------------------------------- */
    const timerDisplay = document.getElementById("timer-display");
    const timerLabel = document.getElementById("timer-label");

    if (timerDisplay) {
        let timerInterval = null;
        let timeRemaining = 25 * 60;

        function updateTimerDisplay() {
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        document.getElementById("timer-start").addEventListener("click", () => {
            if (!timerInterval) {
                timerInterval = setInterval(() => {
                    if (timeRemaining > 0) {
                        timeRemaining--;
                        updateTimerDisplay();
                    } else {
                        clearInterval(timerInterval);
                        timerInterval = null;
                        alert("Timer Complete! Step away and take a well-deserved break.");
                    }
                }, 1000);
            }
        });

        document.getElementById("timer-pause").addEventListener("click", () => {
            clearInterval(timerInterval);
            timerInterval = null;
        });

        document.getElementById("timer-reset").addEventListener("click", () => {
            clearInterval(timerInterval);
            timerInterval = null;
            timeRemaining = 25 * 60;
            if (timerLabel) timerLabel.textContent = "Pomodoro Focus";
            updateTimerDisplay();
        });

        document.getElementById("timer-short").addEventListener("click", () => {
            clearInterval(timerInterval);
            timerInterval = null;
            timeRemaining = 5 * 60;
            if (timerLabel) timerLabel.textContent = "Short Break";
            updateTimerDisplay();
        });
    }

    /* -----------------------------------------------------------
       8. GOOGLE CALENDAR PLACEHOLDER
    ----------------------------------------------------------- */
    const gcalBtn = document.getElementById("gcal-connect-btn");
    if (gcalBtn) {
        gcalBtn.addEventListener("click", () => {
            alert("Google Calendar OAuth Initialized!\n\nTo run this in production, insert your Google Cloud Client ID into the OAuth config to sync scheduled tasks automatically.");
        });
    }
});