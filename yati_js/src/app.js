(function (window, yati, Backbone, barebone) {

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

    var staticData = window._yati_data || {};

    yati.router = new (Backbone.Router.extend({
        initialize: function () {
            this.route('', 'index');
            this.route(':project_id/', 'project');
            //this.route(':project_id/add/', 'sourceAdd');
            this.route(':project_id/users/', 'project_users');
            this.route(':project_id/users/:user/:action', 'project_users_action');
            this.route(':project_id/lang/:language/', 'language');
            this.route(':project_id/lang/:language/:module_id(/)(:filter)(/)(:page)(/)', 'module');
        },
        index: afterInit(function () {
            if (yati.app.get('projects').length == 1) {
                this.navigate(this.link('project', yati.app.get('projects').first().get('id')), {trigger: true});
                return;
            }
            yati.app.set({view: 'index'});
        }),
        _getProject: function (project_id) {
            var prj = yati.app.get('projects').get(project_id);
            if (prj) return prj;
            this.navigate('', {trigger: true});
        },
        _getProjectLanguage: function (project_id, language) {
            var prj = this._getProject(project_id),
                lang = yati.app.get('languages').get(language);
            if (prj) {
                if (!lang || !yati.app.get('user').hasLanguage(language)) {
                    this.navigate(this.link('project', project_id), {trigger: true});
                } else {
                    return [prj, lang];
                }
            }
        },
        _getProjectUser: function (project_id, user_id) {
            var prj = this._getProject(project_id),
                user = prj.get('users').get(user_id);
            if (!user) {
                this.navigate(this.link('project_users', project_id), {trigger: true})
            }
            return [prj, user];
        },
        project: afterInit(function (project_id) {
            var prj = this._getProject(project_id);
            if (prj) {
                //if (prj.get('targetlanguages'))
                // @TODO check which languages are present and which user has
                var langs = prj.getLanguagesForUser(yati.app.get('user'));
                if (langs.length == 1 && !yati.app.get('user').get('is_staff')) {
                    this.navigate(this.link('language', project_id, langs[0]), {trigger: true});
                    return;
                }
                yati.app.set({view: 'project', project: prj});
            }
        }),
        project_users: afterInit(function (project_id) {
            var prj = this._getProject(project_id);
            if (prj) {
                yati.app.set({view: 'project_users', project: prj});
            }
        }),
        project_users_action: afterInit(function (project_id, user_id, action) {
            var prjuser = this._getProjectUser(project_id, user_id);
            if (prjuser) {
                yati.app.set({view: 'project_users_' + action, project: prj, selected_user: user});
            }
        }),
        /*sourceAdd: afterInit(function (project_id) {
            var prj = this._getProject(project_id);
            if (prj) {
                yati.app.set({view: 'sourceAdd', project: prj});
            }
        }),*/
        language: afterInit(function (project_id, language) {
            var prjlang = this._getProjectLanguage(project_id, language);
            if (prjlang) {
                // check if only one module, redirect there
                if (prjlang[0].get('modules').length === 1 && !yati.app.get('user').get('is_staff')) {
                    this.navigate(this.link('module', project_id, language, prjlang[0].get('modules').first().get('id')),
                        {trigger: true, replace: true});
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
                if (!mod) {
                    this.navigate(this.link('language', project_id, language), {trigger: true});
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
                    return '/' + (args[0]||(yati.app.get('project').get('id'))) + '/';
                case 'project_users':
                    return this.link('project', args[0]) + 'users/';
                case 'project_users_action':
                    return this.link('project_users', args[0]) + args[1] + '/' + args[2] + '/';
                case 'language':
                    return this.link('project', args[0]) + 'lang/' + (args[1]||(lang && lang.get('id'))) + '/';
                case 'module':
                    return this.link('language', args[0], args[1])
                        + (args[2]||(mod && mod.get('id'))) + '/' + (args[3]||'all') + '/' + (args[4]||1) + '/';
                default:
                    return '/';
            }
        }
    }));

    yati.App = barebone.Model.extend({
        defaults: {
            //language: 'sl', // currently selected language
            //languageDisplay: 'Slovenian',
            language: {},
            languages: [],
            projects: [],
            project: {},    // currently selected project
            module: {},     // currently selected module
            view: 'index',
            unitParams: { filter: 'all' },
            user: null,
            selected_user: null,
            terms: []
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
            },
            {
                type: Backbone.Many,
                key: 'terms',
                relatedModel: 'yati.models.Term',
                collectionType: 'yati.models.Terms'
            },
            {
                type: Backbone.One,
                key: 'user',
                relatedModel: 'yati.models.User'
            },
            {
                type: Backbone.One,
                key: 'selected_user',
                relatedModel: 'yati.models.User'
            }
        ],
        initialize: function (attrs, options) {
            if (staticData.languages) {
                this.get('languages').reset(staticData.languages);
            } else {
                this.get('languages').fetch();
            }
            if (staticData.user) {
                this.set('user', staticData.user);
            } else {
                // @TODO now what?
            }
            /*if (staticData.projects) { @TODO Y U NO WORK?
                this.get('projects').reset(staticData.projects);
            } else {*/
                this.get('projects').fetch();
            //}

            this.on('change:module', this.on_module_changed);
            this.on('change:unitParams', this.on_module_changed);
            this.on('change:language', this.on_language_changed);
        },
        on_module_changed: function () {
            this.get('module').get('units').setQueryParams(_({
                module_id: this.get('module').get('id'),
                language: this.get('language').get('id')
            }).extend(this.get('unitParams')));
        },
        on_language_changed: function () {
            //this.get('project').get('modules').setQueryParams({language: this.get('language').get('id')});
            this.get('projects').setQueryParams({language: this.get('language').get('id')});
        },
        set_term_unit: function (unit) {
            this.get('terms').setQueryParams({language: this.get('language').get('id'), project_id: this.get('project').get('id'), unit_id: null}, {silent: true})
                .reset([]);
            if (unit) {
                this.get('terms').setQueryParams({unit_id: unit.get('id')});
            }
        }
    });

    yati.app = new yati.App;

}(window, yati, Backbone, barebone));