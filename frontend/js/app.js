/**
 * App Module - Orquestra a aplicação
 */

const App = (function() {
    // Elementos DOM
    let authContainer, chatContainer, loadingOverlay, userNameSpan, logoutBtn;

    /**
     * Inicializa a aplicação
     */
    function init() {
        // Captura elementos do DOM
        authContainer = document.getElementById('auth-container');
        chatContainer = document.getElementById('chat-container');
        loadingOverlay = document.getElementById('loading-overlay');
        userNameSpan = document.getElementById('user-name');
        logoutBtn = document.getElementById('logout-btn');

        // Inicializa módulos
        Auth.init();
        Chat.init();

        // Configura event listeners
        setupEventListeners();
    }

    /**
     * Configura os event listeners
     */
    function setupEventListeners() {
        // Escuta eventos de autenticação
        window.addEventListener('authSuccess', handleAuthSuccess);
        window.addEventListener('authLogout', handleLogout);

        // Logout button
        logoutBtn.addEventListener('click', () => {
            if (confirm('Deseja realmente sair?')) {
                Auth.logout();
            }
        });
    }

    /**
     * Processa login bem-sucedido
     */
    function handleAuthSuccess(event) {
        const { user } = event.detail;

        // Atualiza nome do usuário
        userNameSpan.textContent = user.name || user.email;

        // Transição de telas
        authContainer.classList.add('hidden');
        chatContainer.classList.remove('hidden');

        // Foca no input do chat
        Chat.focusInput();
    }

    /**
     * Processa logout
     */
    function handleLogout() {
        // Limpa chat
        Chat.clearMessages();

        // Transição de telas
        chatContainer.classList.add('hidden');
        authContainer.classList.remove('hidden');
    }

    /**
     * Mostra loading overlay
     */
    function showLoading() {
        loadingOverlay.classList.remove('hidden');
    }

    /**
     * Esconde loading overlay
     */
    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }

    // API pública
    return {
        init,
        showLoading,
        hideLoading
    };
})();

// Inicializa quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', App.init);
