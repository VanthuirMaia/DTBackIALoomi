/**
 * Chat Module - Gerencia interface de chat e comunicação com a API
 */

const Chat = (function () {
  // Configuração da API
  const API_URL = "";

  // Elementos DOM
  let messagesContainer, chatForm, chatInput, sendBtn, clearBtn;
  let welcomeMessage;

  // Estado
  let isTyping = false;

  /**
   * Inicializa o módulo de chat
   */
  function init() {
    // Captura elementos do DOM
    messagesContainer = document.getElementById("messages");
    chatForm = document.getElementById("chat-form");
    chatInput = document.getElementById("chat-input");
    sendBtn = document.getElementById("send-btn");
    clearBtn = document.getElementById("clear-chat");

    // Configura event listeners
    setupEventListeners();
  }

  /**
   * Configura os event listeners
   */
  function setupEventListeners() {
    chatForm.addEventListener("submit", handleSendMessage);
    clearBtn.addEventListener("click", handleClearChat);

    // Enter para enviar (Shift+Enter para nova linha não aplicável em input)
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        // Form submit será tratado pelo evento submit
      }
    });
  }

  /**
   * Processa o envio de mensagem
   */
  async function handleSendMessage(e) {
    e.preventDefault();

    const message = chatInput.value.trim();
    if (!message || isTyping) return;

    const token = Auth.getToken();
    if (!token) {
      alert("Sessão expirada. Por favor, faça login novamente.");
      Auth.logout();
      return;
    }

    // Limpa input
    chatInput.value = "";

    // Remove mensagem de boas-vindas se existir
    hideWelcomeMessage();

    // Adiciona mensagem do usuário
    addMessage(message, "user");

    // Mostra indicador de digitação
    showTypingIndicator();

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message }),
      });

      // Remove indicador de digitação
      hideTypingIndicator();

      if (response.status === 401) {
        alert("Sessão expirada. Por favor, faça login novamente.");
        Auth.logout();
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erro ao processar mensagem");
      }

      // Extrai URLs de imagens (do campo images ou do texto)
      let imageUrls = [];
      let cleanedResponse = data.response;

      if (data.images && data.images.length > 0) {
        imageUrls = data.images.map((img) => img.url);
      } else {
        // Fallback: tenta extrair URLs de imagens do texto
        const urlPattern =
          /https:\/\/oaidalleapiprodscus\.blob\.core\.windows\.net\/[^\s\)\]"'<>]+/g;
        const matches = data.response.match(urlPattern);
        if (matches) {
          imageUrls = matches;
        }
      }

      // Se encontrou imagens, limpa URLs e markdown do texto
      if (imageUrls.length > 0) {
        // Remove markdown de imagem: ![texto](url)
        cleanedResponse = cleanedResponse.replace(
          /!\[.*?\]\(https:\/\/oaidalleapiprodscus\.blob\.core\.windows\.net\/[^)]+\)/g,
          "",
        );
        // Remove URLs soltas
        cleanedResponse = cleanedResponse.replace(
          /https:\/\/oaidalleapiprodscus\.blob\.core\.windows\.net\/[^\s<>]+/g,
          "",
        );
        // Limpa linhas vazias extras
        cleanedResponse = cleanedResponse.replace(/\n{3,}/g, "\n\n").trim();
      }

      // Adiciona resposta do assistente com imagens
      addMessage(cleanedResponse, "assistant", imageUrls);
    } catch (error) {
      hideTypingIndicator();
      addMessage(`Desculpe, ocorreu um erro: ${error.message}`, "assistant");
    }
  }

  /**
   * Limpa o histórico de conversa
   */
  async function handleClearChat() {
    const token = Auth.getToken();
    if (!token) return;

    try {
      await fetch(`${API_URL}/chat/clear`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // Limpa mensagens da interface
      clearMessages();
    } catch (error) {
      console.error("Erro ao limpar conversa:", error);
    }
  }

  /**
   * Adiciona uma mensagem ao chat
   */
  function addMessage(content, type, imageUrls = []) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    // Processa o conteúdo para HTML básico
    contentDiv.innerHTML = formatMessage(content);

    messageDiv.appendChild(contentDiv);

    // Normaliza imageUrls para array
    const urls = Array.isArray(imageUrls)
      ? imageUrls
      : imageUrls
        ? [imageUrls]
        : [];

    // Adiciona cada imagem
    urls.forEach((imageUrl) => {
      if (imageUrl) {
        const imageContainer = document.createElement("div");
        imageContainer.className = "message-image";

        const img = document.createElement("img");
        img.src = imageUrl;
        img.alt = "Visualização do ambiente";
        img.loading = "lazy";

        // Clique para abrir modal
        img.addEventListener("click", () => openImageModal(imageUrl));

        imageContainer.appendChild(img);
        messageDiv.appendChild(imageContainer);
      }
    });

    messagesContainer.appendChild(messageDiv);

    // Scroll para a última mensagem
    scrollToBottom();
  }

  /**
   * Formata a mensagem (markdown básico)
   */
  function formatMessage(content) {
    if (!content) return "";

    // Escapa HTML primeiro
    let formatted = content
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Negrito: **texto** ou __texto__
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    formatted = formatted.replace(/__(.*?)__/g, "<strong>$1</strong>");

    // Itálico: *texto* ou _texto_
    formatted = formatted.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    formatted = formatted.replace(/_([^_]+)_/g, "<em>$1</em>");

    // Listas com - ou *
    formatted = formatted.replace(/^[-*]\s+(.+)$/gm, "<li>$1</li>");
    formatted = formatted.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");

    // Listas numeradas
    formatted = formatted.replace(/^\d+\.\s+(.+)$/gm, "<li>$1</li>");

    // Quebras de linha
    formatted = formatted.replace(/\n\n/g, "</p><p>");
    formatted = formatted.replace(/\n/g, "<br>");

    // Wrap em parágrafo
    if (!formatted.startsWith("<")) {
      formatted = "<p>" + formatted + "</p>";
    }

    return formatted;
  }

  /**
   * Mostra indicador de digitação
   */
  function showTypingIndicator() {
    isTyping = true;
    sendBtn.disabled = true;

    const typingDiv = document.createElement("div");
    typingDiv.className = "typing-indicator";
    typingDiv.id = "typing-indicator";
    typingDiv.innerHTML = "<span></span><span></span><span></span>";

    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
  }

  /**
   * Esconde indicador de digitação
   */
  function hideTypingIndicator() {
    isTyping = false;
    sendBtn.disabled = false;

    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  /**
   * Esconde mensagem de boas-vindas
   */
  function hideWelcomeMessage() {
    welcomeMessage = messagesContainer.querySelector(".welcome-message");
    if (welcomeMessage) {
      welcomeMessage.remove();
    }
  }

  /**
   * Limpa todas as mensagens
   */
  function clearMessages() {
    messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="paint-palette">
                    <span style="background: #E63946;"></span>
                    <span style="background: #F4A261;"></span>
                    <span style="background: #E9C46A;"></span>
                    <span style="background: #2A9D8F;"></span>
                    <span style="background: #264653;"></span>
                </div>
                <h2>Olá! Sou seu assistente de tintas.</h2>
                <p>Posso ajudar você a:</p>
                <ul>
                    <li>Encontrar a tinta ideal para seu projeto</li>
                    <li>Calcular a quantidade necessária</li>
                    <li>Sugerir cores para cada ambiente</li>
                    <li>Visualizar como ficaria o ambiente pintado</li>
                </ul>
                <p class="hint">Experimente perguntar: "Qual tinta usar para pintar um quarto de bebê?"</p>
            </div>
        `;
  }

  /**
   * Abre modal com imagem ampliada
   */
  function openImageModal(imageUrl) {
    const modal = document.getElementById("image-modal");
    const modalImage = document.getElementById("modal-image");

    modalImage.src = imageUrl;
    modal.classList.remove("hidden");

    // Fecha modal ao clicar fora ou no botão
    modal.addEventListener("click", (e) => {
      if (e.target === modal || e.target.classList.contains("modal-close")) {
        modal.classList.add("hidden");
      }
    });

    // Fecha com ESC
    document.addEventListener("keydown", function closeOnEsc(e) {
      if (e.key === "Escape") {
        modal.classList.add("hidden");
        document.removeEventListener("keydown", closeOnEsc);
      }
    });
  }

  /**
   * Scroll suave para o final das mensagens
   */
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  /**
   * Foca no input do chat
   */
  function focusInput() {
    chatInput.focus();
  }

  // API pública
  return {
    init,
    clearMessages,
    focusInput,
  };
})();
