(function (yati, Backbone, barebone, _, ko, kb) {

    ko.bindingHandlers.block = {
        update: function(element, value_accessor) {
            return element.style.display = ko.utils.unwrapObservable(value_accessor()) ? 'block' : 'none';
        }
    };
    ko.bindingHandlers.inline = {
        update: function(element, value_accessor) {
            return element.style.display = ko.utils.unwrapObservable(value_accessor()) ? 'inline' : 'none';
        }
    };

    var initUnitSet = function (model) {
        this.progress = ko.computed(function () { return 90; model.getProgress(); });
        this.count = ko.computed(function () { return 90; model.getCount(); });
        this.countDone = ko.computed(function () { return 90; model.getCountDone(); });
    };
    var collectionFactory = function (view_model) { return function (col) { return kb.collectionObservable(col, {view_model: view_model})} };

    yati.views = {};

    yati.views.AppView = kb.ViewModel.extend({
        constructor: function (model) {
            model = yati.app;
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['title', 'language', 'languageDisplay', 'languages', 'view', 'project', 'module'],
                factories: {
                    project: yati.views.ProjectView,
                    projects: collectionFactory(yati.views.ProjectView),
                    module: yati.views.ModuleView
                }
            });

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

    yati.views.ProjectView = kb.ViewModel.extend({
        constructor: function (model) {
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['id', 'name', 'modules'],
                factories: {
                    modules: collectionFactory(yati.views.ModuleView)
                }
            });
            initUnitSet.call(this, model);
        }
    });

    yati.views.ModuleView = kb.ViewModel.extend({
        constructor: function (model) {
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['id', 'name', 'units'],
                factories: {
                    units: collectionFactory(yati.views.UnitView)
                }
            });

            initUnitSet.call(this, model);
        }
    });

    yati.views.UnitView = kb.ViewModel.extend({
        constructor: function (model) {
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['id', 'msgid', 'msgstr']
            });

            this.msgid0 = ko.computed(function () { return model.get('msgid').first().get('value'); });
            this.msgstr0 = ko.computed(function () { return model.get('msgstr').first().get('value'); });
        }
    });


}(yati, Backbone, barebone, _, ko, kb));