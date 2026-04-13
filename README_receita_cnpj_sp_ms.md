# Receita Federal CNPJ — Extrator SP + MS

## O que faz

Baixa os arquivos oficiais da Receita Federal (~5 GB), filtra empresas de SP e MS por CNAE de interesse, e gera o arquivo `data/empresas.csv` para a aba **Empresas & Potencial** do dashboard.

## Pré-requisitos

```bash
pip install duckdb requests
```

## Como rodar

```bash
# Gera o CSV na pasta padrão (saida_receita_sp_ms/)
python build_receita_sp_ms.py

# Para mudar o diretório de saída:
python build_receita_sp_ms.py --output-dir data/

# Para manter os downloads intermediários (útil para debug):
python build_receita_sp_ms.py --keep-downloads
```

Depois copie o arquivo gerado para a pasta `data/`:

```bash
cp saida_receita_sp_ms/receita_empresas_sp_ms.csv.gz data/empresas.csv.gz
# ou descomprima:
gunzip -c saida_receita_sp_ms/receita_empresas_sp_ms.csv.gz > data/empresas.csv
```

## Aviso de tamanho

O download total é de ~5 GB (10 arquivos de Estabelecimentos + 10 de Empresas + Simples + domínios). O processamento usa DuckDB em memória — recomendado 8 GB de RAM disponível.

## Coluna `uf`

O script padrão filtra SP e MS. Se quiser incluir PR e RJ, edite `UF_ALVO_DEFAULT` no topo de `build_receita_sp_ms.py`:

```python
UF_ALVO_DEFAULT = ("SP", "MS", "PR", "RJ")
```
