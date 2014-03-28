(function (yati, Backbone, barebone) {
    yati.router = new (Backbone.Router.extend({
        initialize: function () {
            this.route('', 'index');
            this.route(':language', 'index');
            this.route(':language/:module_id', 'module');
        },
        index: function (language) {
            yati.app.set({language: language||'sl', view: 'index'});
        },
        module: function (language, module_id) {
            if (!yati.app.get('modules').length) {
                yati.app.get('modules').once('sync', function () {this.module(language, module_id); }, this);
            } else {
                yati.app.set({language: language||'sl', view: 'module', module: yati.app.get('modules').get(module_id)});
            }
        }
    }));

    yati.app = new (barebone.Model.extend({
        defaults: {
            title: 'Translation',
            language: 'sl',
            languages: [],
            languageDisplay: 'Slovenian',
            module: null,
            modules: [],
            view: 'index'
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'languages',
                relatedModel: 'yati.models.Language',
                collectionType: 'yati.models.Languages'
            },
            {
                type: Backbone.Many,
                key: 'modules',
                relatedModel: 'yati.models.Module',
                collectionType: 'yati.models.Modules'
            }
        ],
        initialize: function (attrs, options) {
            _(this).bindAll('on_language_changed');
            this.on('change:language', this.on_language_changed);
            this.on('sync:languages', this.on_language_changed);
        },
        on_language_changed: function () {
            var lang = this.get('languages').get(this.get('language'));
            this.set('languageDisplay', (lang && lang.get('display')||'None'));
            this.get('modules').setQueryParams({ language: this.get('language') }).reset();
        }
    }));

}(yati, Backbone, barebone));