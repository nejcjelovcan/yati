(function (yati, Backbone, barebone) {

    yati.models = {};

    yati.models.Project = barebone.Model.extend({
        urlRoot: '/site/api/translation/projects/',
        defaults: {
            name: 'Project',
            modules: []
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'pofiles',
                relatedModel: 'yati.models.Pofile',
                collectionType: 'yati.models.Pofiles'
            }
        ]
    });


    yati.models.Language = barebone.Model.extend({
        defaults: {
            id: null,
            display: null
        }
    });

    yati.models.Languages = barebone.Collection.extend({
        urlRoot: '/site/api/translation/languages/',
        model: yati.models.Language
    });

    yati.models.Module = barebone.Model.extend({
        urlRoot: '/site/api/translation/modules/',
        defaults: {
            language: 'en',
            messages: []
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'messages',
                relatedModel: 'yati.models.Message',
                collectionType: 'yati.models.Messages'
            }
        ],
        initialize: function () {
            _(this).bindAll('getProgress');
            this.get('messages').setQueryParams({module_id: this.get('id'), language: this.get('language')}, {silent: true});
            this.on('change:language', function () { this.get('messages').setQueryParams({language: this.get('language')}, {silent: true}); }, this);
        },
        getProgress: function () {
            if (!this.get('messages_count')) return 0;
            return ((this.get('messages_count')-this.get('messages_missing_count'))/this.get('messages_count'))*100;
        }
    });
    
    yati.models.Modules = barebone.Collection.extend({
        urlRoot: '/site/api/translation/modules/',
        model: yati.models.Module,
        initialize: function (items, options) {
            options || (options = {});
            if (options.language) this.language = options.language;
            if (this.language) {
                this.on('add', function (model) {
                    model.set('language', this.language);
                }, this);
                this.setQueryParams({language: this.language}, {silent: true});
            }
        }
    });

    yati.models.Pofile = barebone.Model.extend({
        urlRoot: '/site/api/translation/pofiles/',
        defaults: {
            language: 'en',
            messages: []
        },
        /*relations: [
            {
                type: Backbone.Many,
                key: 'messages',
                relatedModel: 'yati.models.Message',
                collectionType: 'yati.models.Messages'
            }
        ],*/
    });

    yati.models.Pofiles = barebone.Collection.extend({
        model: yati.models.Pofile,
        getProject: function () {
            return this.parents[0];
        }
    });

    yati.models.Message = barebone.Model.extend({
        urlRoot: '/site/api/translation/messages/',
        defaults: {

        },
        relations: [
            {
                type: Backbone.Many,
                key: 'strings',
                relatedModel: 'yati.models.MessageString',
                collectionType: 'yati.models.MessageStrings'
            }
        ],
        isPlural: function () {
            return !!this.get('sid_plural');
        }
    });

    yati.models.Messages = barebone.Collection.extend({
        urlRoot: '/site/api/translation/messages/',
        model: yati.models.Message,
        /*fetch: function () {
            if (this.parent)
        },*/
    });

    yati.models.MessageString = barebone.Model.extend({
        defaults: {
            number: 0,
            string: ''
        }
    });

    yati.models.MessageStrings = barebone.Collection.extend({
        model: yati.models.MessageString
    });

}(window.yati, window.Backbone, window.barebone));