import os
from django.core.management.base import BaseCommand, CommandError
from django.template import Template, Context
from django.template.loader import render_to_string
from optparse import make_option

class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option('--server',
        action='store',
        dest='server_config',
        default='nginx',
        help='Configuration format to use (apache/nginx)'),

        make_option('--site',
        action='store',
        dest='site_id',
        type='int',
        default=1,
        help='Use the specified SITE_ID to get the site domain'),
    )

    def handle(self, *args, **options):
        if options['server_config'] not in ('nginx', 'apache'):
            raise CommandError('Only Apache and Nginx are supported right now.')

        from django.contrib.sites.models import Site
        try:
            site = Site.objects.get(pk=options['site_id'])
        except Site.DoesNotExist:
            choices = Site.objects.all().values_list('pk', flat=True)
            choices = ', '.join([unicode(c) for c in choices])
            raise CommandError('Invalid SITE_ID provided, valid choices are %s' % choices)
        
        from django.conf import settings
        if not hasattr(settings, 'WEB_ROOT'):
            raise CommandError('Could not find WEB_ROOT in your settings module')

        context = {'domain': site, 'web_root': settings.WEB_ROOT}
        template = render_to_string('staticgenerator/%s.conf' % options['server_config'], context)
        self.stdout.write(template)
