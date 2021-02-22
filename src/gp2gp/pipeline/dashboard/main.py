import sys
from dataclasses import asdict
from datetime import datetime

import boto3
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from gp2gp.dashboard.organisationMetadata import construct_service_dashboard_metadata
from gp2gp.date.range import DateTimeRange

from gp2gp.io.csv import read_gzip_csv_files
from gp2gp.io.dictionary import camelize_dict
from gp2gp.io.json import write_json_file, read_json_file, upload_json_object
from gp2gp.odsportal.sources import construct_organisation_list_from_dict
from gp2gp.pipeline.dashboard.args import parse_dashboard_pipeline_arguments
from gp2gp.pipeline.dashboard.core import (
    calculate_practice_metrics_data,
    parse_transfers_from_messages,
)
from gp2gp.service.transfer import convert_transfers_to_table
from gp2gp.spine.sources import construct_messages_from_splunk_items
from pyarrow.parquet import write_table
from pyarrow.fs import S3FileSystem


def _write_dashboard_json_file(dashboard_data, output_file_path):
    content_dict = asdict(dashboard_data)
    camelized_dict = camelize_dict(content_dict)
    write_json_file(camelized_dict, output_file_path)


def _upload_dashboard_json_object(dashboard_data, s3_object):
    content_dict = asdict(dashboard_data)
    camelized_dict = camelize_dict(content_dict)
    upload_json_object(camelized_dict, s3_object)


def _read_spine_csv_gz_files(file_paths):
    items = read_gzip_csv_files(file_paths)
    return construct_messages_from_splunk_items(items)


def _get_time_range(year, month):
    metric_month = datetime(year, month, 1, tzinfo=tzutc())
    next_month = metric_month + relativedelta(months=1)
    return DateTimeRange(metric_month, next_month)


def _is_outputting_to_file(args):
    return (
        args.organisation_metadata_output_file
        and args.practice_metrics_output_file
        and args.transfers_output_file
    )


def _is_outputting_to_s3(args):
    return (
        args.organisation_metadata_output_key
        and args.practice_metrics_output_key
        and args.transfers_output_key
    )


def main():
    args = parse_dashboard_pipeline_arguments(sys.argv[1:])
    time_range = _get_time_range(args.year, args.month)

    organisation_data = read_json_file(args.organisation_list_file)
    organisation_metadata = construct_organisation_list_from_dict(data=organisation_data)

    spine_messages = _read_spine_csv_gz_files(args.input_files)
    transfers = list(parse_transfers_from_messages(spine_messages, time_range))
    practice_metrics_data = calculate_practice_metrics_data(
        transfers, organisation_metadata.practices, time_range
    )

    organisation_metadata = construct_service_dashboard_metadata(organisation_metadata)
    transfer_table = convert_transfers_to_table(transfers)

    if _is_outputting_to_file(args):
        _write_dashboard_json_file(organisation_metadata, args.organisation_metadata_output_file)
        _write_dashboard_json_file(practice_metrics_data, args.practice_metrics_output_file)
        write_table(transfer_table, args.transfers_output_file)
    elif _is_outputting_to_s3(args):
        s3 = boto3.resource("s3", endpoint_url=args.s3_endpoint_url)

        bucket_name = args.output_bucket

        _upload_dashboard_json_object(
            organisation_metadata,
            s3.Object(bucket_name, args.organisation_metadata_output_key),
        )
        _upload_dashboard_json_object(
            practice_metrics_data, s3.Object(bucket_name, args.practice_metrics_output_key)
        )
        write_table(
            table=transfer_table,
            where=bucket_name + "/" + args.transfers_output_key,
            filesystem=S3FileSystem(endpoint_override=args.s3_endpoint_url),
        )
