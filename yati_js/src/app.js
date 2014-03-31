(function (yati, Backbone, barebone) {
    yati.router = new (Backbone.Router.extend({
        initialize: function () {
            this.route('', 'index');
            this.route(':language', 'index');
            this.route(':language/:project_id', 'project');
            this.route(':language/:project_id/:module_id', 'module');
        },
        index: function (language) {
            yati.app.set({language: language||'sl', view: 'index'});
        },
        project: function (language, project_id) {
            if (!yati.app.get('projects').length) {
                yati.app.get('projects').once('sync', function () { this.project(language, project_id); }, this);
            } else {
                yati.app.set({language: language||'sl', view: 'project', project: yati.app.get('projects').get(project_id)});
            }
        },
        module: function (language, project_id, module_id) {
            if (!yati.app.get('projects').length) {
                yati.app.get('projects').once('sync', function () { this.module(language, project_id, module_id); }, this);
            } else {
                var prj = yati.app.get('projects').get(project_id);
                yati.app.set({language: language||'sl', view: 'module', project: prj, module: prj.get('modules').get(module_id)});
            }
        }
    }));

    yati.App = barebone.Model.extend({
        defaults: {
            title: 'Translation',
            language: 'sl', // currently selected language
            languages: [],
            languageDisplay: 'Slovenian',
            projects: [],
            project: {},    // currently selected project
            module: {},     // currently selected module
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
                key: 'projects',
                relatedModel: 'yati.models.Project',
                collectionType: 'yati.models.Projects'
            },
            {
                type: Backbone.One,
                key: 'project',
                relatedModel: 'yati.models.Project'
            },
            {
                type: Backbone.One,
                key: 'module',
                relatedModel: 'yati.models.Module'
            }
        ],
        initialize: function (attrs, options) {
            _(this).bindAll('on_language_changed');
            this.on('change:language', this.on_language_changed);
            this.on('sync:languages', this.on_language_changed);
            this.on('change:module', this.on_module_changed);
        },
        on_language_changed: function () {
            var lang = this.get('languages').get(this.get('language'));
            this.set('languageDisplay', (lang && lang.get('display')||'None'));
            this.get('projects').setQueryParams({ language: this.get('language') }).reset();
            this.get('module').get('units').setQueryParams({ language: this.get('language') }, {silent: true}).reset();
        },
        on_module_changed: function () {
            this.get('module').get('units').setQueryParams({ module_id: this.get('module').get('id'), language: this.get('language') }, {silent: !this.get('module').get('id')});
        }
    });

    yati.app = new yati.App;

}(yati, Backbone, barebone));