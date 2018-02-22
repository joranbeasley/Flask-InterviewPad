function MySocketIO(ws_url,userCredentials,options){
    var self=this;
    self.socket = io.connect(ws_url,options);
    self.editor = null;
    self.chat_panel = null;
    self.handlebar_template = Handlebars.templates.user_buttons
    this.emit=function(eventType,payload){
        console.log("emit:",eventType,payload)
        self.socket.emit(eventType,payload)
    };
    this.on=function(eventType,callback){
        self.socket.on(eventType,callback)
    };

    self.on("connect", function(data) {
        console.log("Connected!~~",data)
        self.emit("join_room",userCredentials)
    });
    self.on("error", function(data){
        console.log("GOT ERROR MSG FROM WS:",data)
    });
    self.on("sync_result",function(data){
        if(self.editor && data['room']['current_text'] != self.editor.value()){
            var old_p = self.editor.getCursorPosition();
            self.editor.value(data['room']['current_text'],old_p)
        }
        $("#users-holder").html(
          self.handlebar_template({'users':data['room']['users']})
        );
        console.log("GOT SYNC RESULT!",data)
    });
    self.on("user_joined",function(data){
        console.log("USER JOINED!:",data)
        Materialize.toast("User "+data['nickname']+" has joined the room!", 2000);

    });
    return this;
}