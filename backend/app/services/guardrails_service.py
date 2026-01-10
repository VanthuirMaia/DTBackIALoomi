"""
Servico de Guardrails para seguranca do agente de IA.

Implementa validacoes de input/output para garantir comportamento seguro e adequado.
"""

import re
import logging
from typing import Tuple
from enum import Enum

# Configuracao de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GuardrailViolationType(Enum):
    """Tipos de violacao de guardrails."""
    PROMPT_INJECTION = "prompt_injection"
    OFF_TOPIC = "off_topic"
    BLOCKED_PATTERN = "blocked_pattern"
    INAPPROPRIATE_OUTPUT = "inappropriate_output"


class GuardrailViolation(Exception):
    """Excecao customizada para violacoes de guardrails."""

    def __init__(self, violation_type: GuardrailViolationType, message: str, original_input: str = ""):
        self.violation_type = violation_type
        self.message = message
        self.original_input = original_input
        super().__init__(message)


class GuardrailsService:
    """
    Servico de guardrails para validacao de inputs e outputs do agente.

    Implementa:
    - Deteccao de prompt injection
    - Filtragem de padroes bloqueados
    - Validacao de topico (foco em tintas)
    - Validacao de output
    """

    # Padroes de prompt injection conhecidos
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|above|prior|your)?\s*(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|above|prior|your)?\s*(instructions?|prompts?|rules?)",
        r"forget\s+(all\s+)?(previous|above|prior|your)?\s*(instructions?|prompts?|rules?)",
        r"ignore\s+.*?(system\s+prompt|instructions?)",
        r"you\s+are\s+now\s+(a|an)\s+(?!assistente|especialista)",
        r"pretend\s+(you\s+are|to\s+be)",
        r"act\s+as\s+(if\s+you\s+are|a\s+different)",
        r"new\s+instructions?:",
        r"override\s+(previous\s+)?instructions?",
        r"jailbreak",
        r"DAN\s+mode",
        r"\[system\]",
        r"\[admin\]",
        r"<\s*system\s*>",
        r"sudo\s+",
        r"execute\s+(code|command|script)",
    ]

    # Padroes de conteudo bloqueado
    BLOCKED_CONTENT_PATTERNS = [
        r"(hack|hacker|hacking)",
        r"(malware|virus|trojan)",
        r"(armas?|weapons?|guns?)",
        r"(drogas?|drugs?|cocaine|marijuana)",
        r"(explosivos?|bomb|explosive)",
        r"(terroris[mt]|attack)",
        r"(matar|kill|murder)",
        r"(roubar|steal|robbery)",
        r"(pornografia|porn|xxx)",
        r"(nude|naked|sex)",
    ]

    # Palavras-chave relacionadas ao dominio de tintas
    DOMAIN_KEYWORDS = [
        "tinta", "tintas", "pintar", "pintura", "pintando",
        "cor", "cores", "colorido", "colorida",
        "parede", "paredes", "superficie",
        "suvinil", "premium", "economica", "standard",
        "litros", "latas", "galao", "galoes",
        "demao", "demaos", "cobertura", "rendimento",
        "acabamento", "fosco", "acetinado", "brilhante", "semi-brilho",
        "interno", "externo", "ambiente", "quarto", "sala", "cozinha", "banheiro",
        "fachada", "muro", "teto", "madeira", "metal", "gesso", "piso",
        "latex", "acrilica", "esmalte", "verniz",
        "branco", "azul", "verde", "amarelo", "vermelho", "cinza", "bege", "marrom",
        "preco", "custo", "orcamento", "quantidade", "calcular", "calculadora",
        "recomenda", "recomendacao", "sugestao", "melhor", "ideal",
        "resistente", "lavavel", "anti-mofo", "impermeavel", "secagem",
        "ola", "oi", "bom dia", "boa tarde", "boa noite", "obrigado", "obrigada",
        "ajuda", "ajudar", "duvida", "pergunta", "produto", "produtos",
        "catalogo", "opcoes", "disponivel", "disponivel",
    ]

    # Saudacoes e interacoes basicas permitidas
    GREETING_PATTERNS = [
        r"^(oi|ola|hey|hi|hello|e\s*ai)\b",
        r"^bom\s+dia\b",
        r"^boa\s+(tarde|noite)\b",
        r"^obrigad[oa]\b",
        r"^tchau\b",
        r"^ate\s+(logo|mais)\b",
    ]

    def __init__(self):
        """Inicializa o servico de guardrails."""
        # Compila padroes regex para melhor performance
        self._injection_regex = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._blocked_regex = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_CONTENT_PATTERNS]
        self._greeting_regex = [re.compile(p, re.IGNORECASE) for p in self.GREETING_PATTERNS]
        self._domain_keywords_lower = [kw.lower() for kw in self.DOMAIN_KEYWORDS]

    def validate_input(self, user_input: str) -> Tuple[bool, str]:
        """
        Valida o input do usuario.

        Args:
            user_input: Texto enviado pelo usuario

        Returns:
            Tuple (is_valid, message)

        Raises:
            GuardrailViolation: Se uma violacao grave for detectada
        """
        if not user_input or not user_input.strip():
            return False, "Mensagem vazia nao e permitida."

        user_input_clean = user_input.strip()

        # 1. Verifica prompt injection
        injection_detected = self._check_prompt_injection(user_input_clean)
        if injection_detected:
            self._log_violation(GuardrailViolationType.PROMPT_INJECTION, user_input_clean)
            raise GuardrailViolation(
                GuardrailViolationType.PROMPT_INJECTION,
                "Desculpe, nao posso processar esse tipo de solicitacao.",
                user_input_clean
            )

        # 2. Verifica conteudo bloqueado
        blocked = self._check_blocked_content(user_input_clean)
        if blocked:
            self._log_violation(GuardrailViolationType.BLOCKED_PATTERN, user_input_clean)
            raise GuardrailViolation(
                GuardrailViolationType.BLOCKED_PATTERN,
                "Desculpe, nao posso ajudar com esse tipo de assunto.",
                user_input_clean
            )

        # 3. Verifica se e saudacao (sempre permitido)
        if self._is_greeting(user_input_clean):
            return True, "OK"

        # 4. Verifica se esta no topico (tintas)
        is_on_topic = self._check_topic_relevance(user_input_clean)
        if not is_on_topic:
            self._log_violation(GuardrailViolationType.OFF_TOPIC, user_input_clean, level="warning")
            return False, "off_topic"

        return True, "OK"

    def validate_output(self, agent_output: str) -> Tuple[bool, str]:
        """
        Valida o output do agente.

        Args:
            agent_output: Resposta gerada pelo agente

        Returns:
            Tuple (is_valid, sanitized_output ou mensagem de erro)
        """
        if not agent_output:
            return False, "Desculpe, nao consegui gerar uma resposta."

        # Verifica se o output contem conteudo bloqueado
        if self._check_blocked_content(agent_output):
            self._log_violation(
                GuardrailViolationType.INAPPROPRIATE_OUTPUT,
                agent_output[:200],
                level="error"
            )
            return False, "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, reformule sua pergunta."

        # Verifica se o agente esta tentando "sair do personagem"
        persona_breaks = [
            r"como\s+um\s+modelo\s+de\s+linguagem",
            r"como\s+uma?\s+IA",
            r"nao\s+tenho\s+(sentimentos|emocoes|opiniao)",
            r"fui\s+treinado\s+(por|pela)\s+(openai|anthropic|google)",
        ]

        for pattern in persona_breaks:
            if re.search(pattern, agent_output, re.IGNORECASE):
                self._log_violation(
                    GuardrailViolationType.INAPPROPRIATE_OUTPUT,
                    f"Persona break detected: {agent_output[:100]}",
                    level="warning"
                )
                # Nao bloqueia, apenas loga (pode ser resposta legitima)
                break

        return True, agent_output

    def get_off_topic_response(self) -> str:
        """Retorna mensagem padrao para perguntas fora do topico."""
        return (
            "Desculpe, sou um assistente especializado em tintas Suvinil. "
            "Posso ajudar voce com:\n\n"
            "- Recomendacoes de tintas para seu projeto\n"
            "- Informacoes sobre cores, acabamentos e linhas de produtos\n"
            "- Calculo de quantidade de tinta necessaria\n"
            "- Dicas sobre tipos de superficie e ambientes\n\n"
            "Como posso ajudar com sua pintura?"
        )

    def _check_prompt_injection(self, text: str) -> bool:
        """Verifica se o texto contem tentativas de prompt injection."""
        for pattern in self._injection_regex:
            if pattern.search(text):
                return True
        return False

    def _check_blocked_content(self, text: str) -> bool:
        """Verifica se o texto contem conteudo bloqueado."""
        for pattern in self._blocked_regex:
            if pattern.search(text):
                return True
        return False

    def _is_greeting(self, text: str) -> bool:
        """Verifica se o texto e uma saudacao."""
        text_lower = text.lower().strip()
        for pattern in self._greeting_regex:
            if pattern.match(text_lower):
                return True
        return False

    def _check_topic_relevance(self, text: str) -> bool:
        """
        Verifica se o texto esta relacionado ao dominio de tintas.

        Usa uma abordagem simples de keywords para evitar
        latencia adicional de chamadas ao LLM.
        """
        text_lower = text.lower()

        # Verifica se alguma keyword do dominio esta presente
        for keyword in self._domain_keywords_lower:
            if keyword in text_lower:
                return True

        # Perguntas muito curtas podem ser ambiguas, permitir
        if len(text.split()) <= 3:
            return True

        return False

    def _log_violation(
        self,
        violation_type: GuardrailViolationType,
        content: str,
        level: str = "warning"
    ) -> None:
        """Registra uma violacao de guardrails no log."""
        log_message = f"[GUARDRAIL] {violation_type.value}: {content[:100]}..."

        if level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)


# Instancia singleton
_guardrails_service = None


def get_guardrails_service() -> GuardrailsService:
    """Retorna instancia singleton do GuardrailsService."""
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService()
    return _guardrails_service
