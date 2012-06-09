import logging
from datetime import datetime, timedelta
from itertools import groupby
from django.http import Http404
from django.utils import timezone
from taggit.models import Tag, TaggedItem
from django.utils.timezone import localtime
from django.core.urlresolvers import reverse
from archive.models import Update, Site, Screenshot, Champion
from django.template.defaultfilters import date as dateformat
from django.views.generic import TemplateView, ListView, DetailView
logger = logging.getLogger(__name__)


class AboutDetail(TemplateView):
    """
    Some background on this site.
    """
    template_name = 'about.html'


class CryForHelp(TemplateView):
    """
    A cry for help.
    """
    template_name = 'cry_for_help.html'
    
    def get_context_data(self, **kwargs):
        context = super(BuildableTemplateView, self).get_context_data(**kwargs)
        context['champion_list'] = Champion.objects.all()
        return context


class ChampionsList(ListView):
    """
    A list of the people who have given money to support the site.
    """
    queryset = Champion.objects.all()
    template_name = 'champion_list.html'


class Index(TemplateView):
    """
    The homepage.
    """
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        update = Update.objects.live()
        if not update:
            raise Http404
        object_list = update.screenshot_set.filter(
            has_crop=True, site__on_the_homepage=True)
        object_list = object_list.select_related("site")
        # A case-insensitive resorting of the list
        object_list = sorted(object_list, key=lambda x: x.site.name.lower())
        object_list = group_objects_by_number(object_list, 4)
        return {
            'update': update,
            'object_list': object_list,
        }


class ScreenshotDetail(DetailView):
    """
    All about a particular screenshot. See the whole thing full size.
    """
    template_name = 'screenshot_detail.html'
    queryset = Screenshot.objects.filter(site__status='active').select_related("update")
    
    def get_context_data(self, **kwargs):
        context = super(ScreenshotDetail, self).get_context_data(**kwargs)
        try:
            next = Screenshot.objects.exclude(id=context['object'].id).filter(
                site=context['object'].site,
                has_image=True,
                timestamp__gte=context['object'].timestamp
            ).order_by("timestamp")[0]
        except IndexError:
            next = None
        try:
            prev = Screenshot.objects.exclude(id=context['object'].id).filter(
                site=context['object'].site,
                has_image=True,
                timestamp__lte=context['object'].timestamp
            )[0]
        except IndexError:
            prev = None
        context.update({
            'next': next,
            'prev': prev,
        })
        return context


class DateDetail(DetailView):
    """
    All the updates on a particular date.
    """
    template_name = 'date_detail.html'
    queryset = Update.objects.dates()
    
    def get_object(self):
        try:
            date_parts = map(int, [
                self.kwargs['year'],
                self.kwargs['month'],
                self.kwargs['day']
            ])
            date_obj = datetime(*date_parts)
        except:
            raise Http404
        for i in self.queryset:
            if i == date_obj.date():
                return date_obj
        raise Http404
    
    def get_context_data(self, **kwargs):
        tz = timezone.get_current_timezone()
        update_list = Update.objects.filter(
            start__range=map(tz.localize, [
                self.object,
                self.object + timedelta(days=1)
            ])
        )
        if not update_list:
            raise Http404
        screenshot_list = Screenshot.objects.filter(
            update__in=update_list,
        ).select_related("site", "update")
        screenshot_groups = []
        for key, group in groupby(screenshot_list, lambda x: x.update):
            screenshot_groups.append((key, group_objects_by_number(list(group), 8)))
        return {
            'date': self.object,
            'screenshot_groups': screenshot_groups,
        }


class SiteDetail(DetailView):
    """
    All about a particular site.
    """
    template_name = 'site_detail.html'
    queryset = Site.objects.active()

    def get_context_data(self, **kwargs):
        screenshot_list = Screenshot.objects.filter(
            site=self.object,
            has_image=True,
            has_crop=True,
        ).select_related("site", "update")[:100]
        try:
            latest_screenshot = screenshot_list[0]
            screenshot_groups = []
            for key, group in groupby(screenshot_list[1:], lambda x: localtime(x.update.start).date()):
                screenshot_groups.append((key, group_objects_by_number(list(group), 5)))
        except IndexError:
            latest_screenshot = None
            screenshot_groups = []
        return {
            'object': self.object,
            'latest_screenshot': latest_screenshot,
            'screenshot_list': screenshot_groups,
        }


class UpdateDetail(DetailView):
    """
    All about a particular update.
    """
    template_name = "update_detail.html"
    queryset = Update.objects.all()

    def get_context_data(self, **kwargs):
        screenshot_list = Screenshot.objects.filter(update=self.object)
        screenshot_groups = group_objects_by_number(
            screenshot_list,
            number_in_each_group=4
        )
        return {
            'object': self.object,
            'screenshot_groups': screenshot_groups,
        }


