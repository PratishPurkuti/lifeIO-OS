document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();

    // Modal Handling
    const modal = document.getElementById('add-entry-modal');
    const openBtn = document.getElementById('open-entry-modal');
    const closeBtn = document.getElementById('close-entry-modal');

    if (openBtn) {
        openBtn.onclick = () => {
            modal.classList.remove('hidden');
            prefillDates();
        };
    }

    function prefillDates() {
        const now = new Date();
        const localNow = new Date(now.getTime() - (now.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
        const today = new Date().toISOString().slice(0, 10);

        document.querySelectorAll('input[type="datetime-local"]').forEach(el => {
            if (!el.value) el.value = localNow;
        });
        document.querySelectorAll('input[type="date"]').forEach(el => {
            if (!el.value) el.value = today;
        });
    }
    if (closeBtn) {
        closeBtn.onclick = () => modal.classList.add('hidden');
    }

    // Form Submissions
    setupForm('entry-form-activity', '/api/activities');
    setupForm('entry-form-sleep', '/api/sleep');
    setupForm('entry-form-finance', '/api/finance');
});

function setupForm(formId, endpoint) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Simple validation or defaults
        if (data.income === "") data.income = 0;
        if (data.expense === "") data.expense = 0;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            document.getElementById('add-entry-modal').classList.add('hidden');
            form.reset();
            fetchDashboardData();
        } else {
            const err = await response.json();
            alert(`Error: ${err.error || 'Submission failed'}`);
        }
    };
}

async function fetchDashboardData() {
    try {
        // Fetch Summary Stats
        const summaryRes = await fetch('/api/stats/summary');
        const summary = await summaryRes.json();

        if (summaryRes.ok) {
            document.getElementById('level-val').textContent = summary.level;
            document.getElementById('total-xp-val').textContent = summary.xp_stats.total;
            document.getElementById('today-xp-val').textContent = summary.xp_stats.today;

            const progress = (summary.xp_stats.current_level_progress / summary.xp_stats.needed_for_next) * 100;
            document.getElementById('xp-progress-bar').style.width = `${progress}%`;
        } else if (summaryRes.status === 401) {
            window.location.href = '/';
        }

        // Fetch Skill Stats
        const skillsRes = await fetch('/api/stats/skills');
        const skills = await skillsRes.json();

        if (skillsRes.ok) {
            updateSkillBar('Work', skills.Work || 0);
            updateSkillBar('Study', skills.Study || 0);
            updateSkillBar('Workout', skills.Workout || 0);
            updateSkillBar('Cooking', skills.Cooking || 0);
            updateSkillBar('Wasted Time', skills['Wasted Time'] || 0, true);
        }

        // Fetch Finance Stats
        const financeRes = await fetch('/api/stats/finance');
        const fin = await financeRes.json();
        if (financeRes.ok) {
            document.getElementById('finance-income-val').textContent = `$${fin.total_income}`;
            document.getElementById('finance-expense-val').textContent = `$${fin.total_expense}`;
            document.getElementById('finance-net-val').textContent = `$${fin.net}`;

            const maxVal = Math.max(fin.total_income, fin.total_expense, 100);
            document.getElementById('finance-income-bar').style.width = `${(fin.total_income / maxVal) * 100}%`;
            document.getElementById('finance-expense-bar').style.width = `${(fin.total_expense / maxVal) * 100}%`;
        }

        // Fetch Sleep Logs
        const sleepRes = await fetch('/api/sleep');
        const logs = await sleepRes.json();
        if (sleepRes.ok) {
            const container = document.getElementById('sleep-logs-container');
            container.innerHTML = logs.slice(0, 5).map(log => `
                <div class="flex justify-between items-center text-xs border-b border-slate-700 pb-1">
                    <span>${new Date(log.sleep_time).toLocaleDateString()}</span>
                    <span>${Math.round(log.duration_minutes / 60)}h</span>
                    <span class="text-yellow-400">${'★'.repeat(log.quality)}</span>
                </div>
            `).join('') || '<p class="text-xs text-slate-500">No logs yet.</p>';
        }

    } catch (err) {
        console.error('Error fetching dashboard data:', err);
    }
}

function updateSkillBar(name, xp, isNegative = false) {
    const id = name.toLowerCase().replace(' ', '-');
    const bar = document.getElementById(`skill-bar-${id}`);
    const text = document.getElementById(`skill-text-${id}`);

    if (bar && text) {
        const progress = Math.min((Math.abs(xp) / 1000) * 100, 100);
        bar.style.width = `${progress}%`;
        text.textContent = `${xp} XP`;

        if (isNegative && xp < 0) {
            bar.classList.add('bg-rose-600');
        }
    }
}
