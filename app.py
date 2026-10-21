"""Dashboard ARP: monitoramento local, seleção de linhas e relatório executivo."""

import hashlib
import time

import pandas as pd
import streamlit as st

from banco import inicializar_banco, obter_historico, salvar_coleta, ultima_coleta
from rede import dados_demonstracao, executar_arp
from relatorio import formatar_data, gerar_html, texto_executivo

st.set_page_config(page_title="Dashboard ARP", page_icon="🖥️", layout="wide")
inicializar_banco()

st.title("🖥️ Dashboard de Monitoramento ARP")
st.caption("Visualização local das associações IPv4 e MAC obtidas pelo comando arp -a")

with st.sidebar:
    st.header("Configurações")
    modo_demo = st.toggle("Modo de demonstração (dados fictícios)", value=False)
    st.write("**Frequência:** 60 segundos")
    st.info("A atualização automática funciona enquanto esta página estiver aberta e conectada.")
    st.caption("As coletas são salvas no arquivo local historico_arp.sqlite3.")

fonte = "demo" if modo_demo else "real"
if modo_demo:
    st.warning("MODO DEMONSTRAÇÃO ATIVO — os IPs e MACs exibidos são fictícios.")
else:
    st.info("**Leitura real:** esta aplicação consulta a tabela ARP do computador em que o Python está rodando.")


@st.fragment(run_every=60)
def painel():
    # O clique em uma linha ou em um filtro reexecuta este bloco.
    # O relógio abaixo impede que cada clique dispare uma nova consulta ARP.
    chave_tempo = f"ultima_execucao_{fonte}"
    chave_erro = f"ultimo_erro_{fonte}"
    atualizar_agora = st.button("🔄 Executar nova consulta agora", key=f"atualizar_{fonte}")
    agora = time.monotonic()
    ultima_execucao = st.session_state.get(chave_tempo)
    deve_coletar = (
        atualizar_agora
        or ultima_execucao is None
        or agora - ultima_execucao >= 60
    )

    if deve_coletar:
        st.session_state[chave_tempo] = agora
        try:
            registros_lidos = dados_demonstracao() if modo_demo else executar_arp()
            salvar_coleta(registros_lidos, fonte)
            st.session_state[chave_erro] = ""
        except (RuntimeError, OSError) as erro:
            st.session_state[chave_erro] = str(erro)

    erro_atual = st.session_state.get(chave_erro, "")
    if erro_atual:
        st.error(f"Não foi possível fazer a nova leitura: {erro_atual}")
        st.caption("Se houver dados antigos, eles aparecem abaixo identificados pela data da última coleta.")

    coleta, registros = ultima_coleta(fonte)
    if coleta is None:
        st.info("Ainda não há nenhuma coleta gravada neste modo.")
        return

    horario = formatar_data(coleta["momento"])
    st.caption(f"**Última coleta salva:** {horario} — {coleta['total']} registros")
    dinamicos = sum(r["tipo"] == "Dinâmico" for r in registros)
    estaticos = sum(r["tipo"] == "Estático" for r in registros)
    outros = len(registros) - dinamicos - estaticos
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros ARP", len(registros))
    col2.metric("Dinâmicos", dinamicos)
    col3.metric("Estáticos", estaticos)
    col4.metric("Interfaces locais", len({r["interface"] for r in registros}))

    if not registros:
        st.warning(
            "Nenhuma associação IPv4 unicast foi encontrada nesta coleta. "
            "Isso não significa que não existam dispositivos na rede."
        )
        return

    esquerda, direita = st.columns([2, 1])
    with esquerda:
        st.subheader("Associações encontradas")
        filtro = st.text_input(
            "Filtrar por IP ou MAC", placeholder="Ex.: 192.168.1 ou AA-BB",
            key=f"filtro_{fonte}",
        ).strip().lower()
        filtrados = [
            r for r in registros
            if filtro in r["ip"].lower() or filtro in r["mac"].lower()
        ]
        if not filtrados:
            st.warning("Nenhum registro corresponde ao filtro informado.")
            return

        tabela = pd.DataFrame(filtrados).rename(columns={
            "interface": "Interface local", "ip": "IP", "mac": "MAC", "tipo": "Tipo"
        })
        # Ao mudar a coleta/filtro, a seleção reinicia para não apontar
        # por engano para outro IP que passou a ocupar a mesma linha.
        id_filtro = hashlib.sha256(filtro.encode("utf-8")).hexdigest()[:10]
        evento = st.dataframe(
            tabela[["IP", "MAC", "Tipo", "Interface local"]],
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"tabela_{fonte}_{coleta['id']}_{id_filtro}",
        )
        st.caption("Clique em uma linha da tabela para gerar o relatório executivo.")

    with direita:
        st.subheader("Distribuição por tipo")
        quantidades = pd.Series(
            {"Dinâmico": dinamicos, "Estático": estaticos, "Outros": outros},
            name="Quantidade",
        )
        st.bar_chart(quantidades)

    if evento.selection.rows:
        indice = evento.selection.rows[0]
        selecionado = filtrados[indice]
        historico = obter_historico(selecionado["ip"], selecionado["mac"], fonte)
        st.divider()
        st.subheader(f"📄 Relatório executivo — {selecionado['ip']}")
        st.write(texto_executivo(selecionado, historico, modo_demo))
        a, b, c = st.columns(3)
        a.metric("Tipo de associação", selecionado["tipo"])
        b.metric("Observações gravadas", historico["quantidade_coletas"])
        c.metric("Interface local", selecionado["interface"])
        st.write(f"**MAC:** `{selecionado['mac']}`")
        st.write(f"**Primeira observação:** {formatar_data(historico['primeira_vez'])}")
        st.write(f"**Última observação:** {formatar_data(historico['ultima_vez'])}")
        html = gerar_html(selecionado, historico, modo_demo)
        nome_arquivo = f"relatorio_arp_{selecionado['ip'].replace('.', '_')}.html"
        st.download_button(
            "📥 Baixar relatório executivo (HTML para impressão/PDF)",
            data=html.encode("utf-8"),
            file_name=nome_arquivo,
            mime="text/html",
            key=f"baixar_{fonte}_{selecionado['ip']}_{coleta['id']}",
        )
        st.caption("Abra o arquivo baixado no navegador e pressione Ctrl + P para salvar como PDF.")


painel()
st.divider()
st.caption(
    "Projeto didático. Os registros ARP representam associações armazenadas no cache "
    "local, e não um scanner de toda a rede."
)
