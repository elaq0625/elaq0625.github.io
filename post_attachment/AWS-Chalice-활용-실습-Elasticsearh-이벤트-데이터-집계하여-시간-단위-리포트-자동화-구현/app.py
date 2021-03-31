from chalice import Chalice, Cron, Response
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from datetime import datetime, timedelta, timezone
import requests
import json

app = Chalice(app_name='hourly_report_test_chalice')

AWS_ACCESS_KEY = ### INPUT AWS ACCESS KEY
AWS_SECRET_KEY = ### INPUT AWS SECRETE KEY

WEBHOOK_URL = ### INPUT WebHook url 

HOST = ### INPUT AWS Elasticsearch END POINT
REGION = ### INPUT Region

aws_auth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION, 'es')
es_client = Elasticsearch(hosts=[{'host': HOST, 'port': 443}], http_auth=aws_auth,
                          use_ssl=True, verify_certs=True, connection_class=RequestsHttpConnection)

UTC_TIMEFORMAT = "%Y-%m-%dT%H:%M:%SZ"


def make_es_query_dict_object(begin_time, end_time):
    dict_result = {
        "aggs": {
            "count_by_hour": {
                "date_histogram": {
                    "field": "timestamp",
                    "interval": "hour"
                }
            }
        },
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "timestamp": {
                            "format": "strict_date_optional_time",
                            "gte": begin_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "lte": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                        }
                    }
                }
            }
        },
        "size": 0
    }
    return dict_result


def excute_es_query_and_extract_result(es_query):
    es_query_result = es_client.search(index=None, body=es_query)

    if "aggregations" not in es_query_result.keys():
        return None

    agg_result = es_query_result["aggregations"]

    if "count_by_hour" not in agg_result.keys():
        return None

    count_by_hour_result = agg_result["count_by_hour"]

    if "buckets" not in count_by_hour_result.keys():
        return None

    buckets_result = count_by_hour_result["buckets"]
    extract_result = list()

    for elem in buckets_result:
        cur_time_utc = datetime.strptime(
            elem["key_as_string"], UTC_TIMEFORMAT)
        cur_str_time = cur_time_utc.strftime(UTC_TIMEFORMAT)
        cur_count = elem["doc_count"]
        extract_result.append((cur_str_time, cur_count))

    return extract_result


def fill_empty_hour_and_sorted_result(begin_time, end_time, raw_result):
    result = raw_result
    hour_set = set()

    for elem in raw_result:
        hour_set.add(elem[0])

    diff_hour = int((end_time - begin_time).seconds / 3600)

    for delta in range(diff_hour):
        str_current_time = (begin_time + timedelta(hours=delta)
                            ).strftime(UTC_TIMEFORMAT)
        if str_current_time not in hour_set:
            result.append((str_current_time, 0))

    result.sort(key=lambda x: x[0], reverse=False)

    return result


def make_codeblock(result_list):
    msg_formatter = "{: >20} {: >10}"
    header_msg = msg_formatter.format(*["Time", "Count"])

    msg_list = [header_msg]

    for elem in result_list:
        msg_list.append(msg_formatter.format(*elem))

    str_msg = "\n".join(msg_list)

    markdown_code_style_msg = "```{}```".format(str_msg)

    return markdown_code_style_msg


def send_message_to_slack_channel(filled_result):
    message = {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*이벤트 시간당 호출 개수*"}
            },
            {
                "type": "section",
                "fields": [
                        {
                            "type": "mrkdwn",
                            "text": make_codeblock(filled_result)
                        }
                ]
            }
        ]
    }

    response = requests.post(
        WEBHOOK_URL, data=json.dumps(message),
        headers={'Content-Type': 'application/json'}
    )

    return response


def extract_es_hourly_event_data_and_hourly_report():
    now_time = datetime.utcnow()

    end_time_utc = datetime(year=now_time.year, month=now_time.month,
                            day=now_time.day, hour=now_time.hour, minute=0, second=0)
    begin_time_utc = end_time_utc - timedelta(hours=6)

    es_query = make_es_query_dict_object(begin_time_utc, end_time_utc)
    excuted_result = excute_es_query_and_extract_result(es_query)

    filled_result = fill_empty_hour_and_sorted_result(
        begin_time_utc, end_time_utc, excuted_result)

    send_message_to_slack_channel(filled_result)

    return Response(body="OK", status_code=200)


@app.schedule(Cron(0, '*', '*', '*', '?', '*'))
def cron_job(event):
    extract_es_hourly_event_data_and_hourly_report()


@app.route("/excute_hourly_report")
def excute_hourly_report():
    return extract_es_hourly_event_data_and_hourly_report()


@app.route('/')
def index():
    return {'hello': 'world'}


if __name__ == "__main__":
    extract_es_hourly_event_data_and_hourly_report()