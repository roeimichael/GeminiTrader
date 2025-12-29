const API_BASE_URL = 'http://localhost:8000';

let sessionId = null;
let isInitialized = false;

const elements = {
    ticker: document.getElementById('ticker'),
    tradeDate: document.getElementById('tradeDate'),
    query: document.getElementById('query'),
    initializeBtn: document.getElementById('initializeBtn'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    clearBtn: document.getElementById('clearBtn'),
    resultsCard: document.getElementById('resultsCard'),
    loadingCard: document.getElementById('loadingCard'),
    apiStatus: document.getElementById('apiStatus'),
    apiStatusText: document.getElementById('apiStatusText')
};

function setTodayDate() {
    const today = new Date().toISOString().split('T')[0];
    elements.tradeDate.value = today;
}

async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
            elements.apiStatus.classList.add('online');
            elements.apiStatus.classList.remove('offline');
            elements.apiStatusText.textContent = 'API Connected';
            return true;
        }
    } catch (error) {
        elements.apiStatus.classList.add('offline');
        elements.apiStatus.classList.remove('online');
        elements.apiStatusText.textContent = 'API Offline';
        return false;
    }
}

function getSelectedAnalysts() {
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function showLoading(show) {
    elements.loadingCard.style.display = show ? 'block' : 'none';
}

function showResults(show) {
    elements.resultsCard.style.display = show ? 'block' : 'none';
}

function showError(message) {
    alert(`Error: ${message}`);
}

async function initializeAgents() {
    const selectedAnalysts = getSelectedAnalysts();

    if (selectedAnalysts.length === 0) {
        showError('Please select at least one analyst');
        return;
    }

    elements.initializeBtn.disabled = true;
    elements.initializeBtn.textContent = 'Initializing...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/initialize-pool`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                selected_agents: selectedAnalysts,
                session_id: sessionId || 'default'
            })
        });

        const data = await response.json();

        if (response.ok) {
            sessionId = data.session_id;
            isInitialized = true;
            elements.analyzeBtn.disabled = false;
            elements.initializeBtn.textContent = 'Re-initialize Agents';
            showError(`Success: Initialized ${data.agent_count} agents`);
        } else {
            throw new Error(data.detail || 'Failed to initialize agents');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.initializeBtn.disabled = false;
    }
}

async function runAnalysis() {
    const ticker = elements.ticker.value.trim().toUpperCase();
    const tradeDate = elements.tradeDate.value;
    const query = elements.query.value.trim();

    if (!ticker) {
        showError('Please enter a ticker symbol');
        return;
    }

    if (!query) {
        showError('Please enter your question');
        return;
    }

    if (!isInitialized) {
        showError('Please initialize agents first');
        return;
    }

    elements.analyzeBtn.disabled = true;
    elements.analyzeBtn.textContent = 'Analyzing...';
    showLoading(true);
    showResults(false);

    document.getElementById('loadingSubtext').textContent =
        `Analyzing ${ticker} with multi-agent system...`;

    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                ticker: ticker,
                date: tradeDate,
                session_id: sessionId || 'default'
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
            showLoading(false);
            showResults(true);
            window.scrollTo({
                top: document.getElementById('resultsCard').offsetTop - 20,
                behavior: 'smooth'
            });
        } else {
            throw new Error(data.detail || data.error || 'Analysis failed');
        }
    } catch (error) {
        showLoading(false);
        showError(error.message);
    } finally {
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.textContent = 'Run Analysis';
    }
}

function displayResults(data) {
    displayClassification(data.query_classification);
    displayAnalysts(data.individual_responses);
    displayDebate(data.debate);
    displayVerdict(data.final_verdict);
}

function displayClassification(classification) {
    const content = document.getElementById('classificationContent');

    if (!classification) {
        content.innerHTML = '<p>No classification data available</p>';
        return;
    }

    const html = `
        <div class="result-section">
            <h3>Query Analysis</h3>
            <p><strong>Reasoning:</strong> ${classification.reasoning || 'N/A'}</p>

            <div class="classification-info">
                <div class="info-item">
                    <div class="info-label">Complexity</div>
                    <div class="info-value">${classification.complexity || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Selected Agents</div>
                    <div class="info-value">${classification.selected_agents ? classification.selected_agents.length : 0}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Estimated Cost</div>
                    <div class="info-value">${classification.estimated_cost || 'N/A'}</div>
                </div>
            </div>

            ${classification.selected_agents ? `
                <p style="margin-top: 1rem;"><strong>Active Agents:</strong> ${classification.selected_agents.join(', ')}</p>
            ` : ''}
        </div>
    `;

    content.innerHTML = html;
}

function displayAnalysts(responses) {
    const content = document.getElementById('analystsContent');

    if (!responses || responses.length === 0) {
        content.innerHTML = '<p>No analyst responses available</p>';
        return;
    }

    const html = responses.map(response => `
        <div class="result-section">
            <h3>${response.analyst || 'Analyst'}</h3>
            <p>${response.analysis || response.response || 'No analysis provided'}</p>
        </div>
    `).join('');

    content.innerHTML = html;
}

function displayDebate(debate) {
    const content = document.getElementById('debateContent');

    if (!debate || debate.length === 0) {
        content.innerHTML = '<p>No debate data available</p>';
        return;
    }

    const html = debate.map(entry => {
        const isBull = entry.speaker && entry.speaker.toLowerCase().includes('bull');
        const isBear = entry.speaker && entry.speaker.toLowerCase().includes('bear');
        const debateClass = isBull ? 'bull' : (isBear ? 'bear' : '');

        return `
            <div class="debate-entry ${debateClass}">
                <div class="debate-header">
                    <span class="debate-speaker">${entry.speaker || 'Speaker'}</span>
                    <span class="debate-round">Round ${entry.round || 'N/A'}</span>
                </div>
                <p>${entry.argument || entry.message || 'No argument provided'}</p>
            </div>
        `;
    }).join('');

    content.innerHTML = html;
}

function displayVerdict(verdict) {
    const content = document.getElementById('verdictContent');

    if (!verdict) {
        content.innerHTML = '<p>No verdict available</p>';
        return;
    }

    const html = `
        <div class="verdict-box">
            <h3>Final Recommendation</h3>
            <p>${verdict.summary || verdict.decision || verdict.recommendation || 'No verdict provided'}</p>
        </div>

        ${verdict.confidence ? `
            <div class="result-section" style="margin-top: 1.5rem;">
                <h3>Additional Details</h3>
                <p><strong>Confidence:</strong> ${verdict.confidence}</p>
                ${verdict.key_points ? `<p><strong>Key Points:</strong> ${verdict.key_points}</p>` : ''}
            </div>
        ` : ''}
    `;

    content.innerHTML = html;
}

function clearResults() {
    showResults(false);
    elements.ticker.value = '';
    elements.query.value = '';
    setTodayDate();
}

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

elements.initializeBtn.addEventListener('click', initializeAgents);
elements.analyzeBtn.addEventListener('click', runAnalysis);
elements.clearBtn.addEventListener('click', clearResults);

elements.ticker.addEventListener('input', (e) => {
    e.target.value = e.target.value.toUpperCase();
});

elements.ticker.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        runAnalysis();
    }
});

window.addEventListener('DOMContentLoaded', () => {
    setTodayDate();
    setupTabs();
    checkAPIHealth();

    setInterval(checkAPIHealth, 30000);
});
