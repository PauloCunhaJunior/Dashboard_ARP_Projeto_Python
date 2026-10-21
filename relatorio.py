"""Relatório executivo HTML para visualizar, salvar e imprimir."""

from datetime import datetime
from html import escape


def formatar_data(iso):
    if not iso:
        return "Não disponível"
    return datetime.fromisoformat(iso).strftime("%d/%m/%Y às %H:%M:%S")


def texto_executivo(registro, historico, ficticio=False):
    modo = "DADOS FICTÍCIOS DE DEMONSTRAÇÃO" if ficticio else "DADOS DA TABELA ARP LOCAL"
    return (
        f"Fonte: {modo}. A associação IPv4 {registro['ip']} ↔ MAC {registro['mac']} "
        f"foi observada em {historico['quantidade_coletas']} coleta(s) gravada(s), "
        f"entre {formatar_data(historico['primeira_vez'])} e "
        f"{formatar_data(historico['ultima_vez'])}. "
        "Esse registro não comprova que o dispositivo esteja ligado agora, "
        "nem revela por si só seu nome, responsável, sistema operacional ou segurança."
    )


def gerar_html(registro, historico, ficticio=False):
    """Cria HTML com CSS incorporado, pronto para abrir e imprimir em PDF."""
    resumo = texto_executivo(registro, historico, ficticio)
    campos = [
        ("Endereço IPv4", registro["ip"]),
        ("Endereço MAC", registro["mac"]),
        ("Tipo de associação", registro["tipo"]),
        ("Interface local de origem", registro["interface"]),
        ("Primeira observação gravada", formatar_data(historico["primeira_vez"])),
        ("Última observação gravada", formatar_data(historico["ultima_vez"])),
        ("Quantidade de coletas com a associação", historico["quantidade_coletas"]),
    ]
    linhas = "\n".join(
        f"<tr><th>{escape(str(titulo))}</th><td>{escape(str(valor))}</td></tr>"
        for titulo, valor in campos
    )
    titulo = f"Relatório executivo de ARP — {registro['ip']}"
    rotulo = "DEMONSTRAÇÃO — DADOS FICTÍCIOS" if ficticio else "MONITORAMENTO ARP LOCAL"
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(titulo)}</title>
<style>
body {{ background:#f3f6fa; color:#243044; font:16px/1.6 'Segoe UI',Arial,sans-serif; margin:0; }}
main {{ max-width:840px; margin:32px auto; padding:40px; background:#fff;
        border-radius:15px; box-shadow:0 8px 30px #00000011; }}
header {{ border-bottom:3px solid #127ca7; padding-bottom:18px; margin-bottom:30px; }}
h1 {{ font-size:28px; line-height:1.2; margin:8px 0; color:#103755; }}
h2 {{ font-size:19px; color:#103755; margin-top:28px; }}
small {{ color:#477188; font-weight:bold; letter-spacing:.1em; }}
table {{ width:100%; border-collapse:collapse; margin-top:14px; }}
th,td {{ padding:11px 12px; border-bottom:1px solid #dbe6ec; text-align:left; }}
th {{ width:45%; background:#f6fafc; font-weight:600; }}
.nota {{ background:#f1f7fb; border-left:4px solid #127ca7; padding:14px 18px; }}
footer {{ font-size:13px; color:#657789; border-top:1px solid #dbe6ec; padding-top:15px; margin-top:36px; }}
@media print {{ body {{ background:#fff; }} main {{ margin:0; box-shadow:none; padding:6mm; }} }}
</style>
</head>
<body>
<main>
<header><small>{escape(rotulo)}</small><h1>{escape(titulo)}</h1>
<p>Relatório de observação de associações IPv4–MAC</p></header>
<h2>1. Resumo executivo</h2><p class="nota">{escape(resumo)}</p>
<h2>2. Identificação e histórico</h2><table>{linhas}</table>
<h2>3. Interpretação e próximos passos</h2>
<p>O dado foi obtido da tabela ARP do computador que executou a consulta.
O endereço MAC identifica uma interface de rede, mas não identifica de modo confiável
uma pessoa ou um equipamento específico. Se for necessário confirmar a identidade
do ativo, compare-o com o inventário autorizado da rede.</p>
<footer>Relatório local gerado pelo Dashboard ARP. A leitura ARP não é uma varredura
completa da rede e não comprova disponibilidade em tempo real.</footer>
</main></body></html>"""
