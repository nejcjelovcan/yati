<div class="row">
    <div class="small-12 columns index-view">
        <dl class="accordion" data-bind="foreach: projects">
            <dd>
                <div class="accordion-head">
                    <!--ul class="button-group radius right" data-bind="css: {hide: $parent.project().id() != id() || !canChange() || $parent.view() != 'project'}">
                      <li><a href="#" class="button tiny secondary"><span class="fa fa-upload" />Upload pofile</a></li>
                      <li><a data-bind="attr: {href: yati.router.link('project_users', id())}" class="button tiny secondary"><span class="fa fa-users"/>Manage users</a></li>
                    </ul-->
                    <a class="" data-bind="text: name(), attr: { href: yati.router.link('project', id()) }"></a>
                </div>
                <div data-bind="css: {hide: $parent.project().id() != id() || $parent.view() != 'project'}">
                    <ul class="side-nav">
                        <!-- ko foreach: targetlanguages -->
                            <li class="list-progress-item">
                                <div class="progress radius small-4 right">
                                    <span class="meter" data-bind="style { width: progress() + '%' }, text: progress() + '%'"></span>
                                </div>
                                <h5>
                                    <a data-bind="attr: {href: yati.router.link('language', $parent.id(), id()) }">
                                        <span data-bind="attr: {class: 'left f32 ' + country()}"></span>
                                        <span data-bind="text: display"></span>
                                    </a>
                                </h5>
                            </li>
                        <!-- /ko -->
                    </ul>
                </div>
                <div data-bind="css: {hide: $parent.project().id() != id() || $parent.view() != 'project_users'}">
                    <ul class="side-nav">
                        <!-- ko foreach: users -->
                            <li>
                                <!--div data-bind="template: {name: 'language-selector', data: $root}"></div-->
                                <!-- ko foreach: languages -->
                                    <span data-bind="attr: {class: 'right f32 ' + country()}"/>
                                <!-- /ko -->
                                <span data-bind="text: email()"></span>
                            </li>
                        <!-- /ko -->
                        <li>
                            <a href="#" class="button tiny secondary"><span class="fa fa-plus"> Add user</a>
                        </li>
                    </ul>
                </div>
            </dd>
        </dl>
    </div>
</div>
