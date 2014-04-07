(function (yati, Backbone, barebone) {

    var afterInit = function (func) {
        return function () {
            var args = _(arguments).toArray(), that = this;
            if (yati.app.get('projects').queryParams.get('count') === undefined) {
                yati.app.get('projects').once('sync', function () { func.apply(that, args); });
            } else {
                func.apply(that, args);
            }
        }
    };

    yati.router = new (Backbone.Router.extend({
        initialize: function () {
            this.route('', 'index');
            this.route(':project_id/', 'project');
            this.route(':project_id/:language/', 'language');
            this.route(':project_id/:language/:module_id(/)(:filter)(/)(:page)(/)', 'module');
        },
        index: function () {
            yati.app.set({view: 'index'});
        },
        _getProject: function (project_id) {
            var prj = yati.app.get('projects').get(project_id);
            if (prj) return prj;
            this.navigate('', {trigger: true});
        },
        _getProjectLanguage: function (project_id, language) {
            var prj = this._getProject(project_id),
                lang = yati.app.get('languages').get(language);
            console.log('PRJ', project_id, language, prj, lang);
            if (prj) {
                if (!lang) {
                    this.navigate(project_id+'/', {trigger: true});
                } else {
                    return [prj, lang];
                }
            }
        },
        project: afterInit(function (project_id) {
            var prj = this._getProject(project_id);
            if (prj) {
                yati.app.set({view: 'project', project: prj});
            }
        }),
        language: afterInit(function (project_id, language) {
            var prjlang = this._getProjectLanguage(project_id, language);
            if (prjlang) {
                // check if only one module, redirect there
                if (prjlang[0].get('modules').length === 1) {
                    this.navigate(project_id+'/'+language+'/'+prjlang[0].get('modules').first().get('id')+'/', {trigger: true});
                    return;
                }
                yati.app.set({view: 'language', project: prjlang[0], language: prjlang[1]});
            }
        }),
        module: afterInit(function (project_id, language, module_id, filter, page) {
            var prjlang = this._getProjectLanguage(project_id, language);
            if (prjlang) {
                var mod = prjlang[0].get('modules').get(module_id),
                    unitParams = {page: parseInt(page, 10)||1, filter: filter||'all', pageSize: 10};
                console.log({view: 'module', project: prjlang[0], language: prjlang[1],
                    module: mod, unitParams: unitParams});
                if (!mod) {
                    this.navigate(project_id+'/'+language+'/', {trigger: true});
                    return;
                }
                yati.app.set({view: 'module', project: prjlang[0], language: prjlang[1],
                    module: mod, unitParams: unitParams});
            }
        }),
        link: function (view, arg1, arg2) {
            // fugly, but hey, backbone route reversal badly needed
            var args = _(arguments).toArray(),
                view = args.shift(),
                lang = yati.app.get('language'),
                mod = yati.app.get('module');
            switch(view) {
                case 'project':
                    return '#' + (args[0]||(yati.app.get('project').get('id'))) + '/';
                case 'language':
                    return this.link('project', args[0]) + (args[1]||(lang && lang.get('id'))) + '/';
                case 'module':
                    return this.link('language', args[0], args[1])
                        + (args[2]||(mod && mod.get('id'))) + '/' + (args[3]||'all') + '/' + (args[4]||1) + '/';
                default:
                    return '#';
            }
        }
    }));

    yati.App = barebone.Model.extend({
        defaults: {
            title: 'Translation',
            //language: 'sl', // currently selected language
            //languageDisplay: 'Slovenian',
            language: {},
            languages: [],
            projects: [],
            project: {},    // currently selected project
            module: {},     // currently selected module
            view: 'index',
            unitParams: { filter: 'all' }
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'languages',
                relatedModel: 'yati.models.Language',
                collectionType: 'yati.models.Languages'
            },
            {
                type: Backbone.One,
                key: 'language',
                relatedModel: 'yati.models.Language'
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
            this.get('languages').fetch();
            this.get('projects').fetch();
            this.on('change:module', this.on_module_changed);
            this.on('change:unitParams', this.on_module_changed);
        },
        on_module_changed: function () {
            console.log('ON MODULE CHANGED', _({
                module_id: this.get('module').get('id'),
                language: this.get('language').get('id')
            }).extend(this.get('unitParams')));
            this.get('module').get('units').setQueryParams(_({
                module_id: this.get('module').get('id'),
                language: this.get('language').get('id')
            }).extend(this.get('unitParams')));
        }
    });

    yati.app = new yati.App;

}(yati, Backbone, barebone));