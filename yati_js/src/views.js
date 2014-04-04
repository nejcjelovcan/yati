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
        this.progress = ko.computed(function () { return model.getProgress(); });
        this.count = ko.computed(function () { return model.getCount(); });
        this.countDone = ko.computed(function () { return model.getCountDone(); });
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

            this.link = ko.computed(function () {
                return '#' + yati.app.get('language') + '/' + yati.app.get('project').get('id') + '/' + this.id() + '/';
            }, this);

            // @TODO this is the only thing that even remotely works
            // better pattern for related models that are not in attributes?
            // (or that are in attributes but not as relations)
            this.unitsParams = ko.computed(function () {
                this.units(); this.model();
                return new yati.views.UnitsQueryParamsView(this.model().get('units').queryParams);
            }, this);

            initUnitSet.call(this, model);
        }
    });

    yati.views.UnitView = kb.ViewModel.extend({
        constructor: function (model) {
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['id', 'msgid', 'msgstr'],
                factories: {
                    //msgid: collectionFactory(yati.views.StringView), too heavy
                    //msgstr: collectionFactory(yati.views.StringView)
                }
            });

            this.plural = ko.computed(function () { return model.isPlural(); });

            this.edit = ko.observable(false);
            this.edit.subscribe(function (val) {
                // @TODO out-of-paradigm fuglyness
                _(function () {
                    $('textarea[data-id=unit-'+this.id()+']')[val ? 'autosize' : 'trigger'](val ? undefined : 'autosize.destroy');
                }).chain().bind(this).defer();
            }, this);

            this.onclick = _(function () {
                this.edit(true);
            }).bind(this);

            this.triggeredMsgid = kb.triggeredObservable(model.get('msgid'), 'change');
            this.triggeredMsgstr = kb.triggeredObservable(model.get('msgstr'), 'change');

            this.msgid0 = ko.computed(function () {
                return this.msgid()[0].value();
            }, this);

            this.msgstr0 = ko.computed({
                read: function () {
                    this.triggeredMsgstr();
                    return this.msgstr()[0].value();
                },
                write: function (val) {
                    this.msgstr()[0].model().set('value', val);
                    this.model().save();
                },
                owner: this
            });
        }
    });

    yati.views.QueryParamsView = kb.ViewModel.extend({
        constructor: function (model, options) {
            options || (options = {});
            options.keys || (options.keys = []);
            options.keys = options.keys.concat(['page','count','pageSize']);
            kb.ViewModel.prototype.constructor.call(this, model, options);

            this.pageCount = ko.computed(function () {
                this.page(); this.count(); this.pageSize();
                if (!this.page()||!this.count()) return 0;
                return model.getPages();
            }, this);

            // returns pagination pages (current page and 3+3 neighbours)
            this.pages = ko.computed(function () {
                if (!this.page()||!this.count()) return [];
                var page = model.get('page'); // @TODO model schemas
                return _(page > 3 ? page-3 : 1).chain().range(
                        page < this.pageCount() - 3 ? page+4 : this.pageCount()+1
                    ).map(function (i) { return { page: i, link: this.pageLink(i) }; }, this)
                    .value();
            }, this);
        },
        pageLink: function (page) {
            return '#';
        }
    });

    yati.views.UnitsQueryParamsView = yati.views.QueryParamsView.extend({
        constructor: function (model) {
            yati.views.QueryParamsView.prototype.constructor.call(this, model, {keys: ['filter']});
        },
        pageLink: function (page) {
            return '#' + yati.app.get('language') + '/' + yati.app.get('project').get('id') + '/' +
                yati.app.get('module').get('id') + '/' + page + '/' + (this.filter() || 'all');
        }
    });

    /*yati.views.StringView = kb.ViewModel.extend({
        constructor: function (model) {
            kb.ViewModel.prototype.constructor.call(this, model, {
                keys: ['index', 'value']
            });
        }
    });*/


}(yati, Backbone, barebone, _, ko, kb));