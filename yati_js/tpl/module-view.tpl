<div class="row">
    <div class="small-12 medium-12 columns module-view">
        <div class="row">
            <h4 class="small-12 medium-6 columns" data-bind="text: $root.project().name() + ': ' + name()"></h4>
            <dl class="sub-nav small-12 medium-6 columns">
              <dt>Filter:</dt>
              <dd data-bind="css: {active: unitsParams().filter() == 'all'}"><a data-bind="attr: { href: link() + unitsParams().page() + '/all' }">All</a></dd>
              <dd data-bind="css: {active: unitsParams().filter() == 'untranslated'}"><a data-bind="attr: { href: link() + unitsParams().page() + '/untranslated' }">Untranslated</a></dd>
            </dl>
        </div>
        <div class="row">
            <table class="units-table small-12 medium-12 large-12 columns">
                <tbody data-bind="template: {name: 'unit-view', foreach: units()}">
                </tbody>
            </table>
        </div>
        <div data-bind="css: { hide: unitsParams().pageCount() < 2 }, template: {name: 'pagination-view', data: unitsParams()}"></section>
    </div>
</div>