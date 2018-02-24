
class SimpleACE{
    private ace:any=null;
    private current_theme:string;
    private current_mode:string;
    private loaded_themes={};
    private loaded_languages={};


    private urls = {
        languages:"https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/mode-{languageMode}.js",
        themes:"https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/theme-{themeName}.js",
        workers:"https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/worker-{languageMode}.js",
        extensions:"https://cdnjs.cloudflare.com/ajax/libs/ace/1.3.1/ext-{extName}.js"
    };
    private _loadJS(url,$callback){
        return loadJS(url,$callback);
    }
    private _loadLanguage(language:string,callback?:Function){
        if (this.loaded_languages[language]) {
                if(callback){callback();}
                return
        }
        let known_workers = {coffee:1,css:1,html:1,javascript:1,json:1,lua:1,php:1,xml:1,xquery:1}
        if(known_workers[language]){
            this._loadJS(this.urls.workers, () => {
                this._loadJS(this.urls.languages, () => {
                    this.loaded_languages[language] = 1;
                    callback();
                })
            })
        }else {
            this._loadJS(this.urls.languages, () => {
                this.loaded_languages[language] = 1;
                callback();
            })
        }
    }
    private _loadTheme(theme:string,callback?:Function){
        if(this.loaded_themes[theme]){
            callback()
        }else{
            this._loadJS(this.urls.themes,()=>{
                this.loaded_themes[theme]=1;
                callback()
            })
        }
    }
    constructor(divId:string,opts?:{}){
        this.ace = window['ace'].edit(divId,opts)
    }

    setTheme(themeName){
        this._loadTheme(themeName,function() {
            this.ace['setTheme']("ace/theme/{themeName}")
        })
    }
    setMode(languageName){
        this._loadLanguage(languageName,function(){
            this.ace['setMode'](languageName)
        })
    }
}
class MarkersList{

}
export class AceEditor{
    editor:SimpleACE;
    constructor(divId:string,opts?:{}){
        this.editor = new SimpleACE(divId,opts);
    }
    setMode(modeName:string){this.editor.setMode(modeName);}
    setTheme(themeName:string){this.editor.setTheme(themeName);}
}