import dagster as dg

raw_transactions = dg.AssetSpec("raw_transactions")


@dg.sensor(minimum_interval_seconds=30)
def raw_transactions_sensor(
    context: dg.SensorEvaluationContext,
) -> dg.SensorResult:
    # This sensor polls the external system every 30 seconds
    # for the last time the file was modified.
    file_last_modified_at_ms = ...

    # We can use the cursor to store the last time the sensor updated the asset
    if context.cursor is not None:
        external_asset_last_updated_at_ms = float(context.cursor)
    else:
        external_asset_last_updated_at_ms = 0

    if file_last_modified_at_ms > external_asset_last_updated_at_ms:
        # The external asset has been modified since we last updated it,
        # so record a materialization and update the cursor.
        return dg.SensorResult(
            asset_events=[
                dg.AssetMaterialization(
                    asset_key=raw_transactions.key,
                    # You can optionally attach metadata
                    metadata={"file_last_modified_at_ms": file_last_modified_at_ms},
                )
            ],
            cursor=str(file_last_modified_at_ms),
        )
    else:
        # Nothing has happened since the last time we checked
        return dg.SensorResult()


defs = dg.Definitions(assets=[raw_transactions], sensors=[raw_transactions_sensor])
