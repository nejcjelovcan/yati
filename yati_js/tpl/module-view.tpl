<div class="row">
    <div class="small-12 medium-12 columns module-view">
        <div class="row">
            <!--h4 class="small-12 medium-6 columns" data-bind="text: project().name() + ': ' + module().name()"></h4-->
            <dl class="sub-nav medium-9 small-12 columns">
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
            <div class="medium-3 small-12 columns">
              <form class="row collapse search">
                <div class="columns" data-bind="css: {'small-10': module().searchQuery(), 'small-12': !module().searchQuery()}">
                  <input type="text" name="search" data-bind="value: module().searchQuery, valueUpdate: 'input'" placeholder="Search..."/>
                </div>
                <div class="small-2 columns" data-bind="css: {hide: !module().searchQuery()}">
                  <!--a href="#" class="button postfix" data-bind="click: module().onsearch">Search</a-->
                  <a href="#" class="button postfix" data-bind="click: module().onClear"><i class="fa fa-times"></i></a>
                </div>
              </form>
            </div>
        </div>
        <div class="row">
          <div class="small-12 medium-12 large-12 columns">
            <table class="units-table">
                <tbody data-bind="template: {name: 'unit-view', foreach: module().units()}">
                </tbody>
            </table>
          </div>
        </div>
        <div data-bind="css: { hide: module().unitsParams().pageCount() < 2 }, template: {name: 'pagination-view', data: module().unitsParams()}"></section>
    </div>
</div>