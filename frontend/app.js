const API_BASE_URL = 'http://localhost:8000';

let sessionId = null;
let isInitialized = false;
let availableAgents = {};

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
    apiStatusText: document.getElementById('apiStatusText'),
    agentsLoading: document.getElementById('agentsLoading'),
    agentsContainer: document.getElementById('agentsContainer')
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

async function fetchAvailableAgents() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/agents`);
        if (response.ok) {
            availableAgents = await response.json();
            renderAgents();
            return true;
        }
    } catch (error) {
        console.error('Failed to fetch agents:', error);
        elements.agentsLoading.textContent = 'Failed to load agents. Please refresh.';
        return false;
    }
}

function renderAgents() {
    const categoryOrder = ['analysts', 'researchers', 'managers', 'risk_analysts', 'trader'];
    const categoryLabels = {
        'analysts': 'Analysts',
        'researchers': 'Researchers',
        'managers': 'Managers',
        'risk_analysts': 'Risk Analysts',
        'trader': 'Trader'
    };

    let html = '';

    categoryOrder.forEach(category => {
        if (!availableAgents[category]) return;

        const agents = availableAgents[category];
        const categoryName = categoryLabels[category] || category;

        html += `
            <div class="agent-category">
                <h3>
                    ${categoryName}
                    <span class="category-actions">
                        <button onclick="selectCategoryAgents('${category}', true)">Select All</button> |
                        <button onclick="selectCategoryAgents('${category}', false)">Deselect All</button>
                    </span>
                </h3>
                <div class="checkbox-group">
        `;

        Object.entries(agents).forEach(([agentId, agentInfo]) => {
            const isDefaultChecked = category === 'analysts';

            html += `
                <label class="checkbox-label">
                    <input
                        type="checkbox"
                        data-category="${category}"
                        data-agent-id="${agentId}"
                        ${isDefaultChecked ? 'checked' : ''}
                    >
                    <span>${agentInfo.name}</span>
                    <small>${agentInfo.description}</small>
                    ${agentInfo.requires_memory ? '<small style="color: var(--primary-color); font-weight: 600;">Requires Memory</small>' : ''}
                </label>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    elements.agentsContainer.innerHTML = html;
    elements.agentsLoading.style.display = 'none';
    elements.agentsContainer.style.display = 'block';

    const form = document.querySelector('.form-group label');
    if (form && form.textContent.includes('Loading')) {
        form.textContent = 'Select Agents';
    }
}

function selectCategoryAgents(category, select) {
    const checkboxes = document.querySelectorAll(`input[data-category="${category}"]`);
    checkboxes.forEach(cb => cb.checked = select);
}

function getSelectedAnalysts() {
    const checkboxes = document.querySelectorAll('#agentsContainer input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => {
        const category = cb.getAttribute('data-category');
        const agentId = cb.getAttribute('data-agent-id');
        return `${agentId}_${category === 'analysts' ? 'analyst' :
                              category === 'researchers' ? 'researcher' :
                              category === 'managers' ? 'manager' :
                              category === 'risk_analysts' ? 'analyst' :
                              'trader'}`;
    });
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
            <h3>${response.agent || 'Analyst'}</h3>
            <p>${response.response || 'No analysis provided'}</p>
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

    const html = debate.map(round => {
        const roundHeader = `
            <div style="margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--primary-color);">
                <h3 style="color: var(--primary-color); margin: 0;">Round ${round.round}: ${round.topic || 'Debate'}</h3>
            </div>
        `;

        const exchanges = round.exchanges.map(exchange => {
            const isBull = exchange.speaker && exchange.speaker.toLowerCase().includes('bull');
            const isBear = exchange.speaker && exchange.speaker.toLowerCase().includes('bear');
            const debateClass = isBull ? 'bull' : (isBear ? 'bear' : '');

            return `
                <div class="debate-entry ${debateClass}">
                    <div class="debate-header">
                        <span class="debate-speaker">${exchange.speaker || 'Speaker'}</span>
                        <span class="debate-round">Round ${round.round}</span>
                    </div>
                    <p>${exchange.statement || 'No statement provided'}</p>
                </div>
            `;
        }).join('');

        return roundHeader + exchanges;
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

window.addEventListener('DOMContentLoaded', async () => {
    setTodayDate();
    setupTabs();
    await checkAPIHealth();
    await fetchAvailableAgents();

    setInterval(checkAPIHealth, 30000);
});
