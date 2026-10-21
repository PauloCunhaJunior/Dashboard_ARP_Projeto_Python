"""Execução do comando ARP e interpretação das entradas IPv4 no Windows."""

import ipaddress
import os
import re
import subprocess
import unicodedata

# O Windows normalmente apresenta o MAC separado por hífens.
PADRAO_LINHA = re.compile(
    r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+"
    r"([0-9a-fA-F]{2}(?:[-:][0-9a-fA-F]{2}){5})\s+(.+?)\s*$"
)
PADRAO_INTERFACE = re.compile(
    r"^\s*interface\s*:\s*(\d{1,3}(?:\.\d{1,3}){3})",
    flags=re.IGNORECASE,
)


def identificar_tipo(texto):
    sem_acentos = unicodedata.normalize("NFKD", texto.strip().lower())
    sem_acentos = "".join(
        caractere for caractere in sem_acentos
        if not unicodedata.combining(caractere)
    )
    # Aceita Windows em português, inglês e alguns terminais com acentos alterados.
    if sem_acentos.startswith(("din", "dyn")):
        return "Dinâmico"
    if sem_acentos.startswith(("est", "sta")):
        return "Estático"
    return "Não identificado"


def interpretar_arp(texto):
    """Transforma a saída textual de 'arp -a' em uma lista de registros."""
    interface_atual = "Não identificada"
    registros = []
    vistos = set()

    for linha in texto.splitlines():
        resultado_interface = PADRAO_INTERFACE.match(linha)
        if resultado_interface:
            interface_atual = resultado_interface.group(1)
            continue

        resultado = PADRAO_LINHA.match(linha)
        if not resultado:
            continue

        ip_str, mac, tipo_bruto = resultado.groups()
        try:
            endereco = ipaddress.IPv4Address(ip_str)
        except ipaddress.AddressValueError:
            continue

        # Multicast, loopback e broadcast não são máquinas selecionáveis.
        if (
            endereco.is_multicast
            or endereco.is_loopback
            or endereco.is_unspecified
            or ip_str == "255.255.255.255"
        ):
            continue

        registro = {
            "interface": interface_atual,
            "ip": str(endereco),
            "mac": mac.replace(":", "-").upper(),
            "tipo": identificar_tipo(tipo_bruto),
        }
        chave = tuple(registro.values())
        if chave not in vistos:
            vistos.add(chave)
            registros.append(registro)

    return sorted(registros, key=lambda item: (item["interface"], ipaddress.IPv4Address(item["ip"])))


def executar_arp():
    """Executa o ARP no computador local e devolve entradas interpretadas."""
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        resultado = subprocess.run(
            ["arp", "-a"],
            capture_output=True,
            timeout=12,
            check=False,
            creationflags=flags,
        )
    except FileNotFoundError as erro:
        raise RuntimeError(
            "O comando 'arp' não foi encontrado. Execute o projeto no Windows com ARP disponível."
        ) from erro
    except subprocess.TimeoutExpired as erro:
        raise RuntimeError("O comando 'arp -a' demorou demais para responder.") from erro
    except OSError as erro:
        raise RuntimeError(f"Não foi possível executar 'arp -a': {erro}") from erro

    # UTF-8 é usado em terminais modernos; CP850 é comum no CMD em português.
    try:
        texto = resultado.stdout.decode("utf-8")
    except UnicodeDecodeError:
        texto = resultado.stdout.decode("cp850", errors="replace")
    if resultado.returncode != 0:
        mensagem = resultado.stderr.decode("cp850", errors="replace").strip()
        raise RuntimeError(f"Falha no ARP (código {resultado.returncode}). {mensagem}")

    return interpretar_arp(texto)


def dados_demonstracao():
    """Dados FICTÍCIOS para testar o visual, sem consultar a rede."""
    exemplo = """\
Interface: 192.168.1.100 --- 0x8
  Endereço IP         Endereço físico       Tipo
  192.168.1.1        AA-BB-CC-10-20-01     dinâmico
  192.168.1.20       AA-BB-CC-10-20-02     dinâmico
  192.168.1.30       AA-BB-CC-10-20-03     dinâmico
  192.168.1.40       AA-BB-CC-10-20-04     estático
  224.0.0.22         01-00-5E-00-00-16     estático
  255.255.255.255    FF-FF-FF-FF-FF-FF     estático
"""
    return interpretar_arp(exemplo)
