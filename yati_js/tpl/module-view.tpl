<div class="row">
    <div class="small-12 medium-12 columns module-view">
        <div class="row">
            <h4 class="small-12 medium-6 columns" data-bind="text: project().name() + ': ' + module().name()"></h4>
            <dl class="sub-nav small-12 medium-6 columns">
              <dt>Filter:</dt>
              <dd data-bind="css: {active: module().unitsParams().filter() == 'all' || !module().unitsParams().filter()}">
                <a data-bind="attr: { href: yati.router.link('module', project().id(), language().id(), module().id(), 'all', 1) }">All</a>
              </dd>
              <dd data-bind="css: {active: module().unitsParams().filter() == 'untranslated'}">
                <a data-bind="attr: { href: yati.router.link('module', project().id(), language().id(), module().id(), 'untranslated', 1) }">Untranslated</a>
              </dd>
              <dd data-bind="css: {active: module().unitsParams().filter() == 'translated'}">
                <a data-bind="attr: {href: yati.router.link('module', project().id(), language().id(), module().id(), 'translated', 1) }">Translated</a>
              </dd>
            </dl>
        </div>
        <div class="row">
            <table class="units-table small-12 medium-12 large-12 columns">
                <tbody data-bind="template: {name: 'unit-view', foreach: module().units()}">
                </tbody>
            </table>
        </div>
        <div data-bind="css: { hide: module().unitsParams().pageCount() < 2 }, template: {name: 'pagination-view', data: module().unitsParams()}"></section>
    </div>
</div>