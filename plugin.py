"""
This is your new plugin handler code.

Put your plugin handling code in here. remember to update the __init__.py file with 
you app version number. We have automatically generated a GUID for you, namespace, and a url 
that serves up index.html file
"""
import logging

from django.utils.translation import ugettext as _

from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import (IPluginURL, IPluginBlock, IAppRegister)
from portal.generic.dashboard_interfaces import IDashboardWidget

log = logging.getLogger(__name__)


class DashboardStatsRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "DashboardStats Registration App"
        self.plugin_guid = 'c57e329a-a87a-4264-b945-6f8b92a2e4b9'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'DashboardStats',
                'version': '0.0.1',
                'author': '',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

dashboardstatsplugin = DashboardStatsRegister()

class DashboardStatsWidget(Plugin):
    implements(IDashboardWidget)
    
    # Default refreshing every hour
    timeout = 3600

    def __init__(self):
        self.name = 'DashboardStats'
        self.plugin_guid = '3ca2c763-6474-4b7a-82ff-38f76d6b47b9'
        self.template_name = 'dashboardstats/dashboardwidget.html'
        self.configurable = True
    
    @staticmethod
    def get_render_data(render_data, settings, request):
        import datetime

        from portal.plugins.dashboardstats.utility import get_stats_from_search
        
        if 'savedsearch_id' not in settings:
            render_data['error'] = 'No saved search configured'
            render_data['title'] = ''
            render_data['duration'] = '0'
            render_data['count'] = '0'
            return render_data
        
        try:
            title, count, duration = get_stats_from_search(settings['savedsearch_id'], 'durationSeconds', request, expiry=settings['expiry'])
            seconds = int(duration)
            render_data['count'] = str(count)
            render_data['duration'] = str(datetime.timedelta(seconds=seconds))
            render_data['title'] = "Stats for %s:" % title
        except Exception as exception:
            render_data['error'] = 'Error loading saved search %s: %s' % (settings['savedsearch_id'], exception)
        return render_data

    @staticmethod
    def force_show_config(settings, request):
        return False

    @staticmethod
    def get_config_form(settings, request):
        # Django classes MUST be imported inside method, not when package
        # is initialized
        from django import forms
        from portal.vidispine.icollection import CollectionHelper
        
        choices = ()
        ch = CollectionHelper(runas=request.user)
        collections = ch.getAllCollections(includeItemThumbnails=False, savedSearchesOnly=True)
        for collection in collections:
            choices = choices + ((collection.getId(), collection.getName()),)

        class DashboardStatsWidgetSettingsForm(forms.Form):
            savedsearch_id = forms.ChoiceField(label=_('Saved search:'), choices=choices)
            expiry = forms.IntegerField(label=_('Refresh Interval (seconds):'), initial=3600, min_value=1)

        return DashboardStatsWidgetSettingsForm

    @staticmethod
    def get_list_title():
        return "Stats Widget"

dashboardstatswidget = DashboardStatsWidget()