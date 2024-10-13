from django.contrib.sitemaps import Sitemap

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        # Define normal pages here, assuming they are top-level URLs
        return ['home', 'about', 'skills', 'certification', 'pricing', 'careers', 'contact']

    def location(self, item):
        # Map each page to its full URL
        page_mapping = {
            'home': '/',
            'about': '/about/',
            'skills': '/skills/',
            'certification': '/certification/',
            'pricing': '/pricing/',
            'careers': '/careers/',  # renamed from 'carrier'
            'contact': '/contact/',
        }
        return page_mapping.get(item, '/')
