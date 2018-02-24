
function UsersList(){
    var self=this;
    self.usersList = [];
    self.length = 0;
    self.handlebars_templ = Handlebars.templates.user_buttons;
    self._reindex_users=function(){
        self.length = self.usersList.length;
        for(var i=0;i<self.length;i++){
            self.usersList[i]['index'] = i;
        }
    };
    self.updateUser=function(index,userData){
        var user = self.usersList[index];
        console.log("USER:",index,user)
        for(var key in userData){
            user[key] = userData[key]
        }
        self.usersList[index] = user;
        self.render_users()
    };
    self.setUsers = function(userList){
        self.usersList = userList;
        self.redraw()
    };
    self.addUser=function(userData){
        userData['index'] = self.usersList.length;
        self.usersList.push(userData);
        self.render_users();
    };
    self.getUserIndexBy = function($attribute,value){
        for(var i=0;i<self.usersList.length;i++){
            if(self.usersList[i][$attribute]==value){
                return i;
            }
        }
        return -1;
    };
    self.getUserBy=function($attribute,value){
        var idx = self.getUserIndexBy($attribute,value);
        if(idx<0)return null;
        return self.usersList[idx];
    };
    self.removeUserBy = function($attribute,value){
        var index = self.getUserIndexBy($attribute,value);
        if(index<0)return None;
        return self.removeUser(index);
    };
    self.removeUser=function(index){
       var user2remove = self.usersList[index];
       delete self.usersList[index];
       self.redraw();
       return user2remove;
    };
    self.redraw=function(){
        self._reindex_users();
        self.render_users();
    };
    self.render_users=function(){
        var tmp_userlist = [];
        for(var i in self.usersList){
            var user = self.usersList[i]
            console.log("I:U:",i,user)
            tmp_userlist.push({'nickname':user.nickname,'state':user.state,'user_color':user.user_color})
        }
        // console.log("RENDER USERS:",self.usersList)
        $("#users-holder").html(
              self.handlebars_templ({'users':tmp_userlist})
        );
    }
}
function MySocketIO(ws_url,userCredentials,options){
    var self=this;
    self.socket = io.connect(ws_url,options);
    self.editor = null;
    self.user_id = null;
    self.room_id = null;
    self.user = null;
    self.state="active"
    self.chat_panel = null;
    self.users = new UsersList();
    self.templ = {
        user_btn:Handlebars.templates.user_buttons
    };
    self.selection_timer = null;
    self.blur_timer = null;
    this.notify_blur = function(){
        if(self.blur_timer){
            clearTimeout(self.blur_timer)
        }
        self.blur_timer = setTimeout(function(){
            self.state="inactive";
            self.emit('push_blur',{'user_id':self.user_id,'room_id':self.room_id});
            self.blur_timer = null;
        },1000)
    };
    this.cancel_blur = function(){
        if(self.blur_timer){
            clearInterval(self.blur_timer)
            self.blur_timer = null;
        }else if(self.state === "inactive"){
            self.emit('push_unblur',{'user_id':self.user_id,'room_id':self.room_id})
        }
    };
    this.notify_selection=function(){
        console.log("NOTIFY!")
        var selection = self.editor.editor_instance.getSelectionRange()
        self.socket.emit("push_select",{selection:selection,user_id:self.user_id,room_id:self.room_id})
    };
    this.on_my_editor_select_change=function($ev){
        if(self.selection_timer){
            clearTimeout(self.selection_timer)
        }
        self.selection_timer = setTimeout(self.notify_selection,1200)

    };
    this.init_editor=function(editor_instance){
        self.editor = editor_instance;
        self.editor.on_user_change(self.on_my_editor_change);
        self.editor.on_changeSelection(self.on_my_editor_select_change);
        self.editor.on('blur',function(){
            self.selection_timer = setTimeout(function(){
                self.emit('push_select',{selection:null,user_id:self.user_id,room_id:self.room_id})
            },750)

        })
        self.editor.on('focus',function(){
            if(self.selection_timer){
                clearTimeout(self.selection_timer)
            }
            self.selection_timer = setTimeout(self.notify_selection,1200)
        })
    };

    this.emit=function(eventType,payload){
        console.log("emit:",eventType,payload)
        self.socket.emit(eventType,payload)
    };
    this.on=function(eventType,callback){
        self.socket.on(eventType,callback)
    };
    this.on_my_editor_change=function($ev){
        self.emit("push_change",{change:$ev,user_id:self.user_id,room_id:self.room_id})
    };
    this.apply_remote_select = function(details){
        console.log("APPLY:",details);
        var my_user = self.users.getUserBy('id',details['user_id']);

        var marker_details = {range:details['selection'],color:details['user_color'],
                                hidden:false};
        if(!details.selection || details['hidden']){
            marker_details.hidden = true;
            console.log("Hide Marker!")
        }else if(details.hidden===false){
            marker_details.hidden = false;
        }

        var marker = self.editor.updateMarker(my_user.marker.index,marker_details)
        console.log("New Updated Marker",marker)
    };
    this.send_chat_msg=function(msg){
        self.emit("push_chat_message",{'message':msg,'user_id':self.user_id,'room_id':self.room_id})
    };
    this.apply_remote_change= function(details){
        if(details.user_id == self.user_id){
            console.log("Skip my own edit...")
        }else {
            var my_user = self.users.getUserBy('id',details['user_id']);
            console.log("GOT CHANGE FROM USER:",my_user);
            var delta = details['change']
            self.editor.applyChange(delta)
            if(delta['action']=="insert"){
                var row=delta['end']['row'],column=delta['end']['column']+1;
                marker = self.editor.updateMarker(my_user.marker.index,{range:undefined,row:row,column:column,color:details['user_color'],is_hidden:false})
                self.editor.markers.redraw()
                console.log("Updated Marker:",marker)
                // self.editor.setTmpCursor({delta.end.row})
            }else if(delta['action']=="remove"){
                var row=delta['start']['row'],column=delta['start']['column']+1;
                console.log("C:",row,column)
                marker = self.editor.updateMarker(my_user.marker.index,{range:undefined,row:row,column:column,color:details['user_color'],is_hidden:false})
                self.editor.markers.redraw()
                console.log("Updated Marker:",marker)
            }else{
                console.log('!!!',"Unknown EDIT:",delta,'!!!')
            }

            console.log("Got Remote Change Event:", details)
        }
        // self.editor.applyChange(delta)
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
            // var old_p = self.editor.getCursorPosition();
            self.editor.value(data['room']['current_text'],-1)
        }
        self.users.setUsers(data['room']['users']);
        for(var i=0;i<self.users.usersList.length;i++){
            var user = self.users.usersList[i];
            // if (user.id == self.user_id){ // this works... just not sure i need it
            //     self.user = user;
            // }
            var markerDetails = {color:user.user_color}
            var marker = self.editor.updateMarker(i,markerDetails);
            marker.extra['user'] = user;
            user['marker'] = marker;
        }

        console.log("GOT SYNC RESULT!",data)
    });
    self.on("user_joined",function(data){
        console.log("USER JOINED!:",data)
        Materialize.toast("User "+data['nickname']+" has joined the room!", 2000);
        var index = self.users.getUserIndexBy('id',data['id'])
        self.users.updateUser(index,data)
    });
    self.on("user_left",function(data){
        console.log("Goodbye:",data)
        Materialize.toast("User "+data['nickname']+" has LEFT the room!", 2000);
        var user=self.users.getUserBy('id',data['id'])

        if(!user){
            console.log("hmm no user here?",self.users.usersList)
            return;
        }
        user.state="disconnected"
        self.users.render_users()
    });
    self.on('notify_editor_change',self.apply_remote_change);
    self.on('notify_editor_select',self.apply_remote_select);

    // self.on('changed_editor',self.apply_remote_change);
    return this;
}