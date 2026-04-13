
from __future__ import annotations
import argparse
import csv
import gzip
import io
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

import duckdb

SNAPSHOT_DEFAULT = "2026-01"
BASE_ROOT = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj"

UF_ALVO_DEFAULT = ("SP", "MS")

ESTAB_COLS = [
    "cnpj_basico", "cnpj_ordem", "cnpj_dv", "identificador_matriz_filial",
    "nome_fantasia", "situacao_cadastral", "data_situacao_cadastral",
    "motivo_situacao_cadastral", "nome_cidade_exterior", "pais",
    "data_inicio_atividade", "cnae_fiscal_principal", "cnae_fiscal_secundaria",
    "tipo_logradouro", "logradouro", "numero", "complemento", "bairro", "cep",
    "uf", "municipio", "ddd1", "telefone1", "ddd2", "telefone2", "ddd_fax",
    "fax", "correio_eletronico", "situacao_especial", "data_situacao_especial"
]

EMP_COLS = [
    "cnpj_basico", "razao_social", "natureza_juridica",
    "qualificacao_responsavel", "capital_social", "porte_empresa",
    "ente_federativo_responsavel"
]

SIMPLES_COLS = [
    "cnpj_basico", "opcao_simples", "data_opcao_simples",
    "data_exclusao_simples", "opcao_mei", "data_opcao_mei",
    "data_exclusao_mei"
]

DOM_COLS = ["codigo", "descricao"]

def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    print(f"Baixando: {url}", flush=True)
    urlretrieve(url, dest)
    return dest

