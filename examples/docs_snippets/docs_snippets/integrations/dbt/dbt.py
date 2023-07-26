# ruff: isort: skip_file


def scope_load_assets_from_dbt_project():
    # start_load_assets_from_dbt_project
    from dagster_dbt import load_assets_from_dbt_project

    dbt_assets = load_assets_from_dbt_project(project_dir="path/to/dbt/project")
    # end_load_assets_from_dbt_project


def scope_load_assets_from_dbt_manifest():
    # start_load_assets_from_dbt_manifest
    import json

    from dagster_dbt import load_assets_from_dbt_manifest

    with open("path/to/dbt/manifest.json") as f:
        manifest_json = json.load(f)

    dbt_assets = load_assets_from_dbt_manifest(manifest_json)
    # end_load_assets_from_dbt_manifest


def scope_dbt_cli_resource_config():
    # start_dbt_cli_resource
    import os

    from dagster_dbt import DbtCliResource, load_assets_from_dbt_project

    from dagster import Definitions

    DBT_PROJECT_PATH = "path/to/dbt_project"
    DBT_TARGET = "hive" if os.getenv("EXECUTION_ENV") == "prod" else "duckdb"

    defs = Definitions(
        assets=load_assets_from_dbt_project(DBT_PROJECT_PATH),
        resources={
            "dbt": DbtCliResource(project_dir=DBT_PROJECT_PATH, target=DBT_TARGET),
        },
    )
    # end_dbt_cli_resource


def scope_schedule_assets(dbt_assets):
    # start_schedule_assets
    from dagster import ScheduleDefinition, define_asset_job, Definitions

    run_everything_job = define_asset_job("run_everything", selection="*")

    # only `order_stats` and its children
    run_something_job = define_asset_job("run_something", selection="order_stats*")

    defs = Definitions(
        assets=dbt_assets,
        schedules=[
            ScheduleDefinition(
                job=run_something_job,
                cron_schedule="@daily",
            ),
            ScheduleDefinition(
                job=run_everything_job,
                cron_schedule="@weekly",
            ),
        ],
    )

    # end_schedule_assets


def scope_downstream_asset():
    from dagster import AssetIn, asset

    # start_downstream_asset
    @asset(
        ins={"my_dbt_model": AssetIn(input_manager_key="pandas_df_manager")},
    )
    def my_downstream_asset(my_dbt_model):
        # my_dbt_model is a Pandas dataframe
        return my_dbt_model.where(foo="bar")

    # end_downstream_asset


def scope_upstream_asset():
    from dagster import asset

    # start_upstream_asset
    @asset(key_prefix="jaffle_shop")
    def orders():
        return ...

    # end_upstream_asset


def scope_input_manager():
    # start_input_manager
    import pandas as pd

    from dagster import ConfigurableIOManager

    class PandasIOManager(ConfigurableIOManager):
        connection_str: str

        def handle_output(self, context, obj):
            # dbt handles outputs for us
            pass

        def load_input(self, context) -> pd.DataFrame:
            """Load the contents of a table as a pandas DataFrame."""
            table_name = context.asset_key.path[-1]
            return pd.read_sql(f"SELECT * FROM {table_name}", con=self.connection_str)

    # end_input_manager


def scope_input_manager_resources():
    class PandasIOManager:
        def __init__(self, connection_str: str):
            pass

    # start_input_manager_resources
    from dagster_dbt import DbtCliResource, load_assets_from_dbt_project

    from dagster import Definitions

    defs = Definitions(
        assets=load_assets_from_dbt_project(...),
        resources={
            "dbt": DbtCliResource(project_dir="path/to/dbt_project"),
            "pandas_df_manager": PandasIOManager(connection_str=...),
        },
    )
    # end_input_manager_resources


def scope_custom_asset_key_dagster_dbt_translator():
    # start_custom_asset_key_dagster_dbt_translator
    from pathlib import Path
    from dagster import AssetKey, OpExecutionContext
    from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets
    from typing import Any, Mapping

    manifest_path = Path("path/to/dbt_project/target/manifest.json")

    class CustomDagsterDbtTranslator(DagsterDbtTranslator):
        def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
            return self.get_asset_key(dbt_resource_props).with_prefix("snowflake")

    @dbt_assets(
        manifest=manifest_path,
        dagster_dbt_translator=CustomDagsterDbtTranslator(),
    )
    def my_dbt_assets(context: OpExecutionContext, dbt: DbtCliResource):
        yield from dbt.cli(["build"], context=context).stream()

    # end_custom_asset_key_dagster_dbt_translator


def scope_custom_group_name_dagster_dbt_translator():
    # start_custom_group_name_dagster_dbt_translator
    from pathlib import Path
    from dagster import OpExecutionContext
    from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets
    from typing import Any, Mapping, Optional

    manifest_path = Path("path/to/dbt_project/target/manifest.json")

    class CustomDagsterDbtTranslator(DagsterDbtTranslator):
        def get_group_name(
            self, dbt_resource_props: Mapping[str, Any]
        ) -> Optional[str]:
            return "snowflake"

    @dbt_assets(
        manifest=manifest_path,
        dagster_dbt_translator=CustomDagsterDbtTranslator(),
    )
    def my_dbt_assets(context: OpExecutionContext, dbt: DbtCliResource):
        yield from dbt.cli(["build"], context=context).stream()

    # end_custom_group_name_dagster_dbt_translator


def scope_custom_description_dagster_dbt_translator():
    # start_custom_description_dagster_dbt_translator
    import textwrap
    from pathlib import Path
    from dagster import OpExecutionContext
    from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets
    from typing import Any, Mapping

    manifest_path = Path("path/to/dbt_project/target/manifest.json")

    class CustomDagsterDbtTranslator(DagsterDbtTranslator):
        def get_description(self, dbt_resource_props: Mapping[str, Any]) -> str:
            return textwrap.indent(dbt_resource_props.get("raw_sql", ""), "\t")

    @dbt_assets(
        manifest=manifest_path,
        dagster_dbt_translator=CustomDagsterDbtTranslator(),
    )
    def my_dbt_assets(context: OpExecutionContext, dbt: DbtCliResource):
        yield from dbt.cli(["build"], context=context).stream()

    # end_custom_description_dagster_dbt_translator


def scope_custom_metadata_dagster_dbt_translator():
    # start_custom_metadata_dagster_dbt_translator
    from pathlib import Path
    from dagster import MetadataValue, OpExecutionContext
    from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets
    from typing import Any, Mapping

    manifest_path = Path("path/to/dbt_project/target/manifest.json")

    class CustomDagsterDbtTranslator(DagsterDbtTranslator):
        def get_metadata(
            self, dbt_resource_props: Mapping[str, Any]
        ) -> Mapping[str, Any]:
            return {"meta": MetadataValue.json(dbt_resource_props.get("meta", {}))}

    @dbt_assets(
        manifest=manifest_path,
        dagster_dbt_translator=CustomDagsterDbtTranslator(),
    )
    def my_dbt_assets(context: OpExecutionContext, dbt: DbtCliResource):
        yield from dbt.cli(["build"], context=context).stream()

    # end_custom_metadata_dagster_dbt_translator
