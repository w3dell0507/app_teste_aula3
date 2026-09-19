from dataclasses import dataclass
from typing import Optional
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Simulador de Crédito",
    page_icon="🏍️",
    layout="centered"
)

# Constantes de negócio
LIMITE_COMPROMETIMENTO_RENDA = 0.30
IDADE_MINIMA = 18


@dataclass(frozen=True)
class DadosSolicitacao:
    """Dados informados pelo solicitante no formulário."""
    idade: int
    renda_mensal: float
    parcela_desejada: float


@dataclass(frozen=True)
class ResultadoAnalise:
    """Resultado da análise de crédito, pronto para exibição."""
    aprovado: bool
    status: str
    motivo: str
    parcela_maxima_recomendada: Optional[float] = None
    percentual_comprometido: Optional[float] = None


class DadosInvalidosError(ValueError):
    """Levantado quando os dados de entrada não são válidos."""


def validar_dados(dados: DadosSolicitacao) -> None:
    """Valida os dados de entrada antes de qualquer cálculo."""
    if dados.idade < 0:
        raise DadosInvalidosError("Idade não pode ser negativa.")
    if dados.renda_mensal < 0:
        raise DadosInvalidosError("Renda mensal não pode ser negativa.")
    if dados.parcela_desejada < 0:
        raise DadosInvalidosError("Valor da parcela não pode ser negativo.")


def calcular_parcela_maxima(renda_mensal: float) -> float:
    """Calcula a parcela máxima permitida para uma renda mensal."""
    return round(renda_mensal * LIMITE_COMPROMETIMENTO_RENDA, 2)


def analisar_credito(dados: DadosSolicitacao) -> ResultadoAnalise:
    """Aplica as regras de negócio, em ordem, e retorna o resultado."""
    validar_dados(dados)

    if dados.idade < IDADE_MINIMA:
        return ResultadoAnalise(
            aprovado=False,
            status="CRÉDITO NEGADO",
            motivo="É necessário ter pelo menos 18 anos para solicitar financiamento.",
        )

    parcela_maxima = calcular_parcela_maxima(dados.renda_mensal)
    percentual_comprometido = (
        round((dados.parcela_desejada / dados.renda_mensal) * 100, 1)
        if dados.renda_mensal > 0
        else float("inf")
    )

    if dados.parcela_desejada <= parcela_maxima:
        return ResultadoAnalise(
            aprovado=True,
            status="CRÉDITO APROVADO! 🎉",
            motivo="A parcela cabe confortavelmente no seu orçamento mensal.",
            parcela_maxima_recomendada=parcela_maxima,
            percentual_comprometido=percentual_comprometido,
        )

    return ResultadoAnalise(
        aprovado=False,
        status="CRÉDITO NEGADO",
        motivo="O valor da parcela compromete mais de 30% da sua renda mensal.",
        parcela_maxima_recomendada=parcela_maxima,
        percentual_comprometido=percentual_comprometido,
    )


# Interface Streamlit
def main():
    st.title("🏍️ Simulador de Financiamento de Moto")
    st.markdown("Consulte instantaneamente a viabilidade do seu crédito bancário:")

    with st.form("form_simulacao"):
        idade = st.number_input("Sua Idade", min_value=0, max_value=120, value=22, step=1)
        renda_mensal = st.number_input("Renda Mensal (R$)", min_value=0.0, value=2200.0, step=100.0)
        parcela_desejada = st.number_input("Valor da Parcela Desejada (R$)", min_value=0.0, value=480.0, step=50.0)
        
        btn_simular = st.form_submit_button("Simular Crédito", use_container_width=True)

    if btn_simular:
        try:
            dados = DadosSolicitacao(
                idade=idade, 
                renda_mensal=renda_mensal, 
                parcela_desejada=parcela_desejada
            )
            resultado = analisar_credito(dados)

            st.divider()

            if resultado.aprovado:
                st.success(f"### {resultado.status}")
                st.write(f"**Motivo:** {resultado.motivo}")
                st.info(f"📊 **Comprometimento de Renda:** {resultado.percentual_comprometido}%")
            else:
                st.error(f"### {resultado.status}")
                st.write(f"**Motivo:** {resultado.motivo}")
                
                if resultado.parcela_maxima_recomendada is not None:
                    st.warning(
                        f"💡 **Sugestão:** Para obter a aprovação, ajuste o valor da parcela para no máximo **R$ {resultado.parcela_maxima_recomendada:.2f}**."
                    )

        except DadosInvalidosError as e:
            st.error(f"Erro nos dados inseridos: {e}")


if __name__ == "__main__":
    main()