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

    yati.models.Project = barebone.Model.extend(_({
        urlRoot: urlRoot+'projects/',
        defaults: {
            name: 'Project',
            modules: []
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'modules',
                relatedModel: 'yati.models.Module',
                collectionType: 'yati.models.Modules'
            }
        ]
    }).extend(UnitSet));

    yati.models.Projects = barebone.Collection.extend({
        urlRoot: urlRoot+'projects/',
        model: yati.models.Project
    });

    yati.models.Language = barebone.Model.extend({
        defaults: {
            id: null,
            display: null
        }
    });

    yati.models.Languages = barebone.Collection.extend({
        urlRoot: urlRoot+'languages/',
        model: yati.models.Language
    });

    yati.models.Module = barebone.Model.extend({
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
    });
    
    yati.models.Modules = barebone.Collection.extend({
        urlRoot: urlRoot+'modules/',
        model: yati.models.Module
    });

    yati.models.Unit = barebone.Model.extend({
        urlRoot: urlRoot+'units/',
        defaults: {
            msgid: [],
            msgstr: []
        },
        relations: [
            {
                type: Backbone.Many,
                key: 'msgid',
                relatedModel: 'yati.models.String',
                collectionType: 'yati.models.Strings'
            },
            {
                type: Backbone.Many,
                key: 'msgstr',
                relatedModel: 'yati.models.String',
                collectionType: 'yati.models.Strings'
            }
        ],
        isPlural: function () {
            return !!(this.get('msgid')||[]).length;
        },
        parse: function (data) {
            if (data && (data.msgid||data.msgstr)) {
                data.msgid = _(data.msgid).map(function (s, i) { return {value: s, id: i+1}; });
                data.msgstr = _(data.msgstr).map(function (s, i) { return {value: s, id: i+1}; });
            }
            console.log(JSON.stringify(data));
            return data;
        }
    });

    yati.models.Units = barebone.Collection.extend({
        urlRoot: urlRoot+'units/',
        model: yati.models.Unit
    });

    yati.models.String = barebone.Model.extend({
        defaults: {
            value: ''
        }
    });

    yati.models.Strings = barebone.Collection.extend({
        model: yati.models.String
    });

}(window.yati, window.Backbone, window.barebone));