class TagDetail(DetailView):
    """
    All about a particular update.
    """
    template_name = "tag_detail.html"
    queryset = Tag.objects.all()

    def get_context_data(self, **kwargs):
        object_list = [i.content_object for i in
            TaggedItem.objects.filter(tag=self.object)
        ]
        update = Update.objects.live()
        screenshot_list = Screenshot.objects.filter(
            update=update,
            site__in=object_list
        )
        screenshot_groups = group_objects_by_number(
            screenshot_list,
            number_in_each_group=4
        )
        return {
            'object': self.object,
            'update': update,
            'screenshot_groups': screenshot_groups,
        }


class AdvancedSearch(TemplateView):
    """
    An opportunity for users to craft more complex searches of the database.
    """
    template_name = 'advanced_search.html'
    
    def get_context_data(self, **kwargs):
        context = super(AdvancedSearch, self).get_context_data(**kwargs)
        
        # Pull the data for the form fields
        site_list = Site.objects.active()
        site_list = sorted(site_list, key=lambda x: x.name.lower())
        context['site_list'] = site_list
        tag_list = Tag.objects.all()
        context['tag_list'] = tag_list
        
        # Check if any qs variables have been provided
        is_search = len(self.request.GET.keys()) > 0
        context['is_search'] = is_search
        
        # If not just drop out now
        if not is_search:
            return context
        
        # Examine the valid keys and see what's been submitted
        site = self.request.GET.get('site', None)
        tag = self.request.GET.get('tag', None)
        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)
        if start_date == 'YYYY/MM/DD':
            start_date = None
        if end_date == 'YYYY/MM/DD':
            end_date = None
        
        # Since you can't search both site and tag, if we have both
        # we should throw an error
        if site and tag:
            context['has_error'] = True
            context['error_message'] = 'Sorry. You cannot filter by both site and tag at the same time.'
            return context
        
        # A dict to store filters depending on what has been submitted
        filters = {}
        
        # First the site or tag
        if site:
            try:
                site = Site.objects.get(slug=site)
            except Site.DoesNotExist:
                context['has_error'] = True
                context['error_message'] = 'Sorry. The site you submitted does not exist.'
            filters['site'] = site
            # Gotta give it a longer name so it isn't overridden by site
            # context processor
            context['searched_site'] = site
        elif tag:
            try:
                tag = Tag.objects.get(slug=tag)
            except Tag.DoesNotExist:
                context['has_error'] = True
                context['error_message'] = 'Sorry. The tag you submitted does not exist.'
            tagged_list = [i.content_object for i in
                TaggedItem.objects.filter(tag=tag)
            ]
            filters['site__in'] = tagged_list
            context['tag'] = tag
        else:
            context['has_error'] = True
            context['error_message'] = 'Sorry. You must submit either a site or a tag with every search.'
        
        # Then the date range
        if not start_date and not end_date:
            context['has_error'] = True
            context['error_message'] = 'Sorry. You must submit both a start and end date.'
            return context
        elif start_date and not end_date:
            context['has_error'] = True
            context['error_message'] = 'Sorry. You must submit both a start and end date.'
            return context
        elif end_date and not start_date:
            context['has_error'] = True
            context['error_message'] = 'Sorry. You must submit both a start and end date.'
            return context
        elif start_date and end_date:
            # Validate the start date
            try:
                start_date = datetime.strptime(start_date, "%Y/%m/%d")
            except ValueError:
                context['has_error'] = True
                context['error_message'] = 'Sorry. Your start date was not properly formatted.'
                return context
            # Validate the end date
            try:
                end_date = datetime.strptime(end_date, "%Y/%m/%d")
            except ValueError:
                context['has_error'] = True
                context['error_message'] = 'Sorry. Your end date was not properly formatted.'
                return context
            if end_date < start_date:
                context['has_error'] = True
                context['error_message'] = 'Sorry. Your end date comes before you start date.'
                return context
            filters.update({
                'timestamp__range': [start_date, end_date],
            })
            context.update({
                'start_date': start_date,
                'end_date': end_date,
            })
        
        # Execute the filters and pass out the result
        context['object_list'] = Screenshot.objects.filter(**filters)[:500]
        context['object_count'] = context['object_list'].count()
        screenshot_groups = []
        for key, group in groupby(context['object_list'], lambda x: localtime(x.update.start).date()):
            screenshot_groups.append((key, group_objects_by_number(list(group), 6)))
        context['object_groups'] = screenshot_groups
        return context


def group_objects_by_number(object_list, number_in_each_group=3):
    """
    Accepts an object list and groups it into sets.
    
    Intended for displaying the data in a three-column grid.
    """
    new_list = []
    i = 0
    while i < len(object_list):
        new_list.append([x for x in object_list[i:i+number_in_each_group]])
        i += number_in_each_group
    return new_list


