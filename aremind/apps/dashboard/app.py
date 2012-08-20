from rapidsms.apps.base import AppBase

from aremind.apps.dashboard.models import ReportComment
from aremind.apps.dashboard.utils.fadama import get_inquiry_numbers

from apps.utils.functional import map_reduce

class CommunicatorApp(AppBase):
    "Catch messages which might be replies to messages sent by the dashboard communicator."

    def handle(self, msg):
        "Handle otherwise unhandled message from users related to inquiry messages."
        active_reports = active_communicator_threads(msg.connection.identity)
        if not active_reports:
            return False

        for active_report in active_reports:
            comment_data = {
                'report_id': active_report,
                'comment_type': ReportComment.REPLY_TYPE,
                'text': msg.text,
                'author': ReportComment.FROM_BENEFICIARY,
            }
            if len(active_reports) > 1:
                comment_data.extra_info = json.dumps({'ambiguous': list(set(active_reports) - set([active_report]))})

            ReportComment.objects.create(**comment_data)

        # TODO: reply back here? 'your response is received'
        return True
            

def active_communicator_threads(phone_number):
    "Return all phone numbers tied to a submitted report."
    # todo make this query more efficient one we've settled on a back-end data model
    reports = ReportComment.objects.filter(
        comment_type=ReportComment.INQUIRY_TYPE,
    )
    reports = [r for r in reports if _get_connection_from_report(r['report_id']) == phone_number]
    latest_inquiry_per_report = map_reduce(reports, lambda r: [(r.report_id, r.date)], max)
    active_report_ids = [report_id for report_id, last_inquiry in latest_inquiry_per_report.iteritems() if datetime.now() - last_inquiry < settings.COMMUNICATOR_RESPONSE_WINDOW]
    return active_report_ids


