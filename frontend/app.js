const API_BASE_URL = window.location.origin;

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
    apiStatusText: document.getElementById('apiStatusText'),
    loadAgentsBtn: document.getElementById('loadAgentsBtn'),
    availableAgentsContent: document.getElementById('availableAgentsContent'),
    agentsListContent: document.getElementById('agentsListContent'),
    listSessionsBtn: document.getElementById('listSessionsBtn'),
    deleteSessionBtn: document.getElementById('deleteSessionBtn'),
    sessionsContent: document.getElementById('sessionsContent'),
    sessionsListContent: document.getElementById('sessionsListContent'),
    enableDebugBtn: document.getElementById('enableDebugBtn'),
    disableDebugBtn: document.getElementById('disableDebugBtn'),
    viewHistoryBtn: document.getElementById('viewHistoryBtn'),
    clearHistoryBtn: document.getElementById('clearHistoryBtn'),
    historyContent: document.getElementById('historyContent'),
    historyListContent: document.getElementById('historyListContent')
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

function showSuccess(message) {
    alert(`Success: ${message}`);
}

async function loadAvailableAgents() {
    elements.loadAgentsBtn.disabled = true;
    elements.loadAgentsBtn.textContent = 'Loading...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/agents`);
        const data = await response.json();

        if (response.ok) {
            displayAvailableAgents(data);
            elements.availableAgentsContent.style.display = 'block';
        } else {
            throw new Error('Failed to load agents');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.loadAgentsBtn.disabled = false;
        elements.loadAgentsBtn.textContent = 'Reload Available Agents';
    }
}

function displayAvailableAgents(agents) {
    let html = '';

    for (const [category, categoryAgents] of Object.entries(agents)) {
        html += `<div class="result-section">`;
        html += `<h3>${category.charAt(0).toUpperCase() + category.slice(1)}</h3>`;

        for (const [agentId, agentInfo] of Object.entries(categoryAgents)) {
            html += `
                <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <strong>${agentInfo.name || agentId}</strong><br>
                    <small>${agentInfo.description || 'No description'}</small><br>
                    <small style="color: var(--text-secondary);">
                        Memory: ${agentInfo.requires_memory ? 'Yes' : 'No'}
                    </small>
                </div>
            `;
        }
        html += `</div>`;
    }

    elements.agentsListContent.innerHTML = html;
}

async function listSessions() {
    elements.listSessionsBtn.disabled = true;
    elements.listSessionsBtn.textContent = 'Loading...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/sessions`);
        const data = await response.json();

        if (response.ok) {
            displaySessions(data);
            elements.sessionsContent.style.display = 'block';
        } else {
            throw new Error('Failed to load sessions');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.listSessionsBtn.disabled = false;
        elements.listSessionsBtn.textContent = 'Reload Sessions';
    }
}

function displaySessions(data) {
    if (data.total === 0) {
        elements.sessionsListContent.innerHTML = '<p>No active sessions</p>';
        return;
    }

    let html = `<div class="result-section">`;
    html += `<h3>Total Sessions: ${data.total}</h3>`;

    for (const [sid, sessionData] of Object.entries(data.sessions)) {
        html += `
            <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem; border-left: 4px solid var(--primary-color);">
                <strong>Session ID: ${sid}</strong><br>
                <small>Created: ${sessionData.created_at}</small><br>
                <small>Agents: ${sessionData.agent_count} (${sessionData.agents.join(', ')})</small>
            </div>
        `;
    }

    html += `</div>`;
    elements.sessionsListContent.innerHTML = html;
}

async function deleteSession() {
    const sid = sessionId || 'default';

    if (!confirm(`Are you sure you want to delete session "${sid}"?`)) {
        return;
    }

    elements.deleteSessionBtn.disabled = true;
    elements.deleteSessionBtn.textContent = 'Deleting...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/session/${sid}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(data.message);
            sessionId = null;
            isInitialized = false;
            elements.analyzeBtn.disabled = true;
            elements.initializeBtn.textContent = 'Initialize Agents';
        } else {
            throw new Error(data.detail || 'Failed to delete session');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.deleteSessionBtn.disabled = false;
        elements.deleteSessionBtn.textContent = 'Delete Current Session';
    }
}

async function enableDebug() {
    elements.enableDebugBtn.disabled = true;
    elements.enableDebugBtn.textContent = 'Enabling...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/debug/enable`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(data.message);
        } else {
            throw new Error('Failed to enable debug mode');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.enableDebugBtn.disabled = false;
        elements.enableDebugBtn.textContent = 'Enable Debug Mode';
    }
}

async function disableDebug() {
    elements.disableDebugBtn.disabled = true;
    elements.disableDebugBtn.textContent = 'Disabling...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/debug/disable`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(data.message);
        } else {
            throw new Error('Failed to disable debug mode');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.disableDebugBtn.disabled = false;
        elements.disableDebugBtn.textContent = 'Disable Debug Mode';
    }
}

