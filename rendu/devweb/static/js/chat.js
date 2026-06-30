// Chat and System Management for TechCorp Financial AI

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const apiTypeSelect = document.getElementById('apiType');
    const apiUrlInput = document.getElementById('apiUrl');
    const modelNameSelect = document.getElementById('modelName');
    const btnCheckConn = document.getElementById('btnCheckConn');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const statusLatency = document.getElementById('statusLatency');
    
    const temperatureInput = document.getElementById('temperature');
    const tempValue = document.getElementById('tempValue');
    
    const conversationsList = document.getElementById('conversationsList');
    const btnNewChat = document.getElementById('btnNewChat');
    const btnClearHistory = document.getElementById('btnClearHistory');
    
    const activeChatTitle = document.getElementById('activeChatTitle');
    const currentModelDisplay = document.getElementById('currentModelDisplay');
    const btnExportChat = document.getElementById('btnExportChat');
    
    const chatViewport = document.getElementById('chatViewport');
    const welcomeScreen = document.getElementById('welcomeScreen');
    const messagesContainer = document.getElementById('messagesContainer');
    const typingIndicator = document.getElementById('typingIndicator');
    
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const btnSend = document.getElementById('btnSend');

    // App State
    let conversations = {};
    let activeConversationId = null;
    let isConnected = false;
    let isGenerating = false;

    // Initialize UI and load conversations
    init();

    function init() {
        // Setup icons
        lucide.createIcons();
        
        // Load localStorage
        loadConversations();
        
        // Setup events
        btnCheckConn.addEventListener('click', checkConnection);
        apiTypeSelect.addEventListener('change', handleApiTypeChange);
        apiUrlInput.addEventListener('input', () => { isConnected = false; updateStatusUI('disconnected', 'Tester la connexion'); });
        
        temperatureInput.addEventListener('input', (e) => {
            tempValue.textContent = e.target.value;
        });

        // Auto-resize textarea
        userInput.addEventListener('input', () => {
            userInput.style.height = 'auto';
            userInput.style.height = (userInput.scrollHeight) + 'px';
            btnSend.disabled = userInput.value.trim() === '' || isGenerating;
        });

        // Enter key submits form (Shift+Enter inserts newline)
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (userInput.value.trim() !== '' && !isGenerating) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            }
        });

        chatForm.addEventListener('submit', handleSendMessage);
        btnNewChat.addEventListener('click', () => startNewConversation());
        btnClearHistory.addEventListener('click', clearAllHistory);
        btnExportChat.addEventListener('click', exportActiveChat);
        
        // Initial ping check
        checkConnection();
        
        // Regular server monitoring every 15 seconds
        setInterval(checkConnection, 15000);
    }

    // --- Core Logic functions ---

    function loadConversations() {
        try {
            const data = localStorage.getItem('techcorp_chats');
            if (data) {
                conversations = JSON.parse(data);
            }
        } catch (e) {
            console.error("Error reading localStorage", e);
            conversations = {};
        }

        const keys = Object.keys(conversations);
        if (keys.length > 0) {
            // Sort by last updated
            keys.sort((a, b) => conversations[b].updatedAt - conversations[a].updatedAt);
            renderConversationsList(keys);
            
            // Activate the most recent conversation
            setActiveConversation(keys[0]);
        } else {
            startNewConversation(false); // set state to empty
        }
    }

    function saveConversations() {
        localStorage.setItem('techcorp_chats', JSON.stringify(conversations));
    }

    function renderConversationsList(sortedKeys) {
        conversationsList.innerHTML = '';
        if (sortedKeys.length === 0) {
            conversationsList.innerHTML = '<div class="system-disclaimer">Aucune conversation</div>';
            return;
        }

        sortedKeys.forEach(id => {
            const chat = conversations[id];
            const item = document.createElement('button');
            item.className = `conversation-item ${id === activeConversationId ? 'active' : ''}`;
            item.dataset.id = id;
            
            // Inner HTML with layout
            item.innerHTML = `
                <i data-lucide="message-square"></i>
                <span class="conversation-title">${escapeHTML(chat.title)}</span>
                <button class="btn-delete-chat" title="Supprimer">
                    <i data-lucide="trash-2"></i>
                </button>
            `;
            
            // Select click
            item.addEventListener('click', (e) => {
                if (e.target.closest('.btn-delete-chat')) {
                    e.stopPropagation();
                    deleteConversation(id);
                } else {
                    setActiveConversation(id);
                }
            });
            
            conversationsList.appendChild(item);
        });
        
        lucide.createIcons();
    }

    function setActiveConversation(id) {
        activeConversationId = id;
        
        // Highlight in list
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.toggle('active', item.dataset.id === id);
        });

        const chat = conversations[id];
        if (chat && chat.messages.length > 0) {
            welcomeScreen.style.display = 'none';
            messagesContainer.style.display = 'flex';
            
            // Render messages
            messagesContainer.innerHTML = '';
            chat.messages.forEach(msg => {
                appendMessageToUI(msg.role, msg.content);
            });
            activeChatTitle.textContent = chat.title;
            scrollToBottom();
        } else {
            // New empty conversation
            welcomeScreen.style.display = 'flex';
            messagesContainer.style.display = 'none';
            messagesContainer.innerHTML = '';
            activeChatTitle.textContent = "Nouveau Chat Financier";
        }
    }

    function startNewConversation(render = true) {
        const id = 'chat_' + Date.now();
        conversations[id] = {
            id: id,
            title: "Nouveau Chat Financier",
            messages: [],
            createdAt: Date.now(),
            updatedAt: Date.now()
        };
        
        saveConversations();
        activeConversationId = id;
        
        if (render) {
            const keys = Object.keys(conversations).sort((a, b) => conversations[b].updatedAt - conversations[a].updatedAt);
            renderConversationsList(keys);
            setActiveConversation(id);
        }
    }

    function deleteConversation(id) {
        delete conversations[id];
        saveConversations();
        
        const keys = Object.keys(conversations).sort((a, b) => conversations[b].updatedAt - conversations[a].updatedAt);
        renderConversationsList(keys);
        
        if (activeConversationId === id) {
            if (keys.length > 0) {
                setActiveConversation(keys[0]);
            } else {
                startNewConversation();
            }
        }
    }

    function clearAllHistory() {
        if (confirm("Êtes-vous sûr de vouloir effacer tout l'historique des conversations ?")) {
            conversations = {};
            saveConversations();
            startNewConversation();
        }
    }

    function handleApiTypeChange() {
        const type = apiTypeSelect.value;
        if (type === 'ollama') {
            apiUrlInput.value = 'http://localhost:11434';
        } else if (type === 'openai') {
            apiUrlInput.value = 'http://localhost:8000';
        } else {
            apiUrlInput.value = 'http://localhost:5000';
        }
        isConnected = false;
        updateStatusUI('disconnected', 'Tester la connexion');
        checkConnection();
    }

    async function checkConnection() {
        const url = apiUrlInput.value.trim();
        const type = apiTypeSelect.value;
        
        if (!url) return;
        
        statusText.textContent = "Vérification...";
        statusDot.className = "status-dot disconnected";
        
        const startTime = performance.now();
        
        try {
            const response = await fetch('/api/health', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ apiUrl: url, apiType: type })
            });
            
            const endTime = performance.now();
            const latency = Math.round(endTime - startTime);
            
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'connected') {
                    isConnected = true;
                    updateStatusUI('connected', 'Connecté', `${latency} ms`);
                    
                    // Populate models if returned
                    if (data.models && data.models.length > 0) {
                        updateModelsDropdown(data.models);
                    }
                    return;
                }
            }
        } catch (e) {
            console.error("Health check failed", e);
        }
        
        isConnected = false;
        updateStatusUI('disconnected', 'Hors ligne');
    }

    function updateStatusUI(status, text, latencyStr = '') {
        statusDot.className = `status-dot ${status}`;
        statusText.textContent = text;
        statusLatency.textContent = latencyStr;
    }

    function updateModelsDropdown(models) {
        // Keep active choice if possible
        const currentChoice = modelNameSelect.value;
        modelNameSelect.innerHTML = '';
        
        models.forEach(model => {
            const opt = document.createElement('option');
            opt.value = model;
            opt.textContent = model;
            if (model === currentChoice || model.includes('phi3') || model.includes('financial')) {
                opt.selected = true;
            }
            modelNameSelect.appendChild(opt);
        });
        
        // Add default options back if empty
        if (models.length === 0) {
            const opt = document.createElement('option');
            opt.value = 'phi3.5-financial';
            opt.textContent = 'phi3.5-financial (Par défaut)';
            modelNameSelect.appendChild(opt);
        }
        
        // Update display text
        currentModelDisplay.textContent = modelNameSelect.value;
    }

    modelNameSelect.addEventListener('change', () => {
        currentModelDisplay.textContent = modelNameSelect.value;
    });

    // --- Message handling ---

    async function handleSendMessage(e) {
        e.preventDefault();
        
        const messageText = userInput.value.trim();
        if (!messageText || isGenerating) return;
        
        // Show in UI
        welcomeScreen.style.display = 'none';
        messagesContainer.style.display = 'flex';
        
        appendMessageToUI('user', messageText);
        
        // Save user message to state
        const chat = conversations[activeConversationId];
        chat.messages.push({ role: 'user', content: messageText });
        
        // Update title if first message
        if (chat.title === "Nouveau Chat Financier" || chat.messages.length === 1) {
            chat.title = messageText.length > 25 ? messageText.substring(0, 25) + '...' : messageText;
            activeChatTitle.textContent = chat.title;
        }
        
        chat.updatedAt = Date.now();
        saveConversations();
        
        // Refresh sidebar lists
        const keys = Object.keys(conversations).sort((a, b) => conversations[b].updatedAt - conversations[a].updatedAt);
        renderConversationsList(keys);
        
        // Clear input
        userInput.value = '';
        userInput.style.height = 'auto';
        btnSend.disabled = true;
        
        // Trigger model request
        isGenerating = true;
        typingIndicator.style.display = 'flex';
        scrollToBottom();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    apiUrl: apiUrlInput.value.trim(),
                    apiType: apiTypeSelect.value,
                    modelName: modelNameSelect.value,
                    messages: chat.messages, // sends whole conversation context
                    temperature: parseFloat(temperatureInput.value)
                })
            });
            
            typingIndicator.style.display = 'none';
            isGenerating = false;
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const reply = data.content;
                    appendMessageToUI('assistant', reply);
                    chat.messages.push({ role: 'assistant', content: reply });
                    chat.updatedAt = Date.now();
                    saveConversations();
                } else {
                    appendMessageToUI('assistant', `⚠️ **Erreur du serveur d'inférence** : ${data.message}`);
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errMsg = errorData.message || `Code erreur HTTP ${response.status}`;
                appendMessageToUI('assistant', `❌ **Erreur de connexion** : Impossible de joindre l'API d'inférence. \n\n*Détails : ${errMsg}* \n\n*Veuillez vérifier que l'INFRA a bien lancé Ollama/Triton et que l'URL configurée dans le panneau de gauche est correcte.*`);
            }
        } catch (err) {
            console.error(err);
            typingIndicator.style.display = 'none';
            isGenerating = false;
            appendMessageToUI('assistant', `❌ **Erreur système** : Une erreur inattendue est survenue dans le script web. \n\n*Détails : ${err.message}*`);
        }
        
        scrollToBottom();
    }

    function appendMessageToUI(role, content) {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        
        if (role === 'user') {
            avatar.innerHTML = '<i data-lucide="user"></i>';
        } else {
            avatar.innerHTML = '<i data-lucide="cpu"></i>';
        }
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = formatMarkdown(content);
        
        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);
        messagesContainer.appendChild(wrapper);
        
        lucide.createIcons();
    }

    function scrollToBottom() {
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }

    window.setQuickPrompt = function(promptText) {
        userInput.value = promptText;
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
        btnSend.disabled = false;
        userInput.focus();
    };

    function exportActiveChat() {
        const chat = conversations[activeConversationId];
        if (!chat || chat.messages.length === 0) return;
        
        const jsonString = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(chat, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", jsonString);
        downloadAnchor.setAttribute("download", `chat_export_${chat.id}.json`);
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
    }

    // --- HTML Sanitization & Simple Markdown Parsing ---

    function escapeHTML(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatMarkdown(markdownText) {
        if (!markdownText) return '';
        
        let text = escapeHTML(markdownText);
        
        // 1. Code blocks: ```lang ... ```
        const codeBlockRegex = /```(?:[a-zA-Z0-9]+)?\n([\s\S]*?)\n```/g;
        text = text.replace(codeBlockRegex, (match, code) => {
            return `<pre><code>${code}</code></pre>`;
        });
        
        // 2. Inline code: `code`
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // 3. Bold: **text**
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // 4. Tables: | col1 | col2 |
        const lines = text.split('\n');
        let inTable = false;
        let tableHTML = '';
        let tableHeaderParsed = false;
        let formattedLines = [];
        
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i].trim();
            
            if (line.startsWith('|') && line.endsWith('|')) {
                // Table line
                if (!inTable) {
                    inTable = true;
                    tableHTML = '<table>';
                    tableHeaderParsed = false;
                }
                
                // Check if it is a separator row e.g. |---|---|
                if (line.match(/^\|[\s-|-]*\|$/)) {
                    continue; // Skip separator line
                }
                
                const cells = line.split('|').slice(1, -1).map(c => c.trim());
                
                if (!tableHeaderParsed) {
                    tableHTML += '<thead><tr>';
                    cells.forEach(cell => {
                        tableHTML += `<th>${cell}</th>`;
                    });
                    tableHTML += '</tr></thead><tbody>';
                    tableHeaderParsed = true;
                } else {
                    tableHTML += '<tr>';
                    cells.forEach(cell => {
                        tableHTML += `<td>${cell}</td>`;
                    });
                    tableHTML += '</tr>';
                }
            } else {
                if (inTable) {
                    inTable = false;
                    tableHTML += '</tbody></table>';
                    formattedLines.push(tableHTML);
                    tableHTML = '';
                }
                formattedLines.push(lines[i]);
            }
        }
        if (inTable) {
            tableHTML += '</tbody></table>';
            formattedLines.push(tableHTML);
        }
        
        text = formattedLines.join('\n');
        
        // 5. Lists: * item or - item
        const listRegex = /^(?:\*|-)\s+(.+)$/gm;
        text = text.replace(listRegex, '<li>$1</li>');
        // Wrap adjacent li elements into ul
        // A simple pass replacing sequential <li> items
        text = text.replace(/(<li>[\s\S]*?<\/li>)/g, (match) => {
            return `<ul>${match}</ul>`;
        });
        // Remove redundant ul wrappers
        text = text.replace(/<\/ul>\s*<ul>/g, '');

        // 6. Numbered Lists: 1. item
        const numListRegex = /^\d+\.\s+(.+)$/gm;
        text = text.replace(numListRegex, '<li>$1</li>');
        text = text.replace(/(<li>[\s\S]*?<\/li>)/g, (match) => {
            // Note: simple match, if it was already list it might conflict, but this is a light parser
            if (match.includes('<ul>')) return match;
            return `<ol>${match}</ol>`;
        });
        text = text.replace(/<\/ol>\s*<ol>/g, '');
        
        // 7. Line Breaks (paragraphs)
        // Convert single returns to br, but respect pre blocks and tables
        const blocks = text.split(/(<pre>[\s\S]*?<\/pre>|<table>[\s\S]*?<\/table>|<ul>[\s\S]*?<\/ul>|<ol>[\s\S]*?<\/ol>)/g);
        for (let j = 0; j < blocks.length; j++) {
            if (!blocks[j].startsWith('<pre>') && !blocks[j].startsWith('<table>') && !blocks[j].startsWith('<ul>') && !blocks[j].startsWith('<ol>')) {
                blocks[j] = blocks[j].replace(/\n/g, '<br>');
            }
        }
        text = blocks.join('');
        
        return text;
    }
});
