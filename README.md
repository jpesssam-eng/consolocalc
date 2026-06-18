# ConsoloCalc

Aplicação web open-source para dimensionamento de **consolos curtos de concreto armado** segundo a **ABNT NBR 6118:2023**, pelo método de bielas e tirantes.

Desenvolvido como Trabalho de Conclusão de Curso em Engenharia Civil — Centro Universitário Internacional UNINTER, 2026.

---

## 📋 Sobre

Ferramenta gratuita e de código aberto que automatiza o dimensionamento estrutural de consolos curtos, com:

- Classificação automática do consolo (muito curto, curto, longo)
- Cálculo das forças no tirante e na biela comprimida
- Dimensionamento das armaduras de tirante e de costura
- Verificação da biela comprimida
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

Verifique se o cálculo está funcionando com o exemplo do Araújo (2014):

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
├── consolo_calc.py       # Módulo de cálculo (funções puras)
├── teste_validacao.py    # Script de teste com caso da literatura
├── requirements.txt      # Dependências Python
└── README.md             # Este arquivo
```

---

## 📚 Referências

- ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 6118: Projeto de estruturas de concreto — Procedimento.** Rio de Janeiro: ABNT, 2023.
- ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 9062: Projeto e execução de estruturas de concreto pré-moldado.** Rio de Janeiro: ABNT, 2017.
- SIQUEIRA, R. F. **Dimensionamento automatizado de consolos curtos de concreto armado pelo método de bielas e tirantes.** TCC. UTFPR, Toledo, 2018.

---

## 📄 Licença

Distribuído sob licença MIT. Veja o arquivo `LICENSE` para mais informações.

---

## 👤 Autor

**Junior Pessoa da Silva**
Centro Universitário Internacional UNINTER — Engenharia Civil — 2026
