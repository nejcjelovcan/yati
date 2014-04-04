<tr>
    <td data-bind="html: yati.util.prepareString(msgid0())" style="width: 50%;"></td>
    <td style="width: 50%;" data-bind="click: onclick">
        <textarea data-bind="css: { hide: !(edit() || !msgstr0()) }, value: msgstr0, hasFocus: edit, attr: {'data-id': 'unit-'+id()}"></textarea>
        <div data-bind="html: yati.util.prepareString(msgstr0()), css: { hide: edit() || !msgstr0() }"></div>
    </td>
</tr>