async function viewHistory() {
    const sid = sessionId || 'default';

    elements.viewHistoryBtn.disabled = true;
    elements.viewHistoryBtn.textContent = 'Loading...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/history?session_id=${sid}&limit=10`);
        const data = await response.json();

        if (response.ok) {
            displayHistory(data);
            elements.historyContent.style.display = 'block';
        } else {
            throw new Error('Failed to load history');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.viewHistoryBtn.disabled = false;
        elements.viewHistoryBtn.textContent = 'Reload History';
    }
}

function displayHistory(history) {
    if (!history || history.length === 0) {
        elements.historyListContent.innerHTML = '<p>No history available</p>';
        return;
    }

    let html = '<div class="result-section">';
    html += `<h3>Recent Queries (${history.length})</h3>`;

    history.forEach((item, index) => {
        const recommendation = item.final_verdict?.overall_recommendation || 'N/A';
        const ticker = item.ticker || 'N/A';

        html += `
            <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem; border-left: 4px solid var(--success-color);">
                <strong>#${index + 1} - ${ticker}</strong><br>
                <small>Time: ${item.timestamp}</small><br>
                <small>Query: ${item.query ? item.query.substring(0, 100) : 'N/A'}...</small><br>
                <small style="color: var(--primary-color);">Recommendation: ${recommendation}</small>
            </div>
        `;
    });

    html += '</div>';
    elements.historyListContent.innerHTML = html;
}

async function clearHistory() {
    const sid = sessionId || 'default';

    if (!confirm(`Are you sure you want to clear history for session "${sid}"?`)) {
        return;
    }

    elements.clearHistoryBtn.disabled = true;
    elements.clearHistoryBtn.textContent = 'Clearing...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/history?session_id=${sid}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(data.message);
            elements.historyContent.style.display = 'none';
        } else {
            throw new Error('Failed to clear history');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        elements.clearHistoryBtn.disabled = false;
        elements.clearHistoryBtn.textContent = 'Clear History';
    }
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
            showSuccess(`Initialized ${data.agent_count} agents`);
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
            <p style="white-space: pre-wrap;">${response.response || response.analysis || 'No analysis provided'}</p>
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

    let html = '';

    debate.forEach(round => {
        html += `<div class="result-section">`;
        html += `<h3>Round ${round.round}: ${round.topic || 'Debate'}</h3>`;

        if (round.exchanges && round.exchanges.length > 0) {
            round.exchanges.forEach(exchange => {
                const isBull = exchange.speaker && exchange.speaker.toLowerCase().includes('bull');
                const isBear = exchange.speaker && exchange.speaker.toLowerCase().includes('bear');
                const debateClass = isBull ? 'bull' : (isBear ? 'bear' : '');

                html += `
                    <div class="debate-entry ${debateClass}">
                        <div class="debate-header">
                            <span class="debate-speaker">${exchange.speaker || 'Speaker'}</span>
                        </div>
                        <p style="white-space: pre-wrap;">${exchange.statement || exchange.argument || exchange.message || 'No statement provided'}</p>
                    </div>
                `;
            });
        }

        html += `</div>`;
    });

    content.innerHTML = html;
}

function displayVerdict(verdict) {
    const content = document.getElementById('verdictContent');

    if (!verdict) {
        content.innerHTML = '<p>No verdict available</p>';
        return;
    }

    let html = `
        <div class="verdict-box">
            <h3>Final Recommendation: ${verdict.overall_recommendation || 'N/A'}</h3>
        </div>

        <div class="result-section" style="margin-top: 1.5rem;">
            <h3>Summary</h3>
            <p style="white-space: pre-wrap;">${verdict.summary || verdict.decision || verdict.recommendation || verdict.final_trade_decision || 'No verdict provided'}</p>
        </div>
    `;

    if (verdict.confidence_level || verdict.sentiment_breakdown) {
        html += `<div class="result-section">`;
        html += `<h3>Additional Details</h3>`;

        if (verdict.confidence_level) {
            html += `<p><strong>Confidence:</strong> ${verdict.confidence_level}</p>`;
        }

        if (verdict.sentiment_breakdown) {
            html += `
                <p><strong>Sentiment Breakdown:</strong></p>
                <ul>
                    <li>Bullish: ${verdict.sentiment_breakdown.bullish || 0}</li>
                    <li>Bearish: ${verdict.sentiment_breakdown.bearish || 0}</li>
                    <li>Neutral: ${verdict.sentiment_breakdown.neutral || 0}</li>
                    <li>Bullish %: ${verdict.sentiment_breakdown.bullish_percentage || 0}%</li>
                </ul>
            `;
        }

        html += `</div>`;
    }

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

// Event Listeners
elements.loadAgentsBtn.addEventListener('click', loadAvailableAgents);
elements.listSessionsBtn.addEventListener('click', listSessions);
elements.deleteSessionBtn.addEventListener('click', deleteSession);
elements.enableDebugBtn.addEventListener('click', enableDebug);
elements.disableDebugBtn.addEventListener('click', disableDebug);
elements.viewHistoryBtn.addEventListener('click', viewHistory);
elements.clearHistoryBtn.addEventListener('click', clearHistory);
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
