(function (yati, Backbone, barebone) {

    yati.models = {};
    var urlRoot = yati.models.urlRoot = '/yati/',
        UnitSet = {
            getProgress: function () {
                if (!this.get('units_count') || this.get('units_count').length < 2 || this.get('units_count')[0] < 1) return 0;
                return Math.round((this.get('units_count')[1]/this.get('units_count')[0])*100);
            },
            getCount: function () {
                if (!this.get('units_count') || this.get('units_count').length < 1) return 0;
                return this.get('units_count')[0];
            },
            getCountDone: function () {
                if (!this.get('units_count') || this.get('units_count').length < 2) return 0;
                return this.get('units_count')[1];
            }
        };

    // @TODO move to util.js
    yati.util = {
        // this replaces many spaces at beginning/end with only one visible placeholder
        // @TODO put in as many placeholders as spaces
        // @TODO render trailing newline as &#9166;
        _entityMap: {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': '&quot;',
            "'": '&#39;',
            "/": '&#x2F;'
        },
        escapeHtml: function (str) {
            return String(str).replace(/[&<>"'\/]/g, function (s) {
                return yati.util._entityMap[s];
            });
        },
        highlightTrim: function (str) {
            return (str||'').replace(/^[ ]+/, '&#9251;')
                .replace(/[ ]+$/, '&#9251;');
        },
        // html-ize tabs and newlines
        htmlize: function (str) {
            return str.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;').replace(/\n/g, '<br/>');
        },
        prepareString: function (str) {
            return yati.util.htmlize(yati.util.highlightTrim(yati.util.escapeHtml(str)));
        }
    };

    yati.models.User = barebone.Model.extend({
        defaults: { permissions: [] },
        has_perm: function (perm) {
            return this.get('permissions').indexOf(perm) > -1;
        }
    });

    yati.models.Project = barebone.Model.extend(_({
        urlRoot: urlRoot+'projects/',
        defaults: {
            name: 'Project',
            modules: [],
            targetlanguages: [],
            users: []
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'modules',
                relatedModel: 'yati.models.Module',
                collectionType: 'yati.models.Modules'
            },
            {
                type: Backbone.Many,
                key: 'targetlanguages',
                relatedModel: 'yati.models.Language',
                collectionType: 'yati.models.Languages'
            },
            {
                type: Backbone.Many,
                key: 'users',
                relatedModel: 'yati.models.User',
                collectionType: 'yati.models.Users'
            }
        ],
        getLanguagesForUser: function (user) {
            return this.get('targetlanguages').chain().map(function (l) { return l.get('id'); }).filter(user.hasLanguage).value();
        }
    }).extend(UnitSet));

    yati.models.Projects = barebone.Collection.extend({
        urlRoot: urlRoot+'projects/',
        model: yati.models.Project
    });

    yati.models.Language = barebone.Model.extend(_({
        defaults: {
            id: null,
            display: null,
            country: null
        }
    }).extend(UnitSet));

    yati.models.Languages = barebone.Collection.extend({
        urlRoot: urlRoot+'languages/',
        model: yati.models.Language
    });

    yati.models.Module = barebone.Model.extend(_({
        urlRoot: urlRoot+'modules/',
        // @TODO fsck this shizzle - check nested Many collections because they're fishy
        defaults: {
            units: []
        }, 
        relations: [
            {
                type: Backbone.Many,
                key: 'units',
                relatedModel: 'yati.models.Unit',
                collectionType: 'yati.models.Units'
            }
        ]
    }).extend(UnitSet));
    
    yati.models.Modules = barebone.Collection.extend({
        urlRoot: urlRoot+'modules/',
        model: yati.models.Module
    });

    var changeUpdater = function (model, eventName) {
        var cb = function () {
            model.off(eventName, cb);
            model.save(null, {
                success: function (){
                    model.on(eventName, cb);
                }
            });
        };
        model.on(eventName, cb);
    };

    yati.models.Unit = barebone.Model.extend({
        urlRoot: urlRoot+'units/',
        defaults: {
        },
        initialize: function () {
            // @TODO this is fucked up
            // maybe forget the listener until save is done?
            var update = function () {

            };
            changeUpdater(this, 'change:msgstr');
        },
        isPlural: function () {
            return !!(this.get('msgid_plural')||[]).length;
        },
        toJSON: function () {
            var json = barebone.Model.prototype.toJSON.call(this);
            return {msgstr: [json.msgstr].concat(json.msgstr_plural || [])};
        }
    });

    yati.models.Units = barebone.Collection.extend({
        urlRoot: urlRoot+'units/',
        model: yati.models.Unit
    });

    yati.models.Term = barebone.Model.extend({
        defaults: {
            msgid: '',
            msgstr: ''
        },
        parse: function (data) {
            data.msgstr = data.msgstr.join(', ');
            return data;
        }
    });

    yati.models.Terms = barebone.Collection.extend({
        urlRoot: urlRoot+'terms/',
        model: yati.models.Term
    });

    yati.models.User = barebone.Model.extend({
        defaults: {
            is_staff: false,
            languages: [],
            permissions: [],
            email: null
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'languages',
                relatedModel: 'yati.models.Language',
                collectionType: 'yati.models.Languages'
            }
        ],
        initialize: function () {
            _(this).bindAll('hasLanguage', 'can');
        },
        can: function (perm) {
            return self.get('permissions').indexOf(perm) > -1;
        },
        hasLanguage: function (lang) {
            return this.get('is_staff') ||
                !this.get('languages').length ||
                !!this.get('languages').get(lang);
        }
    });

}(window.yati, window.Backbone, window.barebone));