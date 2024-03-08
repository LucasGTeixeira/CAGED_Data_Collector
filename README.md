## Objetivos
Esse repositório é uma ferramenta de coleta de dados da base de dados pública CAGED. O objetivo desse crawler é obter os dados disponíveis na plataforma de maneira dinâmica, que seja necessário o processo manual de navegação entre os campos da página.

## Features
Atualmente esse repositório armazena duas versões do script, uma versão que coleta os dados agrupados por mês com a somatória dos dados ocupacionais presente na branch: ``feature/parallelization`` e uma outra versão que extrai os dados específicos com detalhes de CBO de cada uma das profssões registradas na base na branch: ``master``

## Como rodar
### Requisitos
Certifique-se de ter o Python instalado em sua máquina. Recomenda-se a versão 3.5 ou superior.

### Instale o pip
Se você ainda não tiver o pip instalado, siga as instruções em 
[pip.pypa.io](https://pip.pypa.io/en/stable/installation/) para realizar a instalação.

### Instale os pacotes necessários via requirements.txt
No diretório raiz do projeto, instale as dependências necessárias executando o seguinte comando no terminal:
```bash
pip install -r requirements.txt
```

## Executando o Script
Para executar o programa, utilize o seguinte comando no terminal:
```bash
python3 ./main.py
```
