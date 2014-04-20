<div class="row">
    <div class="small-12 columns index-view">
        <dl class="accordion" data-bind="foreach: projects">
            <dd>
                <div class="accordion-head">
                    <ul class="button-group radius right" data-bind="css: {hide: $parent.project().id() != id()}">
                      <li><a href="#" class="button tiny secondary">Upload pofile</a></li>
                      <li><a href="#" class="button tiny secondary">Manage users</a></li>
                    </ul>
                    <a class="" data-bind="text: name(), attr: { href: yati.router.link('project', id()) }"></a>
                </div>
                <div data-bind="css: {hide: $parent.project().id() != id()}">
                    <ul class="side-nav">
                        <!-- ko foreach: targetlanguages -->
                            <li class="list-progress-item">
                                <div class="progress radius small-4 right">
                                    <span class="meter" data-bind=""></span>
                                </div>
                                <h5>
                                    <a data-bind="attr: {href: yati.router.link('language', $parent.id(), id) }">
                                        <span data-bind="attr: {class: 'left f32 ' + country}"></span>
                                        <span data-bind="text: display"></span>
                                    </a>
                                </h5>
                            </li>
                        <!-- /ko -->
                        <!--li>
                            <h5><a data-bind="attr: {href: yati.router.link('language', id(), 'add')}">+ Add source</a></h5>
                        </li-->
                    </ul>
                </div>
            </dd>
        </dl>
    </div>
</div>
