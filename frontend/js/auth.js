/**
 * Auth Module - Gerencia autenticação (login/registro/logout)
 */

const Auth = (function() {
    // Configuração da API
    const API_URL = 'http://127.0.0.1:8000';

    // Elementos DOM
    let loginForm, registerForm, loginEmailInput, loginPasswordInput;
    let registerNameInput, registerEmailInput, registerPasswordInput;
    let showRegisterLink, showLoginLink, authError;

    /**
     * Inicializa o módulo de autenticação
     */
    function init() {
        // Captura elementos do DOM
        loginForm = document.getElementById('login-form');
        registerForm = document.getElementById('register-form');
        loginEmailInput = document.getElementById('login-email');
        loginPasswordInput = document.getElementById('login-password');
        registerNameInput = document.getElementById('register-name');
        registerEmailInput = document.getElementById('register-email');
        registerPasswordInput = document.getElementById('register-password');
        showRegisterLink = document.getElementById('show-register');
        showLoginLink = document.getElementById('show-login');
        authError = document.getElementById('auth-error');

        // Configura event listeners
        setupEventListeners();

        // Verifica se já está logado
        checkExistingSession();
    }

    /**
     * Configura os event listeners
     */
    function setupEventListeners() {
        // Toggle entre formulários
        showRegisterLink.addEventListener('click', (e) => {
            e.preventDefault();
            toggleForms('register');
        });

        showLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            toggleForms('login');
        });

        // Submit dos formulários
        loginForm.addEventListener('submit', handleLogin);
        registerForm.addEventListener('submit', handleRegister);
    }

    /**
     * Alterna entre formulários de login e registro
     */
    function toggleForms(form) {
        hideError();
        if (form === 'register') {
            loginForm.classList.remove('active');
            registerForm.classList.add('active');
        } else {
            registerForm.classList.remove('active');
            loginForm.classList.add('active');
        }
    }

    /**
     * Verifica se existe sessão ativa
     */
    function checkExistingSession() {
        const token = getToken();
        const user = getUser();

        if (token && user) {
            // Dispara evento de login bem-sucedido
            window.dispatchEvent(new CustomEvent('authSuccess', {
                detail: { user, token }
            }));
        }
    }

    /**
     * Processa o login
     */
    async function handleLogin(e) {
        e.preventDefault();
        hideError();

        const email = loginEmailInput.value.trim();
        const password = loginPasswordInput.value;

        if (!email || !password) {
            showError('Preencha todos os campos');
            return;
        }

        try {
            App.showLoading();

            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erro ao fazer login');
            }

            // Salva token e dados do usuário (API retorna user object)
            saveSession(data.access_token, data.user);

            // Dispara evento de sucesso
            window.dispatchEvent(new CustomEvent('authSuccess', {
                detail: {
                    user: getUser(),
                    token: data.access_token
                }
            }));

            // Limpa formulário
            loginForm.reset();

        } catch (error) {
            showError(error.message);
        } finally {
            App.hideLoading();
        }
    }

    /**
     * Processa o registro
     */
    async function handleRegister(e) {
        e.preventDefault();
        hideError();

        const name = registerNameInput.value.trim();
        const email = registerEmailInput.value.trim();
        const password = registerPasswordInput.value;

        if (!name || !email || !password) {
            showError('Preencha todos os campos');
            return;
        }

        if (password.length < 6) {
            showError('A senha deve ter pelo menos 6 caracteres');
            return;
        }

        try {
            App.showLoading();

            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    name: name
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erro ao cadastrar');
            }

            // Registro retorna token e user, já autenticado
            saveSession(data.access_token, data.user);

            // Dispara evento de sucesso
            window.dispatchEvent(new CustomEvent('authSuccess', {
                detail: {
                    user: data.user,
                    token: data.access_token
                }
            }));

            // Limpa formulário
            registerForm.reset();

        } catch (error) {
            showError(error.message);
        } finally {
            App.hideLoading();
        }
    }

    /**
     * Faz logout
     */
    function logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');

        // Dispara evento de logout
        window.dispatchEvent(new CustomEvent('authLogout'));
    }

    /**
     * Salva sessão no localStorage
     */
    function saveSession(token, user) {
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user_data', JSON.stringify(user));
    }

    /**
     * Obtém o token atual
     */
    function getToken() {
        return localStorage.getItem('auth_token');
    }

    /**
     * Obtém dados do usuário
     */
    function getUser() {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    }

    /**
     * Exibe mensagem de erro
     */
    function showError(message) {
        authError.textContent = message;
        authError.classList.add('show');
    }

    /**
     * Esconde mensagem de erro
     */
    function hideError() {
        authError.textContent = '';
        authError.classList.remove('show');
    }

    // API pública
    return {
        init,
        logout,
        getToken,
        getUser
    };
})();
