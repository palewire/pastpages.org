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
from bakery.views import BuildableListView
from bakery.views import BuildableDetailView, BuildableTemplateView
logger = logging.getLogger(__name__)


class AboutDetail(BuildableTemplateView):
    """
    Some background on this site.
    """
    template_name = 'about.html'
    build_path = 'about/index.html'


class CryForHelp(BuildableTemplateView):
    """
    A cry for help.
    """
    template_name = 'cry_for_help.html'
    build_path = 'cry-for-help/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(BuildableTemplateView, self).get_context_data(**kwargs)
        context['champion_list'] = Champion.objects.all()
        return context


class ChampionsList(BuildableListView):
    """
    A list of the people who have given money to support the site.
    """
    queryset = Champion.objects.all()
    build_path = 'champions/index.html'
    template_name = 'champion_list.html'


class Index(BuildableTemplateView):
    """
    The homepage.
    """
    template_name = 'index.html'
    build_path = 'index.html'
    
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


class ScreenshotDetail(BuildableDetailView):
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


class DateDetail(BuildableDetailView):
    """
    All the updates on a particular date.
    """
    template_name = 'date_detail.html'
    
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
        for i in self.get_queryset():
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
    
    def get_url(self, obj):
        return '/date/%s/%s/%s/' % (
            dateformat(obj, "Y"),
            dateformat(obj, "m"),
            dateformat(obj, "d")
        )
    
    def set_kwargs(self, obj):
        self.kwargs = dict(
            year=obj.year,
            month=obj.month,
            day=obj.day
        )
    
    def uniqify(self, seq, idfun=None): 
       # order preserving
       if idfun is None:
           def idfun(x): return x
       seen = {}
       result = []
       for item in seq:
           marker = idfun(item)
           # in old Python versions:
           # if seen.has_key(marker)
           # but in new ones:
           if marker in seen: continue
           seen[marker] = 1
           result.append(item)
       return result

    def get_queryset(self):
        return self.uniqify([timezone.localtime(i.start).date()
            for i in Update.objects.all()])
    
    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]


class SiteDetail(BuildableDetailView):
    """
    All about a particular site.
    """
    template_name = 'site_detail.html'
    queryset = Site.objects.filter(status='active')

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


class UpdateDetail(BuildableDetailView):
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


class TagDetail(BuildableDetailView):
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
    
    def get_url(self, obj):
        return reverse('archive-tag-detail', args=[obj.name])



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


