Handlebars.registerHelper('isEqual', function(lvalue, rvalue, options) {
        if( lvalue!=rvalue ) {
            return options.inverse(this);
        } else {
            return options.fn(this);
        }
    });