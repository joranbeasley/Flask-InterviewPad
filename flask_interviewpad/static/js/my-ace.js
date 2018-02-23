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



// call marker.session.removeMarker(marker.id) to remove it
// call marker.redraw after changing one of cursors
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
    self.markers = new Markers();
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
    this.on_change=function($ev){
        console.log("Change:",$ev)
        // x = self.editor_instance.undo()
    };
    this.applyChange= function(changeOb,cursorId){
        // marker.cursors[cursorId]['row']=0;
        console.log("APPLY:",changeOb)
        // marker.cursors[cursorId]['column']=0;
        self.editor_instance.session.doc.applyDelta(changeOb)
    };
    this.on=function(evt,callback){
        console.log("REGISTER ON:",evt,callback)
        self.editor_instance.on(evt,callback)
    };
    this.getattr=function($attr){

        return self.editor_instance[$attr];
    };
    this.setattr=function($attr,$value){
        self.editor_instance[$attr] = $value;
    };
    this.session=function(){
        return self.editor_instance.session;
    };
    this.on_changeSelection=function(callback){
        console.log("Bind to select change!")
        return self.editor_instance.selection.on('changeSelection',callback)
    };
    this.on_user_change=function(callback){
        self.editor_instance.on("change",function($ev){
            if (self.editor_instance.curOp && self.editor_instance.curOp.command.name){
                callback($ev);
            }
            else{
                console.log("change_programatically, no event")
            }
            return true;
        });
    };
    this.clearMarkers=function(){
        self.markers.markers = [];
        self.markers.redraw();
    };

    this.appendMarker=function(markerDetails){
        return self.markers.appendMarker(markerDetails)
    };
    this.updateMarker=function(marker_index,markerDetails){
        if(marker_index == self.markers.markers.length){
            return self.appendMarker(markerDetails)
        }
        return self.markers.updateMarker(marker_index,markerDetails);
    };
    this.deleteMarker=function(marker_index){
        return self.markers.deleteMarker(marker_index);
    };
    this.init=function(languageModeDefaultPython,themeDefaultMonokai){
        self.editor_instance = ace.edit(self.divId)
        self.on_user_change(self.on_change);
        self.setMode(languageModeDefaultPython?languageModeDefaultPython:"python")
        self.setTheme(themeDefaultMonokai?themeDefaultMonokai:"monokai")
        self.markers.session = self.editor_instance.session;
        self.markers.session.addDynamicMarker(self.markers, true)
    };
}



