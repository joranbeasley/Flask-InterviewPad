function loadJS(url,callback){
    var script = document.createElement('script');
    script.onload = ()=>callback();
    script.src = url;
    document.head.appendChild(script);
}