def unzip_single(zip_path: Path, target_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        if not names:
            raise RuntimeError(f"ZIP vazio: {zip_path}")
        name = names[0]
        out = target_dir / Path(name).name
        with zf.open(name) as src, open(out, "wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024 * 8)
        return out

def create_table_from_csv(con: duckdb.DuckDBPyConnection, table_name: str, csv_path: Path, columns: list[str]) -> None:
    coldef = ", ".join([f"{c} VARCHAR" for c in columns])
    con.execute(f"CREATE OR REPLACE TABLE {table_name} ({coldef});")
    con.execute(
        f"""
        INSERT INTO {table_name}
        SELECT * FROM read_csv(
            '{csv_path.as_posix()}',
            delim=';',
            header=false,
            columns={{ {", ".join([f"'{c}':'VARCHAR'" for c in columns])} }},
            quote='\\0',
            escape='\\0',
            all_varchar=true,
            ignore_errors=true
        );
        """
    )

def append_filtered_estabelecimentos(con, csv_path: Path, uf_alvo: tuple[str, ...]) -> None:
    create_table_from_csv(con, "_estab_chunk", csv_path, ESTAB_COLS)
    uf_list = ", ".join([f"'{uf}'" for uf in uf_alvo])
    con.execute(
        f"""
        INSERT INTO estab_filtrado
        SELECT *
        FROM _estab_chunk
        WHERE uf IN ({uf_list});
        """
    )
    con.execute("DROP TABLE _estab_chunk;")

def append_filtered_empresas(con, csv_path: Path) -> None:
    create_table_from_csv(con, "_emp_chunk", csv_path, EMP_COLS)
    con.execute(
        """
        INSERT INTO empresas_filtrado
        SELECT e.*
        FROM _emp_chunk e
        SEMI JOIN cnpjs_alvo c
          ON e.cnpj_basico = c.cnpj_basico;
        """
    )
    con.execute("DROP TABLE _emp_chunk;")

def load_simples_filtrado(con, csv_path: Path) -> None:
    create_table_from_csv(con, "_simples_chunk", csv_path, SIMPLES_COLS)
    con.execute(
        """
        CREATE OR REPLACE TABLE simples_filtrado AS
        SELECT s.*
        FROM _simples_chunk s
        SEMI JOIN cnpjs_alvo c
          ON s.cnpj_basico = c.cnpj_basico;
        """
    )
    con.execute("DROP TABLE _simples_chunk;")

def load_domain(con, table_name: str, csv_path: Path) -> None:
    create_table_from_csv(con, table_name, csv_path, DOM_COLS)

def make_output(con, output_csv_gz: Path):
    query = r"""
    WITH base AS (
        SELECT
            e.cnpj_basico || e.cnpj_ordem || e.cnpj_dv AS cnpj,
            substr(e.cnpj_basico,1,2) || '.' || substr(e.cnpj_basico,3,3) || '.' || substr(e.cnpj_basico,6,3) || '/' ||
            e.cnpj_ordem || '-' || e.cnpj_dv AS cnpj_formatado,
            e.cnpj_basico,
            e.identificador_matriz_filial AS matriz_filial_codigo,
            CASE e.identificador_matriz_filial
                WHEN '1' THEN 'MATRIZ'
                WHEN '2' THEN 'FILIAL'
                ELSE NULL
            END AS matriz_filial_desc,
            emp.razao_social,
            e.nome_fantasia,
            emp.natureza_juridica AS natureza_juridica_codigo,
            nat.descricao AS natureza_juridica_desc,
            emp.qualificacao_responsavel AS qualificacao_responsavel_codigo,
            qual.descricao AS qualificacao_responsavel_desc,
            REPLACE(emp.capital_social, ',', '.') AS capital_social,
            emp.porte_empresa AS porte_codigo,
            CASE emp.porte_empresa
                WHEN '00' THEN 'NAO INFORMADO'
                WHEN '01' THEN 'MICRO EMPRESA'
                WHEN '03' THEN 'EMPRESA DE PEQUENO PORTE'
                WHEN '05' THEN 'DEMAIS'
                ELSE NULL
            END AS porte_desc,
            emp.ente_federativo_responsavel,
            e.situacao_cadastral AS situacao_cadastral_codigo,
            CASE e.situacao_cadastral
                WHEN '01' THEN 'NULA'
                WHEN '1' THEN 'NULA'
                WHEN '2' THEN 'ATIVA'
                WHEN '3' THEN 'SUSPENSA'
                WHEN '4' THEN 'INAPTA'
                WHEN '08' THEN 'BAIXADA'
                WHEN '8' THEN 'BAIXADA'
                ELSE NULL
            END AS situacao_cadastral_desc,
            e.data_situacao_cadastral,
            e.motivo_situacao_cadastral AS motivo_situacao_cadastral_codigo,
            mot.descricao AS motivo_situacao_cadastral_desc,
            e.data_inicio_atividade,
            e.cnae_fiscal_principal AS cnae_principal_codigo,
            cnae.descricao AS cnae_principal_desc,
            e.cnae_fiscal_secundaria AS cnae_secundaria_codigos,
            e.tipo_logradouro,
            e.logradouro,
            e.numero,
            e.complemento,
            e.bairro,
            e.cep,
            e.uf,
            e.municipio AS municipio_codigo,
            mun.descricao AS municipio_nome,
            e.ddd1, e.telefone1, e.ddd2, e.telefone2, e.ddd_fax, e.fax,
            e.correio_eletronico AS email,
            e.situacao_especial,
            e.data_situacao_especial,
            s.opcao_simples,
            s.data_opcao_simples,
            s.data_exclusao_simples,
            s.opcao_mei,
            s.data_opcao_mei,
            s.data_exclusao_mei
        FROM estab_filtrado e
        LEFT JOIN empresas_filtrado emp ON e.cnpj_basico = emp.cnpj_basico
        LEFT JOIN simples_filtrado s ON e.cnpj_basico = s.cnpj_basico
        LEFT JOIN cnaes cnae ON e.cnae_fiscal_principal = cnae.codigo
        LEFT JOIN naturezas nat ON emp.natureza_juridica = nat.codigo
        LEFT JOIN municipios mun ON e.municipio = mun.codigo
        LEFT JOIN motivos mot ON e.motivo_situacao_cadastral = mot.codigo
        LEFT JOIN qualificacoes qual ON emp.qualificacao_responsavel = qual.codigo
    )
    SELECT * FROM base
    """
    tmp_csv = output_csv_gz.with_suffix("")
    con.execute(
        f"""
        COPY ({query})
        TO '{tmp_csv.as_posix()}'
        (HEADER, DELIMITER ';');
        """
    )
    with open(tmp_csv, "rb") as f_in, gzip.open(output_csv_gz, "wb", compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out, length=1024 * 1024 * 8)
    tmp_csv.unlink(missing_ok=True)

def main():
    ap = argparse.ArgumentParser(description="Baixa e consolida a base oficial do CNPJ da Receita Federal para SP + MS.")
    ap.add_argument("--snapshot", default=SNAPSHOT_DEFAULT, help="Ex.: 2026-01")
    ap.add_argument("--output-dir", "--output", dest="output_dir", default="saida_receita_sp_ms",
                    help="Pasta de saída (ex: data/)")
    ap.add_argument("--ufs", nargs="+", default=list(UF_ALVO_DEFAULT),
                    help="UFs a filtrar (ex: --ufs SP MS PR RJ)")
    ap.add_argument("--keep-downloads", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(parents=True, exist_ok=True)
    dl = workdir / "downloads"
    xdir = workdir / "extracted"
    dl.mkdir(exist_ok=True)
    xdir.mkdir(exist_ok=True)

    base = f"{BASE_ROOT}/{args.snapshot}"

    con = duckdb.connect(str(workdir / "receita_sp_ms.duckdb"))
    con.execute("PRAGMA threads=4;")
    con.execute("PRAGMA memory_limit='8GB';")

    con.execute(f"CREATE OR REPLACE TABLE estab_filtrado ({', '.join([c + ' VARCHAR' for c in ESTAB_COLS])});")
    con.execute(f"CREATE OR REPLACE TABLE empresas_filtrado ({', '.join([c + ' VARCHAR' for c in EMP_COLS])});")

    # 1) Estabelecimentos filtrados por UF
    for i in range(10):
        name = f"Estabelecimentos{i}.zip"
        zip_path = download(f"{base}/{name}", dl / name)
        csv_path = unzip_single(zip_path, xdir)
        append_filtered_estabelecimentos(con, csv_path, tuple(args.ufs))
        csv_path.unlink(missing_ok=True)

    # 2) Base de CNPJs alvo
    con.execute("CREATE OR REPLACE TABLE cnpjs_alvo AS SELECT DISTINCT cnpj_basico FROM estab_filtrado;")

    # 3) Empresas filtradas pelos CNPJs alvo
    for i in range(10):
        name = f"Empresas{i}.zip"
        zip_path = download(f"{base}/{name}", dl / name)
        csv_path = unzip_single(zip_path, xdir)
        append_filtered_empresas(con, csv_path)
        csv_path.unlink(missing_ok=True)

    # 4) Simples / MEI
    zip_path = download(f"{base}/Simples.zip", dl / "Simples.zip")
    csv_path = unzip_single(zip_path, xdir)
    load_simples_filtrado(con, csv_path)
    csv_path.unlink(missing_ok=True)

    # 5) Tabelas de domínio
    for name, table in [
        ("Cnaes.zip", "cnaes"),
        ("Naturezas.zip", "naturezas"),
        ("Municipios.zip", "municipios"),
        ("Motivos.zip", "motivos"),
        ("Qualificacoes.zip", "qualificacoes"),
    ]:
        zip_path = download(f"{base}/{name}", dl / name)
        csv_path = unzip_single(zip_path, xdir)
        load_domain(con, table, csv_path)
        csv_path.unlink(missing_ok=True)

    # 6) Output final
    out_csv_gz = outdir / "receita_empresas_sp_ms.csv.gz"
    make_output(con, out_csv_gz)
    print(f"\nArquivo final gerado: {out_csv_gz}")

    if not args.keep_downloads:
        shutil.rmtree(workdir, ignore_errors=True)

if __name__ == "__main__":
    main()