function Marker(color,row,column,is_hidden,selection_size){
    var self=this;
    self.extra = {};

    self.row = (row!==undefined)?row:-1;
    self.column = (column!==undefined)?column:-1;
    self.color = color;
    self.hidden = (is_hidden!==undefined)?is_hidden:false;
    self.selection_size = (selection_size!==undefined)?selection_size:0;
    self.__bounds = {};
    self.range=null;
    self.index=-1;

    self.__get_cursor_bounds=function(row,column,session,config,marker_layer){
        console.log("GET BOUNDS MARKET LAYER:",marker_layer,row,column)
        var screenPos = session.documentToScreenPosition({row:row,column:column});
        var data = {
            height: config.lineHeight,
            width: config.characterWidth,
        };
        data['top']=marker_layer.$getTop(screenPos.row, config);
        data['left']=marker_layer.$padding + screenPos.column * data.width;
        console.log("MY BOUNDDS:",data)
        return data;
    };
    self.__get_select_bounds = function(range,session,config,markerLayer){
        var get_row_bounds=function(row,start_column,end_column){
            if(!start_column){start_column=0;}
            var end_column = end_column?end_column:session.getLine(row).length;
            var startPos = session.documentToScreenPosition({row:row,column:start_column});
            var endPos = session.documentToScreenPosition({row:row,column:end_column});
            var data = {
                height: config.lineHeight,
                char_width: config.characterWidth,
                width: (endPos.column - startPos.column)*config.characterWidth
            };
            data['top'] = markerLayer.$getTop(startPos.row, config);
            data['left'] = markerLayer.$padding + startPos.column * data.char_width;
            console.log("ROW:",row,"::",start_column,"-",end_column,"::",data.width)
            console.log("DATA:")
            return data;
        };

        var start = config.firstRow, end = config.lastRow;
        if (range.start.row < start){
            range.start = {row:start,column:0}
        }
        if (range.end.row > end){
            range.end = {row:end,column:session.getLine(end).length}
        }
        start_row = range.start.row;
        start_col = range.start.column;
        end_col=undefined;
        if(range.start.row==range.end.row){
            end_col=range.end.column
        }

        var row_bounds = {}
        console.log("GET FIRST ROW:",start_row,start_col-end_col)
        row_bounds[range.start.row] = get_row_bounds(start_row,start_col,end_col)
        if(range.end.row > range.start.row) {
            for (var row = range.start.row+1; row < range.end.row ; row++) {
                row_bounds[row] = get_row_bounds(row)
            }
            row_bounds[range.end.row] = get_row_bounds(range.end.row,0,range.end.column)
        }
        return row_bounds
    };
    self.update=function(session,config,markerLayer){
        if(self.range){
            console.log("GET MY RANGE!!")
            self.__bounds = self.__get_select_bounds(self.range,session,config,markerLayer);
        }else {
            console.log("JUST A CURSOR??")
            self.__bounds = self.__get_cursor_bounds(self.row, self.column, session, config, markerLayer)
        }
    };
    self.get_range_html=function(){
        var render_line=function(lineDetails){
            return ("<div class='MyHighlightClass' style='position:absolute;"+
                "height:"+ lineDetails.height+ "px;"+
                "border-bottom:"+(self.color||"blue")+" solid thin;"+
                "top:"+ lineDetails.top+ "px;"+
                "left:"+ lineDetails.left+ "px; width:"+ lineDetails.width+ "px'></div>");
        };
        console.log("RANGE HTML:",self.__bounds)
        var my_html = "";
        for(i=self.range.start.row;i<self.range.end.row+1;i++){
            if(self.__bounds[i]){
                my_html += render_line(self.__bounds[i])
            }
        }
        console.log("FINAL RANGE HTML:?",my_html)
        return my_html;
    };
    self.get_html=function(){
        if(self.range){
            console.log("GET RANGE HTML!")
            return self.get_range_html()
        }
        selection_size = (self.selection_size>0)?self.selection_size:0.3;
        console.log(self.__bounds)
        return ("<div class='MyCursorClass' style='position:absolute;"+
                "height:"+ self.__bounds.height+ "px;"+
                "background:"+(self.color||"blue")+";"+
                "top:"+ self.__bounds.top+ "px;"+
                "left:"+ self.__bounds.left+ "px; width:"+ self.__bounds.width*selection_size+ "px'></div>");
    }
}
function Markers(editor){
    var self=this;
    self.markers = [];
    self.editor = editor;
    self.marker_layer = null;
    self.config = null;
    self.session = null;


    self._reindex_markers=function(){
        for(var i=0;i<self.markers.length;i++){
            self.markers[i].index = i;
        }
    };
    self._render_range=function(cursor){
        if(cursor.hidden ){return '';}
        return cursor.get_html();
    };
    self._render_cursor=function(cursor){
        if(cursor.range){
            return self._render_range(cursor)
        }
        if(cursor.hidden || cursor.row ==undefined || cursor.column ==undefined){
            console.log("SKIP UNDEFINED??")
            return '';}
        var start = self.config.firstRow, end = self.config.lastRow;
        if(start > cursor.row || end < cursor.row){
            console.log("SKIP ROW!!!",start,'>',cursor.row,">",end,"????")
            return '';}
        return cursor.get_html()
    };
    self._render=function(session,config,markerLayer){
        var my_html = "";
        for(var i=0;i<self.markers.length;i++){
            self.markers[i].update(session, config, markerLayer)
            var elem = self._render_cursor(self.markers[i]);
            // if(elem != "") {
            //     console.log("UPD:",i,elem);
            //     self.markers[i].update(session, config, markerLayer)
            // }
            my_html += elem
        }
        return my_html;
    };
    self.update=function(html, markerLayer, session, config){
        console.log("updaet update update!???")
        self.marker_layer=markerLayer;
        self.config =config;
        var my_html = self._render(session,config,markerLayer);
        html.push(my_html)
    };
    self.redraw=function(){
        console.log("REDRAW???")
        self.session._signal("changeFrontMarker");
    };


    self.updateMarker=function(marker_id,markerDetails){
        console.log("UPDATE MARKER:",markerDetails,markerDetails.row,markerDetails.range)
        var marker = self.markers[marker_id];
        var changed=0;

        if(markerDetails.range){

            var startPos=markerDetails.range.start;
            var endPos=markerDetails.range.end;
            if((startPos.row < endPos.row) || (startPos.column<endPos.column)) {
                marker.range = markerDetails.range;
                changed = 1;
                console.log("set range!")
            }else{
                console.log("no range only point?",startPos,endPos)
                marker.range = null;
                marker.row = startPos.row;
                marker.column = startPos.column;
                changed=1;
            }
        }
        if(markerDetails.row!=undefined&&markerDetails.row!=marker.row){marker.row = markerDetails.row;changed=1;}
        if(markerDetails.column!=undefined&&markerDetails.column!=marker.column){marker.column = markerDetails.column;changed=1;}
        if(markerDetails.selection_size&&markerDetails.selection_size!=marker.selection_size) {marker.selection_size = markerDetails.selection_size;changed=1;}
        if(markerDetails.color&&markerDetails.color!=marker.color){marker.color = markerDetails.color;changed=1}
        if(markerDetails.hidden!==undefined&&markerDetails.hidden!=marker.hidden){marker.hidden = markerDetails.hidden;changed=1}
        if(changed===1){self.redraw();}
        console.log("MARK2:",marker)
        return marker;
    };
    self.appendMarker=function(markerDetails){
        if(markerDetails.is_hidden === undefined){markerDetails.is_hidden=false;}
        var marker = new Marker(markerDetails.color,markerDetails.row,markerDetails.column,markerDetails.is_hidden,markerDetails.selection_size)
        marker.index = self.markers.length;
        self.markers.push(marker)
        return marker;
    };
    self.deleteMarker=function(marker_index){
        var marker = self.markers[marker_index];
        delete self.markers[marker_index];
        return marker;
    };
    return this;
}


