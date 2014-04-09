<div class="row">
    <div class="small-12 columns index-view">
        <dl class="accordion" data-bind="foreach: projects">
            <dd>
                <a data-bind="text: name(), attr: { href: yati.router.link('project', id()) }"></a>
                <div data-bind="css: {hide: $parent.project().id() != id()}">
                    <ul class="side-nav">
                        <!-- ko foreach: targetlanguages -->
                            <li>
                                <h5><a data-bind="text: display, attr: {href: yati.router.link('language', $parent.id(), id) }"></a></h5>
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
