<tr>
    <td data-bind="html: yati.util.prepareString(msgid()), click: onclick" style="width: 50%;"></td>
    <td style="width: 50%;" data-bind="click: onclick, css: { edit: edit() || !msgstr() }">
        <textarea data-bind="css: { hide: !(edit() || !msgstr()) }, value: msgstr, hasFocus: edit, attr: {'data-id': 'unit-'+id()}"></textarea>
        <span class="fa fa-edit" data-bind="css: {hide: edit() || !msgstr()}"></span>
        <div data-bind="html: yati.util.prepareString(msgstr()), css: { hide: edit() || !msgstr() }"></div>
    </td>
</tr>