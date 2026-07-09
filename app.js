import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup, GoogleAuthProvider, updateProfile } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-analytics.js";

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

    // -----------------------------------------------------------
    // Firebase client initialization (replace with your config)
    // -----------------------------------------------------------
    const firebaseConfig = {
        apiKey: "AIzaSyCdoCYIGKXLcJxW6hp6qz9_2tBcMk3NVIE",
        authDomain: "app-cloud-11d89.firebaseapp.com",
        projectId: "app-cloud-11d89",
        storageBucket: "app-cloud-11d89.firebasestorage.app",
        messagingSenderId: "815663475397",
        appId: "1:815663475397:web:87452f7b31d237d38a9eac",
        measurementId: "G-V91QWH3XPS"
    };

    const firebaseApp = initializeApp(firebaseConfig);
    try { getAnalytics(firebaseApp); } catch (e) { /* analytics may fail in non-browser env */ }
    const auth = getAuth(firebaseApp);

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
            form.addEventListener("submit", async (e) => {
                e.preventDefault();
                const id = form.id;
                const email = form.querySelector('input[type="email"]')?.value?.trim();
                const pass = form.querySelector('input[type="password"]')?.value || '';

                if (!email || !pass) return alert('Provide email and password.');

                if (id === 'form-login') {
                    // Sign in (modular API)
                    try {
                        const userCred = await signInWithEmailAndPassword(auth, email, pass);
                        const token = await userCred.user.getIdToken();
                        localStorage.setItem('eduIdToken', token);
                        window.location.href = '/dashboard';
                    } catch (err) {
                        alert('Sign-in failed: ' + (err.message || err));
                        console.error(err);
                    }
                } else if (id === 'form-register') {
                    // Register (modular API)
                    try {
                        const displayName = form.querySelector('#reg-name')?.value || '';
                        const userCred = await createUserWithEmailAndPassword(auth, email, pass);
                        if (displayName) await updateProfile(userCred.user, { displayName });
                        const token = await userCred.user.getIdToken();
                        localStorage.setItem('eduIdToken', token);
                        window.location.href = '/dashboard';
                    } catch (err) {
                        alert('Registration failed: ' + (err.message || err));
                        console.error(err);
                    }
                }
            });
        });

        // Google sign-in button
        const googleBtn = document.getElementById('google-signin');
        if (googleBtn) {
            googleBtn.addEventListener('click', async () => {
                const provider = new GoogleAuthProvider();
                try {
                    const result = await signInWithPopup(auth, provider);
                    const token = await result.user.getIdToken();
                    localStorage.setItem('eduIdToken', token);
                    window.location.href = '/dashboard';
                } catch (err) {
                    alert('Google sign-in failed: ' + (err.message || err));
                    console.error(err);
                }
            });
        }
    }

    /* -----------------------------------------------------------
       3. DASHBOARD TAB SWITCHING
    ----------------------------------------------------------- */
    const tabBtns = document.querySelectorAll(".tab-btn[data-tab]");
    const tabPanes = document.querySelectorAll(".tab-pane");

    function activateTab(targetId) {
        if (!targetId) return;

        tabBtns.forEach(btn => btn.classList.toggle("active", btn.getAttribute("data-tab") === targetId));
        tabPanes.forEach(pane => {
            const isActive = pane.id === targetId;
            pane.classList.toggle("hidden", !isActive);
            pane.classList.toggle("fade-in", isActive);
        });

        if (window.location.pathname === "/dashboard") {
            history.replaceState(null, "", `#${targetId}`);
        }
    }

    if (tabBtns.length > 0 && tabPanes.length > 0) {
        const initialTarget = window.location.hash.replace("#", "") || "tab-tasks";
        const requestedPane = document.getElementById(initialTarget);

        if (requestedPane) {
            activateTab(initialTarget);
        } else {
            activateTab("tab-tasks");
        }

        tabBtns.forEach(btn => {
            btn.addEventListener("click", (event) => {
                const targetId = btn.getAttribute("data-tab");
                if (!targetId) return;

                event.preventDefault();
                activateTab(targetId);
            });
        });
    }

    /* -----------------------------------------------------------
       4. K-12 MATH QUESTION GENERATOR (API Integration)
    ----------------------------------------------------------- */
    const generateMathBtn = document.getElementById("generate-math-btn");
    const mathResults = document.getElementById("math-results");
    const savedQuestionsList = document.getElementById("saved-questions-list");
    const reviewQuestionsList = document.getElementById("review-questions-list");
    const gradeSelect = document.getElementById("grade-select");
    const topicSelect = document.getElementById("topic-select");

    const gradeTopicMap = {
        k: ["mixed", "arithmetic", "counting", "shapes"],
        1: ["mixed", "arithmetic", "counting", "shapes"],
        2: ["mixed", "arithmetic", "counting", "shapes"],
        3: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "geometry"],
        4: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "geometry"],
        5: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "geometry"],
        6: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "algebra", "geometry", "probability", "statistics", "exponents", "ratios"],
        7: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "algebra", "geometry", "probability", "statistics", "exponents", "ratios"],
        8: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "algebra", "geometry", "probability", "statistics", "exponents", "ratios"],
        9: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "algebra", "geometry", "probability", "statistics", "exponents", "ratios", "functions", "sequences", "inequalities", "trigonometry", "calculus"],
        10: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "algebra", "geometry", "probability", "statistics", "exponents", "ratios", "functions", "sequences", "inequalities", "trigonometry", "calculus"],
        11: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "algebra", "geometry", "probability", "statistics", "exponents", "ratios", "functions", "sequences", "inequalities", "trigonometry", "calculus"],
        12: ["mixed", "arithmetic", "fractions", "percentages", "word-problems", "algebra", "geometry", "probability", "statistics", "exponents", "ratios", "functions", "sequences", "inequalities", "trigonometry", "calculus"]
    };

    function updateTopicOptions() {
        if (!topicSelect || !gradeSelect) return;

        const allowedTopics = gradeTopicMap[gradeSelect.value] || gradeTopicMap[12];
        Array.from(topicSelect.options).forEach(option => {
            const isAllowed = allowedTopics.includes(option.value);
            option.hidden = !isAllowed;
            option.disabled = !isAllowed;
        });

        if (!allowedTopics.includes(topicSelect.value)) {
            topicSelect.value = "mixed";
        }
    }

    if (gradeSelect && topicSelect) {
        updateTopicOptions();
        gradeSelect.addEventListener("change", updateTopicOptions);
    }

    if (generateMathBtn && mathResults) {
        let practiceQueue = JSON.parse(localStorage.getItem("eduMathPractice")) || { saved: [], review: [] };

        function savePracticeState() {
            localStorage.setItem("eduMathPractice", JSON.stringify(practiceQueue));
        }

        function normalizeAnswer(value) {
            return value.trim().toLowerCase().replace(/^x\s*=\s*/, "").replace(/^answer\s*[:=]\s*/, "").replace(/\s+/g, "");
        }

        function addPracticeItem(question, bucket) {
            const entry = {
                id: question.id,
                question: question.question,
                answer: question.answer,
                topic: question.topic,
                type: question.type
            };

            const existing = practiceQueue[bucket].some(item => item.id === entry.id);
            if (!existing) {
                practiceQueue[bucket].push(entry);
                savePracticeState();
            }
        }

        function renderPracticeQueue() {
            if (savedQuestionsList) {
                savedQuestionsList.innerHTML = practiceQueue.saved.length
                    ? practiceQueue.saved.map(item => `
                        <li class="practice-item">
                            <p><strong>${item.topic}</strong><br>${item.question}</p>
                            <button class="btn btn-outline btn-small" onclick="this.closest('li').remove(); const current=JSON.parse(localStorage.getItem('eduMathPractice')||'{"saved":[],"review":[]}'); current.saved=current.saved.filter(entry=>entry.id!=='${item.id}'); localStorage.setItem('eduMathPractice', JSON.stringify(current));">Remove</button>
                        </li>
                    `).join("")
                    : '<li class="practice-empty">Nothing saved yet.</li>';
            }

            if (reviewQuestionsList) {
                reviewQuestionsList.innerHTML = practiceQueue.review.length
                    ? practiceQueue.review.map(item => `
                        <li class="practice-item">
                            <p><strong>${item.topic}</strong><br>${item.question}</p>
                            <button class="btn btn-outline btn-small" onclick="this.closest('li').remove(); const current=JSON.parse(localStorage.getItem('eduMathPractice')||'{"saved":[],"review":[]}'); current.review=current.review.filter(entry=>entry.id!=='${item.id}'); localStorage.setItem('eduMathPractice', JSON.stringify(current));">Remove</button>
                        </li>
                    `).join("")
                    : '<li class="practice-empty">No missed questions yet.</li>';
            }
        }

        generateMathBtn.addEventListener("click", async () => {
            const grade = document.getElementById("grade-select").value;
            const count = document.getElementById("q-count").value;
            const topic = document.getElementById("topic-select").value;
            const questionType = document.getElementById("question-type-select").value;

            mathResults.innerHTML = "<p style='color:var(--text-muted);'>Generating practice problems...</p>";

            try {
                const response = await fetch("/api/generate-math", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ grade, count, topic, questionType })
                });
                const data = await response.json();

                if (data.status === "success") {
                    mathResults.innerHTML = "";
                    data.questions.forEach((q, index) => {
                        const div = document.createElement("div");
                        div.className = "q-item math-question-card fade-in";
                        div.innerHTML = `
                            <div class="math-question-block">
                                <div class="question-meta">
                                    <span class="topic-pill">${q.topic}</span>
                                    <span class="question-type-pill">${q.type === "multiple-choice" ? "Multiple choice" : q.type === "true-false" ? "True / False" : q.type === "fill-in-the-blank" ? "Fill in the blank" : q.type === "multiple-select" ? "Multiple select" : q.type === "ordering" ? "Ordering" : "Type answer"}</span>
                                    <span class="question-type-pill">${q.difficulty || "Mixed"}</span>
                                </div>
                                <div><strong>Q${index + 1}:</strong> ${q.question}</div>
                                <div class="answer-options"></div>
                                <input class="answer-input hidden" type="text" placeholder="Type your answer here">
                                <div class="answer-feedback"></div>
                            </div>
                            <div class="question-actions">
                                <button class="btn btn-outline btn-small save-practice-btn">Save for Practice</button>
                                <button class="btn btn-primary btn-small check-answer-btn">Check Answer</button>
                            </div>
                        `;

                        const optionsContainer = div.querySelector(".answer-options");
                        const answerInput = div.querySelector(".answer-input");
                        const feedback = div.querySelector(".answer-feedback");
                        const saveButton = div.querySelector(".save-practice-btn");
                        const checkButton = div.querySelector(".check-answer-btn");

                        if ((q.type === "multiple-choice" || q.type === "true-false" || q.type === "multiple-select") && q.choices) {
                            answerInput.classList.add("hidden");
                            q.choices.forEach(choice => {
                                const choiceBtn = document.createElement("button");
                                choiceBtn.type = "button";
                                choiceBtn.className = "choice-btn";
                                choiceBtn.textContent = choice;
                                choiceBtn.addEventListener("click", () => {
                                    if (q.type === "multiple-select") {
                                        choiceBtn.classList.toggle("selected");
                                        choiceBtn.dataset.selected = choiceBtn.classList.contains("selected") ? "true" : "false";
                                    } else {
                                        div.querySelectorAll(".choice-btn").forEach(btn => btn.classList.remove("selected"));
                                        choiceBtn.classList.add("selected");
                                        choiceBtn.dataset.selected = "true";
                                    }
                                });
                                optionsContainer.appendChild(choiceBtn);
                            });
                        } else {
                            optionsContainer.classList.add("hidden");
                            answerInput.classList.remove("hidden");
                        }

                        saveButton.addEventListener("click", () => {
                            addPracticeItem(q, "saved");
                            renderPracticeQueue();
                            feedback.className = "answer-feedback correct";
                            feedback.textContent = "Saved for practice.";
                        });

                        checkButton.addEventListener("click", () => {
                            let userAnswer = "";

                            if (q.type === "multiple-choice" || q.type === "true-false") {
                                const selected = div.querySelector(".choice-btn.selected");
                                userAnswer = selected ? selected.textContent : "";
                            } else if (q.type === "multiple-select") {
                                userAnswer = Array.from(div.querySelectorAll(".choice-btn.selected"))
                                    .map(btn => btn.textContent.trim())
                                    .join(",");
                            } else {
                                userAnswer = answerInput.value;
                            }

                            if (!userAnswer.trim()) {
                                feedback.className = "answer-feedback incorrect";
                                feedback.textContent = "Choose or type an answer first.";
                                return;
                            }

                            const isCorrect = normalizeAnswer(userAnswer) === normalizeAnswer(q.answer);
                            if (isCorrect) {
                                feedback.className = "answer-feedback correct";
                                feedback.textContent = `Correct! ${q.explanation}`;
                            } else {
                                feedback.className = "answer-feedback incorrect";
                                feedback.textContent = `Not quite. The correct answer is ${q.answer}. ${q.explanation}`;
                                addPracticeItem(q, "review");
                                renderPracticeQueue();
                            }
                        });

                        mathResults.appendChild(div);
                    });
                }
            } catch (error) {
                mathResults.innerHTML = "<p style='color:#ef4444;'>Failed to communicate with Flask backend.</p>";
                console.error(error);
            }
        });

        renderPracticeQueue();
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