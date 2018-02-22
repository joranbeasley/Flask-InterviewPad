String.prototype.formatUnicorn = String.prototype.formatUnicorn || function () {
    "use strict";
    var str = this.toString();
    if (arguments.length) {
        var t = typeof arguments[0];
        var key;
        var args = ("string" === t || "number" === t)?Array.prototype.slice.call(arguments): arguments[0];
        for (key in args) {
            str = str.replace(new RegExp("\\{" + key + "\\}", "gi"), args[key]);
        }
    }
    return str;
};
function loadJS(url){
    return new Promise(function(accept,reject){
        var script = document.createElement('script');
        script.onload = accept;
        script.src = url;
        document.head.appendChild(script);
    })
}
function loadCSS(url,timeout){
    return new Promise(function(accept,reject){
        var old_length = document.styleSheets.length;
        var too_late = Date.now()+newtimeout?timeout:3000;

        function check_loaded(){
            if (old_length < document.styleSheets.length){
                return accept()
            }
            if(Date.now() > too_late){
                return reject()
            }
            setTimeout(check_loaded,250)
        }
        var stylesheet = document.createElement('link');
        stylesheet.rel="stylesheet";
        stylesheet.type="text/css";
        script.href = url;
        document.head.appendChild(script);
        check_loaded()
    })
}

function MyAceEditor(divId){
    var known_workers = {coffee:1,css:1,html:1,javascript:1,json:1,lua:1,php:1,xml:1,xquery:1}
    var self=this;
    self.divId =divId;
    self.languages_url = "https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/mode-{languageMode}.js";
    self.themes_url    = "https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/theme-{themeName}.js";
    self.workers_url   = "https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/worker-{languageMode}.js";
    self.extension_url = "https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/ext-{extName}.js";
    this.editor_instance=null;
    this.loaded_modes={}
    this.loaded_themes={}
    this.loaded_workers={}
    this.loaded_extensions={}
    this.setMode=function(languageMode){
        if(!self.loaded_modes[languageMode]){
            console.log("Need To Load This Mode!",languageMode)
            if (known_workers[languageMode]&&!self.loaded_workers[languageMode]){
                console.log("First Load Worker!!",languageMode)
                var worker_url = self.workers_url.formatUnicorn({languageMode:languageMode});
                return loadJS(worker_url).then(
                    function(){
                        self.loaded_workers[languageMode] = 1;
                        self.setMode(languageMode)
                    }
                );
            }
            var url = self.languages_url.formatUnicorn({languageMode:languageMode});
            return loadJS(url).then(
                function(){
                    console.log("OK LOADED:",url)
                    self.loaded_modes[languageMode] = 1
                    self.setMode(languageMode)
                }
            )
        }else{
            self.editor_instance.session.setMode("ace/mode/{languageMode}".formatUnicorn({languageMode:languageMode}))
            console.log("OK SET MODE:",languageMode)
        }
    };
    this.setTheme = function(themeName){
        if(!self.loaded_themes[themeName]){
            console.log("Load Theme:",themeName)
            var url = self.themes_url.formatUnicorn({themeName:themeName})
            return loadJS(url).then(
                function(){
                    self.loaded_themes[themeName] = 1;
                    self.setTheme(themeName);
                }
            )
        }else{
            self.editor_instance.setTheme("ace/theme/{themeName}".formatUnicorn({themeName:themeName}))
            console.log("OK SET THEME:",themeName)
        }

    };
    this.loadExtension=function(extName){
        if(!self.loaded_extensions[extName]){
            console.log("Load EXT:",extName)
            var url = self.extension_url.formatUnicorn({extName:extName})
            return loadJS(url).then(
                function(){
                    self.loaded_extensions[extName] = 1;
                    self.loadExtension(extName);
                }
            )
        }else{
            console.log("Extension Loaded!:",extName)
        }
    };
    this.value = function(new_text,cursorPosition){
        if(self.editor_instance===null){return null;}
        if(new_text===undefined){
            return self.editor_instance.getValue();
        }else{
            self.editor_instance.setValue(new_text,cursorPosition);
            return new_text;
        }
    };
    this.init=function(languageModeDefaultPython,themeDefaultMonokai){
        self.editor_instance = ace.edit(self.divId)
        self.setMode(languageModeDefaultPython?languageModeDefaultPython:"python")
        self.setTheme(themeDefaultMonokai?themeDefaultMonokai:"monokai")
    };
}