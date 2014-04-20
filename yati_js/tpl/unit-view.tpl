<tr>
    <td data-bind="html: yati.util.prepareString(msgid())" style="width: 50%;"></td>
    <td style="width: 50%;" data-bind="click: onclick, css: { edit: edit() || !msgstr() }">
        <textarea data-bind="css: { hide: !(edit() || !msgstr()) }, value: msgstr, hasFocus: edit, attr: {'data-id': 'unit-'+id()}"></textarea>
        <div data-bind="html: yati.util.prepareString(msgstr()), css: { hide: edit() || !msgstr() }"></div>
    </td>
</tr>