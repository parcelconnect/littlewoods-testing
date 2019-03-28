from idv.common.mail import create_mail


class TestCreateMail:

    def test_returns_expected_message_when_using_app_name(self):
        subject = 'Test Subject'
        recipients = ['brianhernandez@scurri.com', 'test@fastway.ie']
        context = {"test": "context"}
        msg = create_mail(
            subject=subject,
            template_prefix='move_report',
            emails=recipients,
            context=context,
            app_name='mover')

        assert msg.subject == subject
        assert msg.recipients() == recipients

    def test_returns_expected_message_when_not_using_app_name(self):
        subject = 'Test Subject'
        recipients = ['brianhernandez@scurri.com', 'test@fastway.ie']
        context = {"test": "context"}
        msg = create_mail(
            subject=subject,
            template_prefix='mover/move_report',
            emails=recipients,
            context=context)

        assert msg.subject == subject
        assert msg.recipients() == recipients
