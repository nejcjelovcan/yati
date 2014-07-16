(function (yati, Backbone, barebone) {

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

}(window.yati, window.Backbone));