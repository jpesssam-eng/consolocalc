# ConsoloCalc

Aplicação web open-source para dimensionamento de **consolos curtos de concreto armado** segundo a **ABNT NBR 6118:2023**, pelo modelo de bielas e tirantes de Santos (2021).

Desenvolvido como Trabalho de Conclusão de Curso em Engenharia Civil — Centro Universitário Internacional UNINTER, 2026.

---

## 📋 Sobre

Ferramenta gratuita e de código aberto que automatiza o dimensionamento estrutural de consolos curtos, com:

- Classificação automática do consolo (muito curto, curto, longo)
- Modelo de bielas e tirantes de Santos (2021): braço de alavanca z = d − y/2 pelo equilíbrio do nó sob a carga (método rigoroso) ou z = 0,85·d (método simplificado)
- Força horizontal integralmente absorvida pelo tirante, com Hd ≥ 0,2·Vd quando há impedimento horizontal (NBR 9062:2017)
- Dimensionamento das armaduras de tirante e de costura
- Verificação do nó carregado e da ductilidade (x/d ≤ 0,4)
- Memorial em PDF, planilha Excel, CSV e análise de sensibilidade
- Interface web acessível em qualquer navegador

---

## 🚀 Como executar (passo a passo)

### 1. Instalar o Python

Baixe e instale o Python (versão 3.10 ou superior) em:
https://www.python.org/downloads/

Durante a instalação no Windows, **marque a opção "Add Python to PATH"**.

### 2. Baixar o projeto

Baixe esta pasta `consolocalc` para o seu computador.

### 3. Instalar as dependências

Abra o terminal (ou PowerShell no Windows) **dentro da pasta `consolocalc`** e execute:

```bash
pip install -r requirements.txt
```

### 4. Rodar o teste de validação

Verifique se o cálculo está funcionando com os exemplos de Santos (2021, Boxe 6.2) e de Silva e Giongo (2000):

```bash
python teste_validacao.py
```

Você deve ver um relatório comparando os resultados da ferramenta com os valores de referência da literatura.

### 5. Rodar a aplicação web

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501` com a interface gráfica.

---

## 📁 Estrutura do projeto

```
consolocalc/
├── app.py                # Interface web (Streamlit)
├── consolo_calc.py       # Módulo de cálculo (modelo de Santos, 2021)
├── visualizacao.py       # Diagrama do consolo
├── memorial_pdf.py       # Memorial de cálculo em PDF
├── exportar.py           # Exportação Excel e CSV
├── sensibilidade.py      # Análise de sensibilidade
├── pacote_completo.py    # Pacote ZIP com todos os resultados
├── teste_validacao.py    # Validação com exemplos da literatura
├── requirements.txt      # Dependências Python
└── README.md             # Este arquivo
```

---

## 📚 Referências

- ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 6118: Projeto de estruturas de concreto — Procedimento.** Rio de Janeiro: ABNT, 2023.
- ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 9062: Projeto e execução de estruturas de concreto pré-moldado.** Rio de Janeiro: ABNT, 2017.
- SANTOS, D. M. dos. **Projeto estrutural por bielas e tirantes.** São Paulo: Oficina de Textos, 2021.
- SCHLAICH, J.; SCHÄFER, K.; JENNEWEIN, M. **Toward a consistent design of structural concrete.** PCI Journal, v. 32, n. 3, p. 74-150, 1987.
- SILVA, R. C. da; GIONGO, J. S. **Modelos de bielas e tirantes aplicados a estruturas de concreto armado.** São Carlos: EESC/USP, 2000.
- SIQUEIRA, R. F. **Dimensionamento automatizado de consolos curtos de concreto armado pelo método de bielas e tirantes.** TCC. UTFPR, Toledo, 2018.

---

## 📄 Licença

Distribuído sob licença MIT. Veja o arquivo `LICENSE` para mais informações.

---

## 👤 Autor

**Junior Pessoa da Silva**
Centro Universitário Internacional UNINTER — Engenharia Civil — 2026
