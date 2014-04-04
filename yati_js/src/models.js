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
        highlightTrim: function (str) {
            return (str||'').replace(/^\s+/, '&#9251;')
                .replace(/[ ]+$/, '&#9251;');
        },
        // html-ize tabs and newlines
        htmlize: function (str) {
            return str.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;').replace(/\n/g, '<br/>');
        },
        prepareString: function (str) {
            return yati.util.htmlize(yati.util.highlightTrim(str));
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
            return data;
        },
        toJSON: function () {
            var json = barebone.Model.prototype.toJSON.call(this);
            // @TODO order by index
            json.msgid = _(json.msgid).map(function (msg) { return msg.value; });
            json.msgstr = _(json.msgstr).map(function (msg) { return msg.value; });
            return json;
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