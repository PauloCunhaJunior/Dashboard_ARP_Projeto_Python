# Dashboard ARP (projeto didático)

Monitor das entradas IPv4 ↔ MAC do comando `arp -a`, desenvolvido com **Python + Streamlit + SQLite**.

## 1. Requisitos do professor

1. Executar `arp -a` automaticamente a cada **60 segundos**, com a página aberta.
2. Organizar os resultados em **dashboard** com indicadores, tabela e gráfico.
3. **Clicar em uma linha** da tabela para apresentar um relatório executivo, com opção de baixar um arquivo HTML imprimível em PDF.

## 2. Iniciar no Windows usando o VS Code

1. Instale o Python 3.10 ou superior e o Visual Studio Code.
2. Extraia este ZIP e abra a **pasta `dashboard_arp`** no VS Code: **Arquivo → Abrir Pasta**.
3. Abra o **Terminal → Novo Terminal** (PowerShell).
4. Execute, na ordem:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
   ```

   Se `py` não funcionar, tente `python -m venv .venv` na primeira linha.

5. No navegador, acesse o endereço apresentado no terminal (normalmente `http://localhost:8501`).
6. Clique em uma linha da tabela para ver o relatório. O HTML pode ser aberto no navegador e impresso/salvo como PDF com **Ctrl+P**.
7. Depois da primeira instalação, você também pode abrir o painel com um duplo clique em `iniciar_dashboard.bat`.

> Não é necessário ativar o ambiente `.venv` no PowerShell: os comandos já usam o executável Python do ambiente. Não é necessário executar como administrador.

## 3. Teste sem depender da rede

Marque **Modo de demonstração (dados fictícios)**, na barra lateral. O painel utilizará quatro registros de exemplo, identificados claramente como fictícios. Desmarque para ler os dados reais do computador.

Para ver o ARP fora do painel, abra o Prompt de Comando e execute:

```cmd
arp -a
```

Se houver pouca informação, você pode acessar um endereço já conhecido da sua própria rede, como o endereço do seu roteador obtido pelo `ipconfig` (Gateway Padrão), e então repetir `arp -a`.

## 4. Arquivos do projeto

- `app.py`: tela, gráficos, seleção de linha e agendamento de atualização.
- `rede.py`: execução e interpretação da saída do comando `arp -a`.
- `banco.py`: gravação e leitura das observações em banco SQLite local.
- `relatorio.py`: criação do resumo executivo e arquivo HTML para impressão.
- `tests/test_projeto.py`: testes da interpretação ARP, banco e relatório.
- `requirements.txt`: bibliotecas Python necessárias.
- `iniciar_dashboard.bat`: inicia o painel após a instalação inicial.

O arquivo `historico_arp.sqlite3` é criado automaticamente na pasta do projeto. Ele contém IPs e MACs observados, por isso **não publique esse banco no GitHub**. O arquivo `.gitignore` já o exclui.

## 5. Como explicar ao professor

> O sistema executa o comando `arp -a` no Windows a cada 60 segundos, enquanto o dashboard permanece aberto. O Python converte a saída em registros estruturados, que são armazenados no banco SQLite. O Streamlit apresenta a tabela, os indicadores e o gráfico. Ao selecionar uma linha, consulta o histórico da associação IP–MAC e gera um relatório executivo, que pode ser salvo e impresso.

## 6. Limitações importantes

- O ARP **não encontra necessariamente todos os computadores** da rede; mostra apenas o cache ARP disponível no computador local.
- A presença no cache **não comprova** que o dispositivo está ligado naquele momento.
- O comando `arp -a` não entrega, por si só, o nome do equipamento, usuário, fabricante ou sistema operacional.
- A coleta automática ocorre **com a página aberta**. Não há serviço em segundo plano quando a aplicação não está em execução/conectada.
- Se houver mais de um visitante com o painel aberto, cada sessão poderá realizar coletas, o que pode gerar mais de um registro por minuto no histórico. Para atividade acadêmica local, use uma única aba.
- O servidor é configurado para responder apenas em `127.0.0.1`, não sendo exposto à rede por padrão.

## 7. Testes automáticos (opcional)

Dentro da pasta do projeto, execute:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
