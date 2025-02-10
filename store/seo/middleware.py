from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect
from .models import MetaData
from django.contrib.contenttypes.models import ContentType

class SEOMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(response, 'context_data') and 'object' in response.context_data:
            obj = response.context_data['object']
            content_type = ContentType.objects.get_for_model(obj)
            
            try:
                meta = MetaData.objects.get(
                    content_type=content_type,
                    object_id=obj.id
                )
                
                if meta.is_noindex:
                    response['X-Robots-Tag'] = 'noindex, nofollow'
                    
                if meta.canonical_url:
                    if request.path != meta.canonical_url:
                        return HttpResponsePermanentRedirect(meta.canonical_url)
                        
            except MetaData.DoesNotExist:
                pass
                
        return response
