(function (yati, Backbone, barebone, _, ko, kb) {

    ko.bindingHandlers.block = {
        update: function(element, value_accessor) {
            return element.style.display = ko.utils.unwrapObservable(value_accessor()) ? 'block' : 'none';
        }
    };

    yati.views = {};

    yati.views.AppView = kb.ViewModel.extend({
        constructor: function (model) {
            model = yati.app;
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['title', 'language', 'languageDisplay', 'languages', 'view', 'module'],
                factories: { module: yati.views.ModuleView }
            });

            this.modules = kb.collectionObservable(model.get('modules'), {
                view_model: yati.views.ModuleView
            }).extend({notify: 'always'});

            yati.appView = this;
            yati.app.get('languages').fetch();

            Backbone.history.start();
            $(document).foundation();
        }
    });

    yati.views.LanguageView = kb.ViewModel.extend({
        constructor: function (model) {
            kb.ViewModel.prototype.constructor.call(this, model,
                ['id', 'display']);
            this.model = model;
        }
    });

    yati.views.ModuleView = kb.ViewModel.extend({
        constructor: function (model) {
            console.log('MODULE VIEW', model);
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['id', 'name', 'description', 'messages_count', 'messages_missing_count']
            });
            this.progress = ko.computed(function () { return model && Math.round(model.getProgress()*100)/100 + '%'; });
        }
    });


}(yati, Backbone, barebone, _, ko, kb));