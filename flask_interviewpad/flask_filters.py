import base64
import json


class MyFilters:
    @staticmethod
    def init_app(app):
        app.template_filter('encode')(MyFilters.encode)
        app.template_filter('strftime')(MyFilters.strftime)
    @staticmethod
    def strftime(datetime_ob,strftime_fmt):
        return getattr(datetime_ob,'strftime',lambda x:str(datetime_ob))(strftime_fmt)


    @staticmethod
    def encode(text,how):
        if how == "base64":
            return base64.b64encode(text.encode("latin1"))
        elif how == "hex":
            return "".join(["\\x%02x"%(ord(c) if isinstance(c,(str,bytes)) else c,)for c in text])
        elif how == "json":# probably an object not text ..
            return json.dumps(text)