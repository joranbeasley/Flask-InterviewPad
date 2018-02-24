"use strict";
var exports={}
var simple_wsio = (function () {
    function simple_wsio() {
        this.io = null;
        this.connected = false;
    }
    simple_wsio.prototype.connect = function (uri, opts) {
        console.log("CONNECT:", uri, opts);
        console.log("WINDOW[io]:", window['io']);
        this.connected = true;
    };
    simple_wsio.prototype.on = function ($eventType, $callBack) {
        this.io.on($eventType, $callBack);
    };
    ;
    simple_wsio.prototype.emit = function ($eventType, $payload) {
        this.io.emit($eventType, $payload);
    };
    return simple_wsio;
}());
var IP_WebSocketIO = (function () {
    function IP_WebSocketIO() {
        this.socket = null;
    }
    IP_WebSocketIO.prototype.on = function ($eventType, $callBack) {
        this.socket.on($eventType, $callBack);
    };
    return IP_WebSocketIO;
}());
exports.IP_WebSocketIO = IP_WebSocketIO;
