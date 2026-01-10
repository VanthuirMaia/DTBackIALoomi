"""
Serviço de integração com DALL-E para geração de imagens.

Permite visualizar simulações de ambientes pintados com diferentes cores.
"""

import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class DallEService:
    """Serviço para geração de imagens com DALL-E."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Usar DALL-E 2 como padrão (mais acessível)
        # Troque para "dall-e-3" se sua conta tiver acesso
        self.model = os.getenv("DALLE_MODEL", "dall-e-2")
        self.default_size = "1024x1024"
        self.default_quality = "standard"

    def generate_room_visualization(
        self,
        ambiente: str,
        cor: str,
        estilo: Optional[str] = None,
        detalhes: Optional[str] = None
    ) -> dict:
        """
        Gera uma imagem de visualização de um ambiente pintado.

        Args:
            ambiente: Tipo de ambiente (sala, quarto, cozinha, banheiro, etc.)
            cor: Cor da tinta a ser visualizada
            estilo: Estilo de decoração (moderno, clássico, minimalista, etc.)
            detalhes: Detalhes adicionais para a imagem

        Returns:
            Dict com URL da imagem e metadados
        """
        try:
            # Constrói prompt otimizado para DALL-E
            prompt = self._build_prompt(ambiente, cor, estilo, detalhes)

            logger.info(f"Gerando imagem DALL-E: {prompt[:100]}...")

            # Monta parâmetros base
            params = {
                "model": self.model,
                "prompt": prompt,
                "size": self.default_size,
                "n": 1,
            }

            # DALL-E 3 suporta quality, DALL-E 2 não
            if self.model == "dall-e-3":
                params["quality"] = self.default_quality

            response = self.client.images.generate(**params)

            image_url = response.data[0].url
            # DALL-E 3 retorna revised_prompt, DALL-E 2 não
            revised_prompt = getattr(response.data[0], 'revised_prompt', None)

            logger.info(f"Imagem gerada com sucesso: {image_url[:50]}...")

            return {
                "success": True,
                "image_url": image_url,
                "prompt_used": prompt,
                "revised_prompt": revised_prompt,
                "ambiente": ambiente,
                "cor": cor,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Erro ao gerar imagem DALL-E: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ambiente": ambiente,
                "cor": cor
            }

    def _build_prompt(
        self,
        ambiente: str,
        cor: str,
        estilo: Optional[str] = None,
        detalhes: Optional[str] = None
    ) -> str:
        """
        Constrói um prompt otimizado para gerar imagens de ambientes pintados.

        Args:
            ambiente: Tipo de ambiente
            cor: Cor da tinta
            estilo: Estilo de decoração
            detalhes: Detalhes adicionais

        Returns:
            Prompt otimizado para DALL-E
        """
        # Mapeia ambientes para descrições mais detalhadas
        ambientes_map = {
            "sala": "sala de estar aconchegante com sofá e decoração",
            "quarto": "quarto de dormir elegante com cama e mobília",
            "cozinha": "cozinha moderna com armários e bancada",
            "banheiro": "banheiro clean com espelho e iluminação",
            "escritório": "escritório home office com mesa e estante",
            "varanda": "varanda espaçosa com plantas",
            "área externa": "área externa com jardim",
            "lavanderia": "área de serviço organizada",
            "corredor": "corredor iluminado",
            "quarto de bebê": "quarto infantil delicado com berço",
            "quarto infantil": "quarto de criança colorido e alegre",
        }

        ambiente_desc = ambientes_map.get(
            ambiente.lower(),
            f"{ambiente} bem decorado"
        )

        # Estilo padrão
        estilo_desc = estilo if estilo else "moderno e contemporâneo"

        # Constrói o prompt base
        prompt = (
            f"Fotografia profissional de interior de {ambiente_desc}, "
            f"paredes pintadas na cor {cor}, "
            f"estilo de decoração {estilo_desc}, "
            f"iluminação natural suave, "
            f"fotorrealista, alta qualidade, "
            f"arquitetura residencial brasileira"
        )

        # Adiciona detalhes extras se fornecidos
        if detalhes:
            prompt += f", {detalhes}"

        return prompt


# Singleton para o serviço
_dalle_service: Optional[DallEService] = None


def get_dalle_service() -> DallEService:
    """Retorna instância singleton do DallEService."""
    global _dalle_service
    if _dalle_service is None:
        _dalle_service = DallEService()
    return _dalle_service
