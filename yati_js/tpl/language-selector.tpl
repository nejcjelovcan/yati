<select data-bind="value: language">
    <option></option>
    <!-- ko foreach: $root.languages -->
        <option data-bind="value: id, text: display"></option>
    <!-- /ko -->
</select>
<!--a href="#" class="button dropdown" data-dropdown="language-selector-dropdown"><span class="fa fa-plus" />Add language</a><br>
<ul class="f-dropdown" data-bind="foreach: languages" id="language-selector-dropdown" data-dropdown-content>
    <li><span data-bind="attr: {class: 'left f32 ' + country()}"></span><a data-bind="text: display()"></a></li>
</ul-->