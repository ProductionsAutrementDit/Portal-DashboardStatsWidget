import logging
from portal.search.elastic import query_elastic
from django.core.cache import cache
import time
from datetime import datetime

log = logging.getLogger(__name__)

def get_stats_from_search(search_id, fieldname, request, item_type='item', expiry=3600):

    from portal.vidispine.icollection import CollectionHelper
    from portal.vidispine.iitem import ItemHelper   
    from portal.search.elastic import query_elastic, postprocess_search   
    from portal.vidispine.vsavedsearch import create_elastic_search_from_saved_search, update_search_with_optional_parameters
    from portal.plugins.dashboardstats.models import StatsJob

    job, created = StatsJob.objects.get_or_create(search_id=search_id, defaults={'status': 'Finished', 'progress': 100})
    
    if job.status == "Calculating":
        # wait for cache key to be filled
        while True:
            time.sleep(60)
            if len(StatsJob.objects.filter(search_id=search_id, status='Finished')) > 0:
                break;
                
    ch = CollectionHelper(runas=request.user)
  
    collection = ch.getCollection(search_id)
    name = collection.getName().replace("savedSearch_", "")
    
    cache_key = 'dashboardstat-' + search_id + '-durationSeconds'
    
    if cache.get(cache_key) is None:
    
        job.status = "Calculating"
        job.save()
    
        ith = ItemHelper(runas=request.user)
        lib_id = ''
        for c in collection.getContent():
            if c.getType() == 'library':
                lib_id = c.getId()
    
        # Get library settings
        try:
            lib_settings = ith.getLibrarySettings(library_id=lib_id)
        except NotFoundError:
            log.warning('Could not get library settings, lib_id: %s', lib_id, exc_info=True)
            return False
        search = create_elastic_search_from_saved_search(
            lib_settings, request.user.username
        )
        search, saved_params = update_search_with_optional_parameters(
            search=search,
            collection_id=search_id,
            lib_settings=lib_settings,
            collection_helper=ch,
            querydict=request.GET,
            request=request
        )
        log.debug('Saved search from elastic, search.to_dict(): %r', search.to_dict())
        sdoc = search.to_dict()
    
        first = 0
        number = 100
        total = 0
        count = 0
        
        while True:
            elastic_results = query_elastic(
                query=sdoc,
                first=first,
                number=number,
                fields=None
            )
            
            for hit in elastic_results['hits']['hits']:
                if hit["_type"] != item_type:
                    continue
                if fieldname in hit['_source']:
                    total = total + float(hit['_source'][fieldname][0])     
            if len(elastic_results['hits']['hits']) < number:
                count = elastic_results['hits']['total']
                break
            first = first + number
        
        cache.set(cache_key, (count, total), expiry)
    
        job.status = "Finished"
        job.save()
      
    else:
        count, total = cache.get(cache_key)
    
    return name, count, total